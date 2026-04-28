"""Thin wrapper over the `ollama` Python client for Tier 4 (LLM-based) rules.

Exposes `classify()` for structured-output classification calls. Other call
shapes (free-form chat, embeddings) can be added when a second caller needs
them; v0 is LS-CAP-02 only.

Errors are swallowed and surfaced via a typed `ClassifyResult` per PLAN.md's
"graceful degradation" principle: if Ollama isn't running, the model isn't
loaded, or the structured output fails to parse, the caller gets a result
they can record (or skip) rather than a crash that aborts the eval.

Two robustness layers earned during the LS-CAP-02 benchmark shake-out:
  * `think=False` is passed unconditionally. Both Qwen 3.x and Gemma 4 emit
    hidden reasoning into `message.thinking` when thinking mode is on; the
    caller never sees `message.content` and the eval times out. `think=False`
    is a no-op for models that don't support thinking, so it's safe to set
    for every call.
  * Some models (notably Gemma 4) wrap structured output in ```json ... ```
    fences despite the `format=` JSON-Schema constraint. We strip those
    before json.loads.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass

import ollama


_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*\n?(.*?)\n?```\s*$", re.DOTALL | re.IGNORECASE)


def _strip_markdown_fence(s: str) -> str:
    m = _FENCE_RE.match(s)
    return m.group(1) if m else s


@dataclass
class ClassifyResult:
    ok: bool
    payload: dict | None
    error: str | None
    latency_ms: float
    raw_content: str | None = None  # the model's literal JSON string, kept for debugging


def classify(
    model: str,
    system: str,
    user: str,
    schema: dict,
    *,
    timeout_s: float = 180.0,
    temperature: float = 0.0,
    keep_alive: int | str | None = None,
) -> ClassifyResult:
    """Send a single classification turn to Ollama with structured output.

    `schema` is a JSON Schema dict; ollama's `format=` accepts it directly and
    constrains the model's output to a parseable JSON instance of that schema.
    `temperature=0.0` is the default for eval reproducibility.

    `keep_alive` is forwarded to Ollama when set. Pass `0` on the last call of
    a multi-model sweep to force the server to unload the model (frees VRAM/RAM
    before the next model loads — avoids the 30 GB-RAM OOM we hit chaining
    26b → 27b). `None` uses Ollama's default (5 minutes).
    """
    started = time.perf_counter()
    raw_content: str | None = None
    try:
        client = ollama.Client(timeout=timeout_s)
        chat_kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "format": schema,
            "think": False,
            "options": {"temperature": temperature},
        }
        if keep_alive is not None:
            chat_kwargs["keep_alive"] = keep_alive
        response = client.chat(**chat_kwargs)
        raw_content = response.message.content
        payload = json.loads(_strip_markdown_fence(raw_content))
        return ClassifyResult(
            ok=True,
            payload=payload,
            error=None,
            latency_ms=(time.perf_counter() - started) * 1000,
            raw_content=raw_content,
        )
    except json.JSONDecodeError as e:
        return ClassifyResult(
            ok=False,
            payload=None,
            error=f"JSONDecodeError: {e}",
            latency_ms=(time.perf_counter() - started) * 1000,
            raw_content=raw_content,
        )
    except Exception as e:
        return ClassifyResult(
            ok=False,
            payload=None,
            error=f"{type(e).__name__}: {e}",
            latency_ms=(time.perf_counter() - started) * 1000,
            raw_content=raw_content,
        )
