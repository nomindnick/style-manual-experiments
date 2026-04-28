"""EXP-07a: cap-03 unescaped-quote hypothesis probe.

Hypothesis (after EXP-05 falsified bracket-tokens and EXP-06 falsified
temperature-fragility): qwen3.5:9b deterministically breaks JSON on
cap-03 because the sentence contains `(the "District")`, and qwen emits
those embedded quotes unescaped inside its `reasoning` string. If the
hypothesis is right, swapping the embedded `"District"` for
`'District'` should produce a clean parse on the same prompt + model +
temperature.

Run from repo root:

    .venv/bin/python rules/03-cap-district/eval/v0-sentences/cap03_quote_probe.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).parent
REPO_ROOT = HERE.parents[3]
sys.path.insert(0, str(REPO_ROOT))

from shared.ollama_client import classify  # noqa: E402

# Load run.py as a module so we can reuse PROMPTS, MARKERS, SCHEMA, build_user_prompt.
_spec = importlib.util.spec_from_file_location("_run", HERE / "run.py")
_run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_run)


MODEL = "qwen3.5:9b"
PROMPT_KEY = "v1b-xml"
SYSTEM = _run.PROMPTS[PROMPT_KEY]
MARKERS = _run.MARKERS[PROMPT_KEY]

ORIGINAL = {
    "id": "cap-03 (original, double-quoted)",
    "sentence": 'Defendant Fresno Unified School District (the "District") demurs to the Complaint.',
    "target_form": "School District",
    "target_occurrence": 1,
}
DOCTORED = {
    "id": "cap-03 (doctored, single-quoted)",
    "sentence": "Defendant Fresno Unified School District (the 'District') demurs to the Complaint.",
    "target_form": "School District",
    "target_occurrence": 1,
}


def show_raw_around(raw: str | None, char_offset: int | None) -> None:
    if not raw:
        print("  (no raw content captured)")
        return
    print(f"  raw length: {len(raw)} chars")
    if char_offset is not None and 0 <= char_offset < len(raw):
        lo = max(0, char_offset - 40)
        hi = min(len(raw), char_offset + 40)
        print(f"  context around char {char_offset}:")
        print(f"  ...{raw[lo:char_offset]}<<<HERE>>>{raw[char_offset:hi]}...")
    else:
        # Just dump the whole thing if it's small
        print(f"  full raw:")
        for line in raw.splitlines():
            print(f"    {line}")


def parse_offset(err: str | None) -> int | None:
    """Pull `char N` out of an error string like 'JSONDecodeError: ... (char 81)'."""
    if not err:
        return None
    import re

    m = re.search(r"char (\d+)", err)
    return int(m.group(1)) if m else None


def main() -> int:
    cases = [
        (ORIGINAL, None),  # default keep_alive
        (DOCTORED, 0),  # final call: unload qwen
    ]
    for row, keep_alive in cases:
        print(f"\n=== {row['id']} ===")
        print(f"sentence: {row['sentence']}")
        user_msg = _run.build_user_prompt(row, MARKERS)
        res = classify(
            model=MODEL,
            system=SYSTEM,
            user=user_msg,
            schema=_run.SCHEMA,
            temperature=0.0,
            keep_alive=keep_alive,
        )
        print(f"ok={res.ok}  latency={res.latency_ms:.0f}ms")
        if res.ok:
            print(f"label: {res.payload.get('label')}")
            print(f"reasoning: {res.payload.get('reasoning')}")
        else:
            print(f"error: {res.error}")
            offset = parse_offset(res.error)
            show_raw_around(res.raw_content, offset)
    return 0


if __name__ == "__main__":
    sys.exit(main())
