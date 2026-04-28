"""EXP-07b: gemma4:e4b × v1b-xml × T=0.7 × 5 seeds.

EXP-06 single-pass at T=0.7 lifted e4b from 80.0% to 85.0% by unlocking
low-03 with cleaner generic-class reasoning. Single-pass on a 20-sentence
corpus is coin-flippy; this probe runs five independent passes to check
whether the lift is consistent (real ceiling-break) or just one lucky
roll. Writes a consolidated per-sentence stability table.

Run from repo root:

    .venv/bin/python rules/03-cap-district/eval/v0-sentences/e4b_t07_multiseed.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
REPO_ROOT = HERE.parents[3]
sys.path.insert(0, str(REPO_ROOT))

from shared.ollama_client import classify  # noqa: E402

_spec = importlib.util.spec_from_file_location("_run", HERE / "run.py")
_run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_run)


MODEL = "gemma4:e4b"
PROMPT_KEY = "v1b-xml"
TEMPERATURE = 0.7
N_SEEDS = 5
SYSTEM = _run.PROMPTS[PROMPT_KEY]
MARKERS = _run.MARKERS[PROMPT_KEY]


def main() -> int:
    with (HERE / "sentences.json").open() as f:
        corpus: list[dict] = json.load(f)
    _run.validate_corpus(corpus)

    n_calls = N_SEEDS * len(corpus)
    print(
        f"  model: {MODEL}  prompt: {PROMPT_KEY}  temperature: {TEMPERATURE}  "
        f"seeds: {N_SEEDS}  total calls: {n_calls}",
        file=sys.stderr,
    )

    # per_sentence[id] = list of (label_or_None, ok)
    per_sentence: dict[str, list[tuple[str | None, bool]]] = {r["id"]: [] for r in corpus}
    gold = {r["id"]: r["gold_label"] for r in corpus}
    started = time.perf_counter()

    last_seed = N_SEEDS - 1
    last_idx = len(corpus) - 1
    for seed_idx in range(N_SEEDS):
        print(f"\n  seed {seed_idx + 1}/{N_SEEDS}", file=sys.stderr)
        for i, row in enumerate(corpus):
            is_final = seed_idx == last_seed and i == last_idx
            keep_alive = 0 if is_final else None
            res = classify(
                model=MODEL,
                system=SYSTEM,
                user=_run.build_user_prompt(row, MARKERS),
                schema=_run.SCHEMA,
                temperature=TEMPERATURE,
                keep_alive=keep_alive,
            )
            label = (res.payload or {}).get("label") if res.ok else None
            per_sentence[row["id"]].append((label, res.ok))
            elapsed = time.perf_counter() - started
            mark = "✓" if (label == gold[row["id"]]) else ("E" if not res.ok else "✗")
            print(
                f"    s{seed_idx + 1}  {row['id']:6s}  "
                f"gold={gold[row['id']]:<10}  pred={str(label):<10}  {mark}  ({elapsed:.0f}s)",
                file=sys.stderr,
            )

    # Aggregate.
    print("\n" + "=" * 78)
    print(f"e4b × v1b-xml × T={TEMPERATURE} × {N_SEEDS} seeds — per-sentence stability")
    print("=" * 78)
    print(f"{'id':<8} {'gold':<10} {'labels per seed':<40} {'correct':>10}")
    print("-" * 78)
    total_correct = 0
    for row in corpus:
        rid = row["id"]
        labels = [lab for lab, _ in per_sentence[rid]]
        oks = [ok for _, ok in per_sentence[rid]]
        n_correct = sum(1 for lab, ok in per_sentence[rid] if ok and lab == gold[rid])
        total_correct += n_correct
        labels_str = " ".join((lab or "ERR")[:3] for lab in labels)
        flag = " (unstable)" if len(set(labels)) > 1 else ""
        print(f"{rid:<8} {gold[rid]:<10} {labels_str:<40} {n_correct}/{N_SEEDS}{flag}")

    overall = total_correct / (N_SEEDS * len(corpus))
    print("-" * 78)
    print(f"Overall: {total_correct}/{N_SEEDS * len(corpus)} = {overall * 100:.1f}%")
    print()
    print("Reference points:")
    print("  EXP-05  T=0    e4b v1b-xml:  16/20 = 80.0%")
    print("  EXP-06  T=0.7  e4b v1b-xml (single-pass):  17/20 = 85.0%")

    out_path = HERE / f"results.v1b-xml.t07.multiseed{N_SEEDS}.gemma4__e4b.json"
    out = {
        "model": MODEL,
        "prompt": PROMPT_KEY,
        "temperature": TEMPERATURE,
        "n_seeds": N_SEEDS,
        "per_sentence": {
            rid: {
                "gold": gold[rid],
                "labels": [lab for lab, _ in seeds],
                "oks": [ok for _, ok in seeds],
                "n_correct": sum(1 for lab, ok in seeds if ok and lab == gold[rid]),
            }
            for rid, seeds in per_sentence.items()
        },
        "overall_correct": total_correct,
        "overall_total": N_SEEDS * len(corpus),
        "overall_accuracy": overall,
    }
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote {out_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
