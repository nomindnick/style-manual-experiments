"""Relabel compound-modifier candidates to `do_not_flag` per LABELING.md.

Resolves the scheme gap surfaced by the smoke test: trigger words sitting in
compound-modifier or function-descriptor positions (`board-approved`,
`school-district contracts`, `board approval`, `governing board`, etc.) are
out of LS-CAP-02 scope under the resolved rule, regardless of whether the
surrounding sentence is about the named party.

Detection looks at the candidate's actual surrounding text:
  * a hyphen immediately before or after the candidate → hyphenated compound
    (`school-district contracts`, `board-approved`)
  * the word "governing" (or similar descriptor) immediately before → function
    descriptor (`the governing board`)
  * a function-descriptor noun (`approval`, `action`, `approved`, `member`,
    `meeting`) immediately after → function-descriptor noun phrase (`board
    approval`, `board action`)

Possessive uses (`the District's officials`), bare proper-noun references
(`the Board of Trustees`), and bare adjectival uses (`District maintenance
employee`) are NOT touched — those remain whatever the agents labeled.

Note-based EXCLUSIONS are also applied: case names, block quotes, section
headings, and statute paraphrases are settled buckets and never relabeled.

Run from repo root:
    .venv/bin/python rules/03-cap-district/eval/relabel_compound_modifiers.py
    .venv/bin/python rules/03-cap-district/eval/relabel_compound_modifiers.py --apply
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).parent
FIXTURES = ["clean", "kitchen-sink", "realistic-mixed"]

# Settled buckets — never re-relabel these regardless of text pattern.
EXCLUDE_NOTE_KEYWORDS = (
    "case name", "case-name", "block", "quoted", "quotation",
    "heading", "paraphras",
)

DESCRIPTOR_BEFORE = ("governing",)  # case-insensitive
FUNCTION_NOUNS_AFTER = (
    "approval", "approvals", "action", "actions",
    "member", "members", "meeting", "meetings",
)
# `approved` / `approving` are verbs, not nouns — `the Board approved X` is a
# bare proper-noun subject, not a compound modifier. The hyphenated form
# (`board-approved`) is already caught by the hyphen rule.


def is_compound_modifier(row: dict) -> tuple[bool, str]:
    """Return (matches, why) using the candidate's actual surrounding text."""
    text = row["paragraph_text"]
    cs, ce = row["char_start"], row["char_end"]
    before = text[max(0, cs - 30):cs]
    after = text[ce:ce + 30]

    if before.endswith("-"):
        return True, "hyphen before candidate"
    if after.startswith("-"):
        return True, "hyphen after candidate"

    # Word immediately before, lowercased, no trailing punctuation.
    before_match = re.search(r"(\w+)\s+$", before)
    if before_match and before_match.group(1).lower() in DESCRIPTOR_BEFORE:
        return True, f"preceded by '{before_match.group(1)}'"

    # Word immediately after, stripped of punctuation.
    after_match = re.match(r"\s+(\w+)", after)
    if after_match and after_match.group(1).lower().rstrip(",;.:") in FUNCTION_NOUNS_AFTER:
        return True, f"followed by '{after_match.group(1)}'"

    return False, ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--apply", action="store_true",
                        help="write relabeled files; default is dry-run preview only")
    args = parser.parse_args()

    total_changed = 0
    for fixture in FIXTURES:
        path = EVAL_DIR / f"candidates.{fixture}.json"
        with path.open() as f:
            rows = json.load(f)
        changes = []
        for row in rows:
            notes_lc = (row.get("notes") or "").lower()
            if any(k in notes_lc for k in EXCLUDE_NOTE_KEYWORDS):
                continue  # settled bucket
            matches, why = is_compound_modifier(row)
            if not matches:
                continue
            if row["label"] == "do_not_flag":
                continue  # already correct
            changes.append({
                "id": row["id"],
                "current_form": row["current_form"],
                "old_label": row["label"],
                "why": why,
                "context_snippet": row["paragraph_text"][
                    max(0, row["char_start"] - 30):row["char_end"] + 30
                ],
            })
            row["label"] = "do_not_flag"
            row["notes"] = "[compound-modifier rule] " + (row["notes"] or "")
        if changes:
            print(f"{fixture}: {len(changes)} rows would change to do_not_flag")
            for c in changes:
                print(f"  {c['id']} ({c['current_form']!r}) {c['old_label']} → do_not_flag  [{c['why']}]")
                print(f"      ...{c['context_snippet']}...")
            total_changed += len(changes)
        if args.apply and changes:
            with path.open("w", encoding="utf-8") as f:
                json.dump(rows, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"  wrote {path.name}")

    print()
    print(f"Total: {total_changed} rows" + (" written" if args.apply else " (dry run; pass --apply)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
