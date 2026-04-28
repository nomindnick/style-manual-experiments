"""Benchmark local Ollama models on the LS-CAP-02 labeled corpus.

Loads the hand-labeled candidate files (`candidates.{fixture}.json`), and for
each (model, candidate) pair calls Ollama with a structured-output schema,
records the model's classification, and aggregates accuracy + per-class
precision/recall against the gold labels.

Defined-term extraction is inline (a small regex pass over the .docx) — the
prompt context tells the LLM which short forms have been set up as
proper-noun referents in the document, since that's the most important signal
for the rule.

Per-model results land at `results.{model_safe}.json`. A summary table prints
to stdout. Run from repo root:

    .venv/bin/python rules/03-cap-district/eval/run_eval.py
    .venv/bin/python rules/03-cap-district/eval/run_eval.py --models gemma4:e4b --limit 5  # smoke
    .venv/bin/python rules/03-cap-district/eval/run_eval.py --score-only                   # re-print metrics
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from shared.document import Document  # noqa: E402
from shared.ollama_client import classify  # noqa: E402

EVAL_DIR = Path(__file__).parent

DEFAULT_MODELS = [
    "gemma4:e4b",
    "gemma4:26b",
    "qwen3.5:9b",
    "qwen3.5:27b",
]

FIXTURES = {
    "clean": REPO_ROOT / "fixtures" / "clean.docx",
    "kitchen-sink": REPO_ROOT / "fixtures" / "kitchen-sink-violations.docx",
    "realistic-mixed": REPO_ROOT / "fixtures" / "realistic-mixed.docx",
}

LABELS = ("must_capitalize", "must_lowercase", "do_not_flag")

SCHEMA = {
    "type": "object",
    "properties": {
        "label": {"type": "string", "enum": list(LABELS)},
        "reasoning": {"type": "string"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    },
    "required": ["label", "reasoning", "confidence"],
}

SYSTEM_PROMPT = """You are a careful proofreader applying rule LS-CAP-02 from a California law firm's style manual to a litigation draft.

Rule LS-CAP-02 states:
- Capitalize trigger nouns ("district", "school district", "board", "board of education", "board of supervisors", "board of trustees", "city", "city council", "county", "agency", "authority", "joint powers authority") when the reference is to a specific defined agency that has been set up as a party substitute or proper-noun referent earlier in the document.
- Lowercase the trigger when the reference is generic (a statutory class, an abstract example, a hypothetical, or paraphrasing law without referring back to the named party).

Out-of-scope cases (use do_not_flag for all of these):
- The trigger appears inside a case name in a citation (e.g., "Los Angeles County Board of Education v. Smith") - case names are reproduced verbatim.
- Inside quoted statutory text or quoted contract text.
- Inside a section heading (heading-case conventions are not policed by this rule).
- The trigger sits in a COMPOUND MODIFIER or FUNCTION-DESCRIPTOR position. Specifically:
   * Hyphenated compounds where the trigger is part of the compound: "board-approved", "school-district contracts", "school-district public works", "board-approval", "school-district funds".
   * The trigger is preceded by "governing" (e.g., "the governing board", "the District's governing Board").
   * The trigger is immediately followed by a function-descriptor noun like "approval", "action", "member", or "meeting" (e.g., "board approval", "board action", "board members").
   These are out of scope EVEN WHEN the surrounding sentence is unambiguously about the named District. The manual is silent on compound modifiers; the rule abstains rather than firing.

YOUR TASK: identify the CORRECT form for this candidate in this position, regardless of how it currently appears in the draft. A separate downstream step will compare your judgment to the current form and decide whether to flag a violation. Do NOT consider whether the current form happens to match; describe the correct form.

Your response must be a JSON object with exactly these three fields and no others:
- "label": one of three values describing the CORRECT form for this position:
   - "must_capitalize": the correct form is capitalized (e.g., "District", "Board"). Use this whenever the rule requires capitalization here, EVEN IF the candidate already appears capitalized in the draft.
   - "must_lowercase": the correct form is lowercase (e.g., "district", "board"). Use this whenever the rule requires lowercase here, EVEN IF the candidate already appears lowercase.
   - "do_not_flag": the rule does not apply at all (case names, quoted text, headings) OR the manual permits both forms equally. Use this regardless of the current form.
- "reasoning": a brief sentence explaining the call.
- "confidence": one of "high", "medium", or "low".

Example outputs:
{"label": "must_capitalize", "reasoning": "The candidate refers back to the named defendant, defined earlier as 'District'.", "confidence": "high"}
{"label": "must_lowercase", "reasoning": "Generic reference to 'a school district' as a statutory class, not the named party.", "confidence": "high"}
{"label": "do_not_flag", "reasoning": "Trigger appears inside a case name in a citation.", "confidence": "high"}

Be conservative. When genuinely uncertain, prefer do_not_flag with low confidence."""


# Matches `("ShortForm")` and curly-quote variants; ShortForm starts with
# capital letter, then alphabetic. The preceding parenthesis is the anchor.
_DEFINED_TERM_PAT = re.compile(
    r"[\(]\s*[\"'“‘]([A-Z][A-Za-z]+)[\"'’”]\s*[\)]"
)


def extract_defined_terms(docx_path: Path, max_paragraphs: int = 60) -> list[str]:
    """Scan the first N paragraphs for `("ShortForm")` party-substitute setups.

    Returns the unique short forms in document order. The LLM gets this as
    context to disambiguate "District" (defined → must_capitalize) from
    "school district" (generic → must_lowercase).
    """
    doc = Document.load(docx_path)
    seen: list[str] = []
    for para in doc.paragraphs[:max_paragraphs]:
        for match in _DEFINED_TERM_PAT.finditer(para.text):
            short = match.group(1)
            if short not in seen:
                seen.append(short)
    return seen


def build_user_prompt(candidate: dict, defined_terms: list[str]) -> str:
    paragraph = candidate["paragraph_text"]
    cs, ce = candidate["char_start"], candidate["char_end"]
    marked = f"{paragraph[:cs]}<<<{paragraph[cs:ce]}>>>{paragraph[ce:]}"
    defined_str = ", ".join(defined_terms) if defined_terms else "(none detected)"
    prior = candidate["prior_paragraph_text"] or "(no prior paragraph)"
    return (
        f"Defined proper-noun referents set up earlier in this document: {defined_str}\n\n"
        f"Prior paragraph:\n{prior}\n\n"
        f"Current paragraph (the candidate is wrapped in <<<...>>>):\n{marked}\n\n"
        f"The candidate, as it currently appears, is: {candidate['current_form']!r}\n\n"
        f"What label applies?"
    )


def safe_model_name(model: str) -> str:
    return model.replace(":", "__").replace("/", "_")


def load_corpus(fixtures: list[str]) -> list[dict]:
    rows: list[dict] = []
    for fix in fixtures:
        path = EVAL_DIR / f"candidates.{fix}.json"
        with path.open() as f:
            for row in json.load(f):
                if not row.get("label"):
                    print(f"  WARNING: {row['id']} has no label — skipping", file=sys.stderr)
                    continue
                rows.append(row)
    return rows


def run_model(model: str, corpus: list[dict], defined_by_fixture: dict[str, list[str]]) -> list[dict]:
    results: list[dict] = []
    started = time.perf_counter()
    for i, cand in enumerate(corpus, 1):
        defined = defined_by_fixture[cand["fixture"]]
        user = build_user_prompt(cand, defined)
        res = classify(model=model, system=SYSTEM_PROMPT, user=user, schema=SCHEMA)
        gold = cand["label"]
        model_label = (res.payload or {}).get("label") if res.ok else None
        results.append(
            {
                "candidate_id": cand["id"],
                "fixture": cand["fixture"],
                "current_form": cand["current_form"],
                "gold_label": gold,
                "model_label": model_label,
                "model_reasoning": (res.payload or {}).get("reasoning") if res.ok else None,
                "model_confidence": (res.payload or {}).get("confidence") if res.ok else None,
                "correct": (model_label == gold) if res.ok else False,
                "ok": res.ok,
                "error": res.error,
                "raw_content": res.raw_content,
                "latency_ms": round(res.latency_ms, 1),
            }
        )
        if i % 20 == 0 or i == len(corpus):
            elapsed = time.perf_counter() - started
            print(f"  {model}: {i}/{len(corpus)} ({elapsed:.1f}s elapsed)", file=sys.stderr)
    return results


def score(results: list[dict]) -> dict:
    total = len(results)
    ok = sum(1 for r in results if r["ok"])
    correct = sum(1 for r in results if r["correct"])
    by_pair = Counter((r["gold_label"], r["model_label"]) for r in results if r["ok"])

    # Per-class precision/recall (one-vs-rest).
    per_class: dict[str, dict] = {}
    for label in LABELS:
        tp = sum(1 for r in results if r["ok"] and r["gold_label"] == label and r["model_label"] == label)
        fp = sum(1 for r in results if r["ok"] and r["gold_label"] != label and r["model_label"] == label)
        fn = sum(1 for r in results if r["ok"] and r["gold_label"] == label and r["model_label"] != label)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        per_class[label] = {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}

    mean_latency = sum(r["latency_ms"] for r in results) / total if total else 0.0
    return {
        "total": total,
        "ok": ok,
        "errors": total - ok,
        "accuracy": correct / ok if ok else 0.0,
        "correct": correct,
        "per_class": per_class,
        "confusion": dict(by_pair),
        "mean_latency_ms": mean_latency,
    }


def print_summary_table(model_metrics: dict[str, dict]) -> None:
    print()
    print(f"{'model':<20} {'ok':>4} {'err':>4} {'acc':>6} "
          f"{'cap-P':>6} {'cap-R':>6} {'low-P':>6} {'low-R':>6} {'dnf-P':>6} {'dnf-R':>6} "
          f"{'lat(ms)':>9}")
    print("-" * 100)
    for model, m in model_metrics.items():
        cap = m["per_class"]["must_capitalize"]
        low = m["per_class"]["must_lowercase"]
        dnf = m["per_class"]["do_not_flag"]
        print(
            f"{model:<20} {m['ok']:>4} {m['errors']:>4} {m['accuracy']*100:>5.1f}% "
            f"{cap['precision']*100:>5.1f}% {cap['recall']*100:>5.1f}% "
            f"{low['precision']*100:>5.1f}% {low['recall']*100:>5.1f}% "
            f"{dnf['precision']*100:>5.1f}% {dnf['recall']*100:>5.1f}% "
            f"{m['mean_latency_ms']:>9.0f}"
        )
    print()
    print("Confusion (gold → model) is in each model's results.<model>.json.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS),
                        help="comma-separated list of Ollama models to benchmark")
    parser.add_argument("--fixtures", default=",".join(FIXTURES.keys()),
                        help="comma-separated list of fixture names to include")
    parser.add_argument("--limit", type=int, default=None,
                        help="run only the first N candidates (for smoke testing)")
    parser.add_argument("--score-only", action="store_true",
                        help="skip inference; re-read existing results.*.json and reprint the table")
    args = parser.parse_args()

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    fixtures = [f.strip() for f in args.fixtures.split(",") if f.strip()]

    if not args.score_only:
        defined_by_fixture = {fix: extract_defined_terms(FIXTURES[fix]) for fix in fixtures}
        for fix, defined in defined_by_fixture.items():
            print(f"  defined terms in {fix}: {defined}", file=sys.stderr)

        corpus = load_corpus(fixtures)
        if args.limit:
            corpus = corpus[: args.limit]
        print(f"  corpus: {len(corpus)} candidates", file=sys.stderr)

        for model in models:
            print(f"  running {model} ...", file=sys.stderr)
            results = run_model(model, corpus, defined_by_fixture)
            out_path = EVAL_DIR / f"results.{safe_model_name(model)}.json"
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"    wrote {out_path.name}", file=sys.stderr)

    # Score whatever results files exist for the requested models.
    model_metrics: dict[str, dict] = {}
    for model in models:
        path = EVAL_DIR / f"results.{safe_model_name(model)}.json"
        if not path.exists():
            print(f"  no results file for {model} — skipping in summary", file=sys.stderr)
            continue
        with path.open() as f:
            results = json.load(f)
        model_metrics[model] = score(results)

    if model_metrics:
        print_summary_table(model_metrics)

    return 0


if __name__ == "__main__":
    sys.exit(main())
