"""Tests for LS-CITE-02 (section symbol placement).

Run from the repo root:
    .venv/bin/python rules/02-section-symbol/test_rule.py

Two test layers:

1. Synthetic positives/negatives — single-paragraph fixtures that exercise the
   inside-parens / outside-parens split, the plural `§§` / `sections` forms,
   nested parens, brackets, and the statute-number precision gate.
2. Integration — the three real .docx fixtures under fixtures/. Asserts that
   the LS-CITE-02 violations recorded in each fixture's *.violations.json
   sidecar are flagged at the expected paragraph index, and that no other
   paragraphs produce LS-CITE-02 findings.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from shared.document import Document  # noqa: E402
from shared.finding import Finding  # noqa: E402

from rule import SectionSymbolPlacementRule  # noqa: E402


def _para_indices(findings: list[Finding]) -> list[int]:
    return sorted(f.location.paragraph_index for f in findings)


def _check_text(text: str) -> list[Finding]:
    return SectionSymbolPlacementRule().check(Document.from_text(text))


# ---------- Synthetic positives (must fire) ----------

def test_section_symbol_in_running_prose():
    findings = _check_text("Public Contract Code § 20118.4 governs change orders.")
    assert len(findings) == 1, findings
    f = findings[0]
    assert f.rule_id == "LS-CITE-02"
    assert f.severity == "error"
    assert f.suggested_fix == "section"


def test_double_section_symbol_in_running_prose():
    findings = _check_text("Education Code §§ 17604 and 17605 govern board approval.")
    assert len(findings) == 1, findings
    assert findings[0].suggested_fix == "sections"


def test_section_word_inside_parens():
    findings = _check_text("The rule is clear.  (Pub. Cont. Code, section 20118.4.)")
    assert len(findings) == 1, findings
    assert findings[0].suggested_fix == "§"


def test_sections_word_inside_parens():
    findings = _check_text(
        "The rule is clear.  (Ed. Code, sections 17604 and 17605.)"
    )
    assert len(findings) == 1, findings
    assert findings[0].suggested_fix == "§§"


def test_section_word_inside_nested_parens():
    # "section" at depth 2 (inside a citation sentence's bracketed sub-ref).
    # LS convention is brackets for sub-references inside citation sentences
    # (LS-CITE-15). Still inside-parens for rule-2 purposes.
    findings = _check_text(
        "See the quoted clause.  (Contract [section 9.1 of General Conditions].)"
    )
    assert len(findings) == 1, findings
    assert findings[0].suggested_fix == "§"


def test_section_symbol_outside_then_valid_inside():
    # One violation (the outside `§`), not two.
    text = (
        "Public Contract Code § 20118.4 governs change orders.  "
        "(See Pub. Cont. Code, § 20118.4.)"
    )
    findings = _check_text(text)
    assert len(findings) == 1, [f.snippet for f in findings]
    assert findings[0].suggested_fix == "section"


def test_valid_outside_then_section_word_inside():
    # One violation (the inside "section"), not two.
    text = (
        "Public Contract Code section 20118.4 reinforces the principle.  "
        "(Pub. Cont. Code, section 20118.4, subd. (a).)"
    )
    findings = _check_text(text)
    assert len(findings) == 1, [f.snippet for f in findings]
    assert findings[0].suggested_fix == "§"


# ---------- Synthetic negatives (must NOT fire) ----------

def test_section_symbol_inside_parens_valid():
    text = "The statute controls.  (Pub. Cont. Code, § 20118.4.)"
    assert _check_text(text) == []


def test_double_section_symbol_inside_parens_valid():
    text = "The statute controls.  (Ed. Code, §§ 17604, 17605.)"
    assert _check_text(text) == []


def test_section_word_outside_parens_valid():
    text = "Public Contract Code section 20118.4 requires a written change order."
    assert _check_text(text) == []


def test_sections_word_outside_parens_valid():
    text = "Education Code sections 17604 and 17605 require board approval."
    assert _check_text(text) == []


def test_section_followed_by_roman_numeral_not_flagged():
    # "Section IV" is a document-structural reference, not a statute.
    text = "As shown in (Section IV of this brief) the Court should rule accordingly."
    assert _check_text(text) == []


def test_section_followed_by_letter_not_flagged():
    # "Section A" — not a statute number shape.
    text = "Refer to (Section A for details) in the appendix."
    assert _check_text(text) == []


def test_generic_section_word_not_flagged():
    # "this section of" — no digit follows; precision gate skips.
    text = "Consider (this section of the Code, which governs change orders)."
    assert _check_text(text) == []


def test_section_symbol_inside_brackets_valid():
    # Real pattern from clean.docx ¶31: `[General Conditions, § 9.1]` appears
    # inside a parenthetical citation; `§` is at depth 2. Must not fire.
    text = (
        "The clause is clear.  "
        "(Compl., Ex. A [General Conditions, § 9.1].)"
    )
    assert _check_text(text) == []


def test_section_symbol_inside_brackets_alone_valid():
    # Even if brackets stand alone (no surrounding parens), treat as "inside".
    # This is the cheap-insurance call documented in rule.py.
    text = "The provision reads [General Conditions, § 9.1] clearly."
    assert _check_text(text) == []


def test_subd_abbreviation_is_not_our_rule():
    # LS-CITE-03 handles `subd.` vs `subdivision`. Our rule must not fire on
    # either the `subd.` token or its expansion.
    text = "The statute controls.  (Pub. Cont. Code, § 20118.4, subd. (a).)"
    assert _check_text(text) == []


def test_paragraph_symbol_is_not_our_rule():
    # LS-CITE-02a covers `¶` / "paragraph". Our rule must ignore `¶` entirely.
    text = "The complaint alleges facts.  (Compl., ¶¶ 6–8.)"
    assert _check_text(text) == []


# ---------- Integration: real fixtures ----------

def _expected_paragraphs(violations_json: Path) -> list[int]:
    data = json.loads(violations_json.read_text())
    return sorted(
        v["paragraph_index"]
        for v in data["violations"]
        if v["rule_id"] == "LS-CITE-02"
    )


def test_clean_fixture_no_findings():
    doc = Document.load(_REPO_ROOT / "fixtures" / "clean.docx")
    findings = SectionSymbolPlacementRule().check(doc)
    assert findings == [], [
        (f.location.paragraph_index, f.snippet) for f in findings
    ]


def test_kitchen_sink_fixture():
    doc = Document.load(_REPO_ROOT / "fixtures" / "kitchen-sink-violations.docx")
    findings = SectionSymbolPlacementRule().check(doc)
    expected = _expected_paragraphs(
        _REPO_ROOT / "fixtures" / "kitchen-sink-violations.violations.json"
    )
    actual = _para_indices(findings)
    assert actual == expected, (actual, expected, [
        (f.location.paragraph_index, f.snippet) for f in findings
    ])


def test_realistic_mixed_fixture():
    doc = Document.load(_REPO_ROOT / "fixtures" / "realistic-mixed.docx")
    findings = SectionSymbolPlacementRule().check(doc)
    expected = _expected_paragraphs(
        _REPO_ROOT / "fixtures" / "realistic-mixed.violations.json"
    )
    actual = _para_indices(findings)
    assert actual == expected, (actual, expected, [
        (f.location.paragraph_index, f.snippet) for f in findings
    ])


# ---------- Test runner ----------

def main() -> int:
    tests = [
        # synthetic positives
        test_section_symbol_in_running_prose,
        test_double_section_symbol_in_running_prose,
        test_section_word_inside_parens,
        test_sections_word_inside_parens,
        test_section_word_inside_nested_parens,
        test_section_symbol_outside_then_valid_inside,
        test_valid_outside_then_section_word_inside,
        # synthetic negatives
        test_section_symbol_inside_parens_valid,
        test_double_section_symbol_inside_parens_valid,
        test_section_word_outside_parens_valid,
        test_sections_word_outside_parens_valid,
        test_section_followed_by_roman_numeral_not_flagged,
        test_section_followed_by_letter_not_flagged,
        test_generic_section_word_not_flagged,
        test_section_symbol_inside_brackets_valid,
        test_section_symbol_inside_brackets_alone_valid,
        test_subd_abbreviation_is_not_our_rule,
        test_paragraph_symbol_is_not_our_rule,
        # integration
        test_clean_fixture_no_findings,
        test_kitchen_sink_fixture,
        test_realistic_mixed_fixture,
    ]
    failed: list[tuple[str, BaseException]] = []
    for t in tests:
        try:
            t()
            print(f"  ok    {t.__name__}")
        except BaseException as e:  # noqa: BLE001
            failed.append((t.__name__, e))
            print(f"  FAIL  {t.__name__}  -> {e}")
    if failed:
        print(f"\n{len(failed)} of {len(tests)} test(s) failed.")
        return 1
    print(f"\n{len(tests)} tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
