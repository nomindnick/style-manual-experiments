"""Tests for LS-SP-02 (two spaces between sentences).

Run from the repo root:
    .venv/bin/python rules/01-two-spaces/test_rule.py

Two test layers:

1. Synthetic positives/negatives — single-paragraph fixtures that exercise the
   suppression logic (citation spans, abbreviations, ellipses, initials).
2. Integration — the three real .docx fixtures under fixtures/. Asserts that
   the LS-SP-02 violations recorded in each fixture's *.violations.json sidecar
   are flagged at the expected paragraph index, and that no other paragraphs
   produce LS-SP-02 findings.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make repo root importable when this file is run directly.
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from shared.document import Document  # noqa: E402
from shared.finding import Finding  # noqa: E402

from rule import TwoSpacesBetweenSentencesRule  # noqa: E402


def _para_indices(findings: list[Finding]) -> list[int]:
    return sorted(f.location.paragraph_index for f in findings)


def _check_text(text: str) -> list[Finding]:
    return TwoSpacesBetweenSentencesRule().check(Document.from_text(text))


# ---------- Synthetic positive cases ----------

def test_simple_single_space_between_sentences():
    findings = _check_text("First sentence. Second sentence.")
    assert len(findings) == 1, findings
    assert findings[0].rule_id == "LS-SP-02"
    assert findings[0].severity == "error"


def test_single_space_after_citation_sentence():
    # Real pattern from kitchen-sink ¶43.
    text = (
        "Statement of facts here.  "
        "(Blank v. Kirwan (1985) 39 Cal.3d 311, 318.) "
        "The District does not accept contentions."
    )
    findings = _check_text(text)
    # Only the `318.) The` boundary should fire — the prior `here.  (` is
    # already two-spaced.
    assert len(findings) == 1, [f.snippet for f in findings]
    assert "318.) The" in findings[0].snippet


def test_single_space_question_mark():
    findings = _check_text("Is this so? Yes it is.")
    assert len(findings) == 1


def test_single_space_exclamation():
    findings = _check_text("Look at that! Now consider this.")
    assert len(findings) == 1


def test_four_dot_ellipsis_end_of_sentence():
    findings = _check_text("She trailed off.... Then she resumed.")
    assert len(findings) == 1, findings


# ---------- Synthetic negative cases (must NOT fire) ----------

def test_two_spaces_between_sentences():
    assert _check_text("First sentence.  Second sentence.") == []


def test_three_dot_ellipsis_midsentence():
    # `...` followed by a capital is mid-sentence per LS-SP-03; not a boundary.
    assert _check_text("She said... And then she paused.") == []


def test_legal_token_internal_period_cal_app():
    # Cal.App.4th has internal periods; eyecite span suppresses them.
    text = "See 186 Cal.App.4th 1298, 1305 for the rule. (Some other context.)"
    # The `1305 for` and `(Some` boundaries are not at single-space-then-capital.
    # Only check that nothing fires from the Cal.App. internal periods.
    findings = _check_text(text)
    # The trailing period before `(Some` is two-spaced ("rule.  (")? No — the
    # text above has one space. So `rule. (` IS a single-space candidate. Let
    # me make this test specific to the Cal.App. suppression itself.
    # Re-author with a clean two-space afterwards:
    text2 = "Citing 186 Cal.App.4th 1298, the court ruled."
    assert _check_text(text2) == []


def test_us_reporter_internal_period():
    # `U.S.` has two internal periods; not sentence boundaries.
    text = "The court in 556 U.S. 662 held that things were so."
    assert _check_text(text) == []


def test_versus_in_case_name():
    # `Smith v. Jones` — `v.` followed by capital. Must not fire.
    text = "Citing Smith v. Jones for the proposition that things are so."
    assert _check_text(text) == []


def test_inc_in_case_name():
    # `Acme, Inc. v. Foo` — Inc. followed by space + lowercase v. The candidate
    # requires a capital, so this won't even match. Try the year-paren form:
    text = "Acme, Inc. (1990) 12 Cal.3d 100 controls. Next sentence."
    findings = _check_text(text)
    # Only the `controls.` boundary (single space + N) should fire.
    assert len(findings) == 1, [f.snippet for f in findings]
    assert "controls. Next" in findings[0].snippet


def test_code_name_leaders():
    # Pub. Cont. Code, Ed. Code, Civ. Code, Gov. Code — every dot is followed
    # by a capital. None should fire.
    text = (
        "Cited authorities include Pub. Cont. Code section 20118.4, "
        "Ed. Code section 17604, Civ. Code section 1550, and "
        "Gov. Code section 815."
    )
    assert _check_text(text) == []


def test_subdivision_abbreviation():
    text = "See section 430.10, subd. (e), and the related provisions."
    assert _check_text(text) == []


def test_id_and_ibid():
    # `(Id. at p. 318.)` and `(Ibid.)` — internal `Id.` and `Ibid.` should
    # not fire as boundaries.
    text = "The court so held. (Id. at p. 318.) The same point appears later."
    findings = _check_text(text)
    # Two boundaries are real here:
    #   "held. ("   single space + `(` -> violation
    #   "318.) The" single space + `T` -> violation
    # `Id. at` is suppressed because `id` is an abbreviation; `at` is lowercase
    # anyway, so the candidate would not have matched.
    para_snips = [f.snippet for f in findings]
    assert any("held. (" in s for s in para_snips), para_snips
    assert any("318.) The" in s for s in para_snips), para_snips
    assert len(findings) == 2


def test_single_letter_initial():
    # `Margaret A. Delacroix` and `G.L. Mezzetta` have initials that look like
    # sentence terminators followed by capitals.
    text = (
        "The declaration of Margaret A. Delacroix is filed concurrently. "
        "Citing G.L. Mezzetta, Inc. (2000) 78 Cal.App.4th 1087."
    )
    findings = _check_text(text)
    # Only the `concurrently. Citing` boundary should fire.
    assert len(findings) == 1, [f.snippet for f in findings]
    assert "concurrently. Citing" in findings[0].snippet


def test_two_spaces_before_open_paren():
    # `prose.  (Cite.)` is the LS pattern; must not fire.
    text = "The court held in three cases.  (Smith v. Jones, supra.)"
    assert _check_text(text) == []


# ---------- Integration: real fixtures ----------

def _expected_lssp02_paragraphs(violations_json: Path) -> list[int]:
    data = json.loads(violations_json.read_text())
    return sorted(
        v["paragraph_index"]
        for v in data["violations"]
        if v["rule_id"] == "LS-SP-02"
    )


def test_clean_fixture_no_findings():
    doc = Document.load(_REPO_ROOT / "fixtures" / "clean.docx")
    findings = TwoSpacesBetweenSentencesRule().check(doc)
    assert findings == [], [
        (f.location.paragraph_index, f.snippet) for f in findings
    ]


def test_kitchen_sink_fixture():
    doc = Document.load(_REPO_ROOT / "fixtures" / "kitchen-sink-violations.docx")
    findings = TwoSpacesBetweenSentencesRule().check(doc)
    expected = _expected_lssp02_paragraphs(
        _REPO_ROOT / "fixtures" / "kitchen-sink-violations.violations.json"
    )
    actual = _para_indices(findings)
    assert actual == expected, (actual, expected, [
        (f.location.paragraph_index, f.snippet) for f in findings
    ])


def test_realistic_mixed_fixture():
    doc = Document.load(_REPO_ROOT / "fixtures" / "realistic-mixed.docx")
    findings = TwoSpacesBetweenSentencesRule().check(doc)
    expected = _expected_lssp02_paragraphs(
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
        test_simple_single_space_between_sentences,
        test_single_space_after_citation_sentence,
        test_single_space_question_mark,
        test_single_space_exclamation,
        test_four_dot_ellipsis_end_of_sentence,
        # synthetic negatives
        test_two_spaces_between_sentences,
        test_three_dot_ellipsis_midsentence,
        test_legal_token_internal_period_cal_app,
        test_us_reporter_internal_period,
        test_versus_in_case_name,
        test_inc_in_case_name,
        test_code_name_leaders,
        test_subdivision_abbreviation,
        test_id_and_ibid,
        test_single_letter_initial,
        test_two_spaces_before_open_paren,
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
