"""EXP-08: run v1b-xml against the labeled fixture corpus, binary-subset only.

The v0-sentences research culminated in qwen3.5:9b + v1b-xml at 100% on
the 19/20 it answers, and gemma4:26b at 100% — but on a controlled
20-sentence corpus that we deliberately designed to be gold-labelable
from a single sentence's content. This script is the test that decides
whether that saturation transfers to the messy real-fixture corpus.

Design choices:
- Reuses v1b-xml prompt + markers verbatim from `v0-sentences/run.py` —
  one source of truth.
- Filters out `do_not_flag` candidates. v1b-xml has a binary label space
  by design; out-of-scope handling (case names, quoted text, headings,
  compound modifiers) is the deterministic-prefilter's job, not the
  LLM's. Same framing as v0-sentences.
- Wraps the target by `char_start`/`char_end` (the offsets recorded
  during candidate enumeration) — more reliable than string matching
  when triggers repeat in the same paragraph.
- Applies the EXP-07a quote-fix: substitutes embedded `"ShortForm"` for
  `'ShortForm'` (single capitalized identifier in straight or curly
  double-quotes) before sending. This avoids qwen3.5:9b's deterministic
  unescaped-quote JSON parse failures on `(the "District")` defined-term
  constructions, which appear in ~25 of the binary candidates.
- Gives the LLM ONLY the (quote-fixed) paragraph_text with the marker —
  no defined-term context, no prior paragraph. v0-sentences was a pure
  per-sentence test; this preserves that purity. If v1b-xml needs more
  context to handle real briefs, we want that to show up here as a
  signal, not be papered over by giving it the heavyweight context.
- Maps model labels (capitalize/lowercase) to gold's three-label space
  (must_capitalize/must_lowercase/do_not_flag) for direct comparison.
- Reuses score() and print_summary_table() from run_eval.py so the
  output table is shaped exactly like the heavyweight-baseline run.

Per-model output: `results.v1b-xml.{model_safe}.json` — namespaced by
prompt so it doesn't clobber the heavyweight `results.{model}.json`
files already in this directory.

Run from repo root:

    .venv/bin/python rules/03-cap-district/eval/run_eval_v1bxml.py
    .venv/bin/python rules/03-cap-district/eval/run_eval_v1bxml.py --models qwen3.5:9b --limit 5
    .venv/bin/python rules/03-cap-district/eval/run_eval_v1bxml.py --temperature 0.7
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
from pathlib import Path

EVAL_DIR = Path(__file__).parent
REPO_ROOT = EVAL_DIR.parents[2]
sys.path.insert(0, str(REPO_ROOT))

from shared.ollama_client import classify  # noqa: E402

# Reuse v1b-xml prompt + markers verbatim from the v0-sentences research harness.
_V0_RUN_SPEC = importlib.util.spec_from_file_location(
    "_v0_run", EVAL_DIR / "v0-sentences" / "run.py"
)
_v0_run = importlib.util.module_from_spec(_V0_RUN_SPEC)
_V0_RUN_SPEC.loader.exec_module(_v0_run)

# Reuse score() and print_summary_table() from the heavyweight eval so the
# output table matches the baseline run exactly.
_RUN_EVAL_SPEC = importlib.util.spec_from_file_location("_run_eval", EVAL_DIR / "run_eval.py")
_run_eval = importlib.util.module_from_spec(_RUN_EVAL_SPEC)
_RUN_EVAL_SPEC.loader.exec_module(_run_eval)


PROMPT_KEY = "v1b-xml"
SYSTEM_PROMPT = _v0_run.PROMPTS[PROMPT_KEY]
MARKERS = _v0_run.MARKERS[PROMPT_KEY]
SCHEMA = _v0_run.SCHEMA  # {reasoning, label, confidence}; label ∈ {capitalize, lowercase}

DEFAULT_MODELS = [
    "gemma4:e2b",
    "gemma4:e4b",
    "gemma4:26b",
    "qwen3.5:9b",
]

FIXTURES = list(_run_eval.FIXTURES.keys())  # ["clean", "kitchen-sink", "realistic-mixed"]

# Map v1b-xml's binary labels onto the three-label gold space. The gold
# `do_not_flag` bucket is filtered out before inference, so the LLM is never
# expected to produce that label.
LABEL_MAP = {
    "capitalize": "must_capitalize",
    "lowercase": "must_lowercase",
}

# EXP-07a quote-fix. Match a single capitalized identifier wrapped in straight
# or curly double-quotes — the defined-term short-form pattern that breaks
# qwen3.5:9b's JSON. Substitute single straight quotes around the identifier.
# Targeted on purpose: longer quoted strings (statutory text, contract
# excerpts) are left alone — those are out-of-scope (do_not_flag) and we've
# filtered them out of the input set anyway.
_QUOTE_FIX_PAT = re.compile(r"[\"“”]([A-Z][A-Za-z]+)[\"“”]")


def apply_quote_fix(text: str) -> str:
    return _QUOTE_FIX_PAT.sub(r"'\1'", text)


def wrap_target_at_offset(paragraph: str, start: int, end: int) -> str:
    open_m, close_m = MARKERS
    return f"{paragraph[:start]}{open_m}{paragraph[start:end]}{close_m}{paragraph[end:]}"


def build_user_prompt(candidate: dict) -> str:
    """Wrap the target inside the (quote-fixed) paragraph and present it.

    Uses the candidate's recorded char_start/char_end offsets, not string
    search, so we don't get fooled when the trigger repeats in a paragraph.
    The quote-fix is applied to the wrapped paragraph (so the marker doesn't
    accidentally get rewritten) — the wrap happens first, then the substitute.
    """
    wrapped = wrap_target_at_offset(
        candidate["paragraph_text"], candidate["char_start"], candidate["char_end"]
    )
    fixed = apply_quote_fix(wrapped)
    return f"Sentence: {fixed}"


def safe_model_name(model: str) -> str:
    return model.replace(":", "__").replace("/", "_")


def load_binary_corpus(fixtures: list[str]) -> tuple[list[dict], dict[str, int]]:
    """Load candidates, filter to binary subset, return rows + a counts breakdown."""
    rows: list[dict] = []
    counts = {"must_capitalize": 0, "must_lowercase": 0, "do_not_flag": 0, "unlabeled": 0}
    for fix in fixtures:
        path = EVAL_DIR / f"candidates.{fix}.json"
        with path.open() as f:
            for cand in json.load(f):
                gold = cand.get("label")
                if not gold:
                    counts["unlabeled"] += 1
                    continue
                counts[gold] = counts.get(gold, 0) + 1
                if gold in ("must_capitalize", "must_lowercase"):
                    rows.append(cand)
    return rows, counts


def run_model(
    model: str,
    corpus: list[dict],
    *,
    temperature: float,
) -> list[dict]:
    results: list[dict] = []
    started = time.perf_counter()
    last_idx = len(corpus) - 1
    for i, cand in enumerate(corpus):
        keep_alive = 0 if i == last_idx else None
        user = build_user_prompt(cand)
        res = classify(
            model=model,
            system=SYSTEM_PROMPT,
            user=user,
            schema=SCHEMA,
            keep_alive=keep_alive,
            temperature=temperature,
        )
        gold = cand["label"]
        raw_label = (res.payload or {}).get("label") if res.ok else None
        mapped_label = LABEL_MAP.get(raw_label) if raw_label else None
        results.append(
            {
                "candidate_id": cand["id"],
                "fixture": cand["fixture"],
                "current_form": cand["current_form"],
                "gold_label": gold,
                "model_label_raw": raw_label,
                "model_label": mapped_label,
                "model_reasoning": (res.payload or {}).get("reasoning") if res.ok else None,
                "model_confidence": (res.payload or {}).get("confidence") if res.ok else None,
                "correct": (mapped_label == gold) if res.ok else False,
                "ok": res.ok,
                "error": res.error,
                "raw_content": res.raw_content,
                "latency_ms": round(res.latency_ms, 1),
            }
        )
        if (i + 1) % 20 == 0 or i == last_idx:
            elapsed = time.perf_counter() - started
            print(f"  {model}: {i + 1}/{len(corpus)} ({elapsed:.1f}s elapsed)", file=sys.stderr)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--models",
        default=",".join(DEFAULT_MODELS),
        help="comma-separated list of Ollama models (size order matters for memory)",
    )
    parser.add_argument(
        "--fixtures",
        default=",".join(FIXTURES),
        help="comma-separated list of fixture names to include",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="run only the first N candidates after filtering (for smoke testing)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="sampling temperature (default 0.0 deterministic; non-zero values get a t-suffix in result filenames)",
    )
    parser.add_argument(
        "--score-only",
        action="store_true",
        help="skip inference; re-read existing results.v1b-xml.*.json and reprint the table",
    )
    args = parser.parse_args()

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    fixtures = [f.strip() for f in args.fixtures.split(",") if f.strip()]
    temp_suffix = "" if args.temperature == 0.0 else f".t{int(round(args.temperature * 10)):02d}"
    file_prefix = f"results.{PROMPT_KEY}{temp_suffix}"

    if not args.score_only:
        corpus, counts = load_binary_corpus(fixtures)
        if args.limit:
            corpus = corpus[: args.limit]
        print(f"  prompt: {PROMPT_KEY} (markers: {MARKERS[0]}…{MARKERS[1]})", file=sys.stderr)
        print(f"  temperature: {args.temperature}", file=sys.stderr)
        print(f"  corpus counts (gold): {counts}", file=sys.stderr)
        print(
            f"  binary subset: {len(corpus)} candidates "
            f"({sum(1 for c in corpus if c['label'] == 'must_capitalize')} cap / "
            f"{sum(1 for c in corpus if c['label'] == 'must_lowercase')} low)",
            file=sys.stderr,
        )

        for model in models:
            print(f"\n  running {model} ...", file=sys.stderr)
            results = run_model(model, corpus, temperature=args.temperature)
            out_path = EVAL_DIR / f"{file_prefix}.{safe_model_name(model)}.json"
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"    wrote {out_path.name}", file=sys.stderr)

    # Score whatever results files exist for the requested models. Reuses
    # run_eval.score() / print_summary_table() so the table format matches the
    # heavyweight baseline. The do_not_flag column will read 0 because we
    # filtered those out — that's expected.
    model_metrics: dict[str, dict] = {}
    for model in models:
        path = EVAL_DIR / f"{file_prefix}.{safe_model_name(model)}.json"
        if not path.exists():
            print(f"  no results file for {model} — skipping in summary", file=sys.stderr)
            continue
        with path.open() as f:
            results = json.load(f)
        model_metrics[model] = _run_eval.score(results)

    if model_metrics:
        _run_eval.print_summary_table(model_metrics)

    return 0


if __name__ == "__main__":
    sys.exit(main())
