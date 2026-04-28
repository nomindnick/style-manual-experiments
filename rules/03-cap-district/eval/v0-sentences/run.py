"""First-principles sentence-level test for LS-CAP-02.

Tests whether small models can determine specific-vs-generic from a single
sentence's context alone, with a minimal prompt and no document-level context.
The `do_not_flag` (out-of-scope) bucket is deliberately excluded — this round
is just the binary form judgment.

The phrase to judge is wrapped in `[[...]]` markers in the prompt. Models run
in size order; the last call for each model passes `keep_alive=0` so the
server unloads it before the next model loads (avoids 30 GB-RAM thrash).

Run from repo root:

    .venv/bin/python rules/03-cap-district/eval/v0-sentences/run.py
    .venv/bin/python rules/03-cap-district/eval/v0-sentences/run.py --models gemma4:e4b
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from shared.ollama_client import classify  # noqa: E402

HERE = Path(__file__).parent

DEFAULT_MODELS = [
    "gemma4:e2b",
    "gemma4:e4b",
    "gemma4:26b",
    "qwen3.5:9b",
]

LABELS = ("capitalize", "lowercase")

SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "label": {"type": "string", "enum": list(LABELS)},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    },
    "required": ["reasoning", "label", "confidence"],
}

PROMPTS = {
    # v0: minimal first-principles prompt. No legal context.
    "v0": """You are applying a style rule to a single sentence.

The style rule: terms like "school district", "district", "board of education", "board", "city", "city council", "county", "board of supervisors", and similar terms should be capitalized when they refer to a specific, identifiable agency or governing body. The same terms should be lowercase when used generically — referring to a class of agency, a hypothetical, or a statutory category rather than a specific named entity.

In the sentence below, the phrase you must judge is marked with [[ ]] brackets. These brackets are not part of the sentence; they only identify your target. Judge only that bracketed phrase — do not judge any other trigger words that may appear elsewhere in the sentence.

Determine whether the bracketed phrase refers to a specific identifiable agency/body (in which case it should be capitalized) or is being used in a generic sense (in which case it should be lowercase).

Respond with a JSON object containing exactly these three fields, in this order:
- "reasoning": a brief explanation of your judgment.
- "label": "capitalize" or "lowercase".
- "confidence": "high", "medium", or "low".""",

    # v1a: v0 + one-line legal context. Tests whether naming the document
    # type alone moves the dial.
    "v1a": """You are applying a style rule to a single sentence taken from a legal document drafted by an attorney.

The style rule: terms like "school district", "district", "board of education", "board", "city", "city council", "county", "board of supervisors", and similar terms should be capitalized when they refer to a specific, identifiable agency or governing body. The same terms should be lowercase when used generically — referring to a class of agency, a hypothetical, or a statutory category rather than a specific named entity.

In the sentence below, the phrase you must judge is marked with [[ ]] brackets. These brackets are not part of the sentence; they only identify your target. Judge only that bracketed phrase — do not judge any other trigger words that may appear elsewhere in the sentence.

Determine whether the bracketed phrase refers to a specific identifiable agency/body (in which case it should be capitalized) or is being used in a generic sense (in which case it should be lowercase).

Respond with a JSON object containing exactly these three fields, in this order:
- "reasoning": a brief explanation of your judgment.
- "label": "capitalize" or "lowercase".
- "confidence": "high", "medium", or "low".""",

    # v1b: v1a + one sentence explaining the significance of the legal-
    # drafting context (party/recipient vs. abstract law). Targets the
    # statutory-paraphrase failure mode that hit both e4b and qwen-9b on v0.
    "v1b": """You are applying a style rule to a single sentence taken from a legal document drafted by an attorney. As such, the attorney may at times refer to a specific agency that is a party to the proceeding or the recipient of the document, and may at other times use an agency or governing-board designation more broadly to explain how the law applies generally.

The style rule: terms like "school district", "district", "board of education", "board", "city", "city council", "county", "board of supervisors", and similar terms should be capitalized when they refer to a specific, identifiable agency or governing body. The same terms should be lowercase when used generically — referring to a class of agency, a hypothetical, or a statutory category rather than a specific named entity.

In the sentence below, the phrase you must judge is marked with [[ ]] brackets. These brackets are not part of the sentence; they only identify your target. Judge only that bracketed phrase — do not judge any other trigger words that may appear elsewhere in the sentence.

Determine whether the bracketed phrase refers to a specific identifiable agency/body (in which case it should be capitalized) or is being used in a generic sense (in which case it should be lowercase).

Respond with a JSON object containing exactly these three fields, in this order:
- "reasoning": a brief explanation of your judgment.
- "label": "capitalize" or "lowercase".
- "confidence": "high", "medium", or "low".""",

    # v1b-xml: identical content to v1b, but the target marker is
    # <target>...</target> instead of [[ ]]. Tests an external suggestion
    # that grammar-constrained JSON decoding may misbehave when bracket
    # tokens appear in the user message — the deterministic cap-03 schema
    # violation on qwen3.5:9b is the specific failure under investigation.
    "v1b-xml": """You are applying a style rule to a single sentence taken from a legal document drafted by an attorney. As such, the attorney may at times refer to a specific agency that is a party to the proceeding or the recipient of the document, and may at other times use an agency or governing-board designation more broadly to explain how the law applies generally.

The style rule: terms like "school district", "district", "board of education", "board", "city", "city council", "county", "board of supervisors", and similar terms should be capitalized when they refer to a specific, identifiable agency or governing body. The same terms should be lowercase when used generically — referring to a class of agency, a hypothetical, or a statutory category rather than a specific named entity.

In the sentence below, the phrase you must judge is wrapped in <target>...</target> tags. These tags are not part of the sentence; they only identify your target. Judge only the phrase between the tags — do not judge any other trigger words that may appear elsewhere in the sentence.

Determine whether the tagged phrase refers to a specific identifiable agency/body (in which case it should be capitalized) or is being used in a generic sense (in which case it should be lowercase).

Respond with a JSON object containing exactly these three fields, in this order:
- "reasoning": a brief explanation of your judgment.
- "label": "capitalize" or "lowercase".
- "confidence": "high", "medium", or "low".""",
}

# Per-prompt target marker. Most prompts use [[ ]]; v1b-xml swaps in XML tags
# to test whether bracket tokens were destabilizing grammar-constrained JSON
# decoding on qwen3.5:9b's deterministic cap-03 failure.
MARKERS: dict[str, tuple[str, str]] = {
    "v0": ("[[", "]]"),
    "v1a": ("[[", "]]"),
    "v1b": ("[[", "]]"),
    "v1b-xml": ("<target>", "</target>"),
}


def find_nth(haystack: str, needle: str, n: int) -> int:
    """Return the start index of the nth (1-indexed) occurrence of needle, or -1."""
    pos = -1
    for _ in range(n):
        pos = haystack.find(needle, pos + 1)
        if pos == -1:
            return -1
    return pos


def wrap_target(
    sentence: str,
    target_form: str,
    occurrence: int,
    markers: tuple[str, str] = ("[[", "]]"),
) -> str:
    start = find_nth(sentence, target_form, occurrence)
    if start == -1:
        raise ValueError(
            f"target {target_form!r} (occurrence {occurrence}) not found in: {sentence!r}"
        )
    end = start + len(target_form)
    open_m, close_m = markers
    return f"{sentence[:start]}{open_m}{sentence[start:end]}{close_m}{sentence[end:]}"


def validate_corpus(corpus: list[dict]) -> None:
    """Catch JSON typos before burning model time."""
    for row in corpus:
        wrap_target(row["sentence"], row["target_form"], row.get("target_occurrence", 1))
        if row["gold_label"] not in LABELS:
            raise ValueError(f"{row['id']}: unknown gold_label {row['gold_label']!r}")


def build_user_prompt(row: dict, markers: tuple[str, str]) -> str:
    marked = wrap_target(
        row["sentence"], row["target_form"], row.get("target_occurrence", 1), markers
    )
    return f"Sentence: {marked}"


def safe_model_name(model: str) -> str:
    return model.replace(":", "__").replace("/", "_")


def run_model(
    model: str,
    corpus: list[dict],
    system_prompt: str,
    markers: tuple[str, str],
    temperature: float,
) -> list[dict]:
    results: list[dict] = []
    started = time.perf_counter()
    last_idx = len(corpus) - 1
    for i, row in enumerate(corpus):
        keep_alive = 0 if i == last_idx else None
        res = classify(
            model=model,
            system=system_prompt,
            user=build_user_prompt(row, markers),
            schema=SCHEMA,
            keep_alive=keep_alive,
            temperature=temperature,
        )
        gold = row["gold_label"]
        payload = res.payload or {}
        model_label = payload.get("label") if res.ok else None
        results.append(
            {
                "id": row["id"],
                "gold_label": gold,
                "model_label": model_label,
                "model_reasoning": payload.get("reasoning") if res.ok else None,
                "model_confidence": payload.get("confidence") if res.ok else None,
                "correct": (model_label == gold) if res.ok else False,
                "ok": res.ok,
                "error": res.error,
                "latency_ms": round(res.latency_ms, 1),
                "sentence": row["sentence"],
                "target_form": row["target_form"],
                "target_occurrence": row.get("target_occurrence", 1),
                "notes": row.get("notes", ""),
            }
        )
        elapsed = time.perf_counter() - started
        flag = "ok " if res.ok else "ERR"
        mark = "✓" if results[-1]["correct"] else "✗"
        print(
            f"  {model} {i+1:>2}/{len(corpus)}  {row['id']}  {flag}  "
            f"gold={gold:<10} pred={str(model_label):<10} {mark}  ({elapsed:.0f}s)",
            file=sys.stderr,
        )
    return results


def score(results: list[dict]) -> dict:
    total = len(results)
    ok = sum(1 for r in results if r["ok"])
    correct = sum(1 for r in results if r["correct"])
    per_class = {}
    for label in LABELS:
        gold_n = sum(1 for r in results if r["gold_label"] == label)
        right = sum(1 for r in results if r["gold_label"] == label and r["correct"])
        per_class[label] = {
            "total": gold_n,
            "correct": right,
            "accuracy": (right / gold_n) if gold_n else 0.0,
        }
    mean_latency = sum(r["latency_ms"] for r in results) / total if total else 0.0
    return {
        "total": total,
        "ok": ok,
        "errors": total - ok,
        "correct": correct,
        "accuracy": (correct / ok) if ok else 0.0,
        "per_class": per_class,
        "mean_latency_ms": mean_latency,
    }


def print_summary(model_metrics: dict[str, dict]) -> None:
    print()
    print(f"{'model':<18} {'ok':>3} {'err':>3} {'acc':>6} {'cap':>6} {'low':>6} {'lat(ms)':>9}")
    print("-" * 60)
    for model, m in model_metrics.items():
        print(
            f"{model:<18} {m['ok']:>3} {m['errors']:>3} {m['accuracy']*100:>5.1f}% "
            f"{m['per_class']['capitalize']['accuracy']*100:>5.1f}% "
            f"{m['per_class']['lowercase']['accuracy']*100:>5.1f}% "
            f"{m['mean_latency_ms']:>9.0f}"
        )


def print_misses(model: str, results: list[dict], markers: tuple[str, str]) -> None:
    misses = [r for r in results if not r["correct"]]
    if not misses:
        print(f"\n  {model} — perfect, no misses")
        return
    print(f"\n  {model} — {len(misses)} miss(es):")
    for r in misses:
        marked = wrap_target(r["sentence"], r["target_form"], r["target_occurrence"], markers)
        if r["ok"]:
            header = f"gold={r['gold_label']} → pred={r['model_label']} ({r['model_confidence']})"
        else:
            header = f"ERROR: {r['error']}"
        print(f"    [{r['id']}] {header}")
        print(f"      {marked}")
        print(f"      notes:     {r['notes']}")
        if r["ok"]:
            print(f"      reasoning: {r['model_reasoning']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--models",
        default=",".join(DEFAULT_MODELS),
        help="comma-separated list of Ollama models (size order matters for memory)",
    )
    parser.add_argument(
        "--prompt",
        default="v0",
        choices=sorted(PROMPTS.keys()),
        help="which prompt variant from PROMPTS to use (output files namespaced by this)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="sampling temperature (default 0.0 deterministic; non-zero values get a t-suffix in result filenames)",
    )
    args = parser.parse_args()
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    system_prompt = PROMPTS[args.prompt]
    markers = MARKERS[args.prompt]
    temp_suffix = "" if args.temperature == 0.0 else f".t{int(round(args.temperature * 10)):02d}"

    with (HERE / "sentences.json").open() as f:
        corpus = json.load(f)
    validate_corpus(corpus)
    cap_n = sum(1 for r in corpus if r["gold_label"] == "capitalize")
    low_n = sum(1 for r in corpus if r["gold_label"] == "lowercase")
    print(f"  prompt: {args.prompt} (markers: {markers[0]}…{markers[1]})", file=sys.stderr)
    print(f"  temperature: {args.temperature}", file=sys.stderr)
    print(f"  corpus: {len(corpus)} sentences ({cap_n} cap / {low_n} low)", file=sys.stderr)

    all_results: dict[str, list[dict]] = {}
    for model in models:
        print(f"\n  running {model} ...", file=sys.stderr)
        results = run_model(model, corpus, system_prompt, markers, args.temperature)
        out_path = HERE / f"results.{args.prompt}{temp_suffix}.{safe_model_name(model)}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"    wrote {out_path.name}", file=sys.stderr)
        all_results[model] = results

    print_summary({m: score(r) for m, r in all_results.items()})
    for model, results in all_results.items():
        print_misses(model, results, markers)

    return 0


if __name__ == "__main__":
    sys.exit(main())
