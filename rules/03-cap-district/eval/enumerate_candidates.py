"""Enumerate LS-CAP-02 trigger-noun candidates across the Phase 0.5 fixtures.

Walks the three fixture .docx files, finds every occurrence of an LS-CAP-02
trigger phrase in body-prose paragraphs (i.e., skipping all-caps captions,
headings, and signature blocks), and writes one row per occurrence to a
per-fixture JSON file: `candidates.{fixture}.json`. The user then hand-labels
each row with `must_capitalize`, `must_lowercase`, or `do_not_flag` — see
LABELING.md for the scheme.

Run from repo root:
    .venv/bin/python rules/03-cap-district/eval/enumerate_candidates.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from shared.document import Document  # noqa: E402

# Longest first — Python regex alternation is leftmost match, not longest, so
# multi-word forms must precede their single-word prefixes to win the match.
TRIGGERS = [
    "joint powers authority",
    "board of education",
    "board of supervisors",
    "board of trustees",
    "school district",
    "city council",
    "district",
    "board",
    "city",
    "county",
    "agency",
    "authority",
]

TRIGGER_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in TRIGGERS) + r")\b",
    re.IGNORECASE,
)

FIXTURES = [
    ("clean", REPO_ROOT / "fixtures" / "clean.docx"),
    ("kitchen-sink", REPO_ROOT / "fixtures" / "kitchen-sink-violations.docx"),
    ("realistic-mixed", REPO_ROOT / "fixtures" / "realistic-mixed.docx"),
]

OUTPUT_DIR = Path(__file__).parent


def is_body_prose(text: str) -> bool:
    """LS-CAP-02 applies to body prose only; captions, headings, and signature
    blocks in CA litigation are conventionally all-caps and out of scope."""
    if not any(c.isalpha() for c in text):
        return False
    return text != text.upper()


def enumerate_fixture(fixture_name: str, docx_path: Path) -> list[dict]:
    doc = Document.load(docx_path)
    paragraphs = doc.paragraphs
    rows: list[dict] = []
    for para in paragraphs:
        if not is_body_prose(para.text):
            continue
        prior_text = paragraphs[para.index - 1].text if para.index > 0 else ""
        for match in TRIGGER_PATTERN.finditer(para.text):
            rows.append(
                {
                    "id": f"{fixture_name}-p{para.index}-c{match.start()}",
                    "fixture": fixture_name,
                    "paragraph_index": para.index,
                    "char_start": match.start(),
                    "char_end": match.end(),
                    "current_form": match.group(0),
                    "paragraph_text": para.text,
                    "prior_paragraph_text": prior_text,
                    "label": "",
                    "notes": "",
                }
            )
    return rows


def main() -> int:
    for fixture_name, docx_path in FIXTURES:
        out_path = OUTPUT_DIR / f"candidates.{fixture_name}.json"
        if out_path.exists():
            alt = out_path.with_name(f"candidates.{fixture_name}.new.json")
            print(
                f"WARNING: {out_path.name} already exists; writing to {alt.name} "
                f"so labeling work isn't clobbered.",
                file=sys.stderr,
            )
            target = alt
        else:
            target = out_path

        rows = enumerate_fixture(fixture_name, docx_path)
        with target.open("w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  {fixture_name}: {len(rows)} candidates → {target.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
