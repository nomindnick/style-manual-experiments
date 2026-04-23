"""LS-CITE-02 — Section symbol placement.

The manual's rule is a clean split keyed on context:

  * **Inside parens:** the section symbol `§` (or `§§` for multiple sections).
  * **Outside parens (running prose):** the word "section" (or "sections").

So the rule fires in two directions:

  1. Any `§` / `§§` at paren-depth 0 is a violation (fix → "section" / "sections").
  2. Any `section` / `sections` at paren-depth > 0, when followed by a
     statute-number-shaped token (digits, optionally dotted), is a violation
     (fix → `§` / `§§`).

The statute-number gate on direction 2 is the precision knob. It keeps the rule
from firing on document-structural references like "Section IV of this brief"
or generic prose like "this section of the code" — neither of which involve a
statute cite. Direction 1 has no comparable gate because `§` is unambiguous;
any out-of-parens occurrence is either the LS violation or a deliberate federal
deviation (see NOTES.md).

Paren-depth is tracked per paragraph with a one-pass scan that counts `(`/`[`
as openers and `)`/`]` as closers. Brackets participate because LS uses them
for sub-references inside citation sentences (e.g.,
`(Compl., Ex. A [General Conditions, § 9.1].)`), and the `§` in such a
sub-reference is still "inside parens" for rule-2 purposes.

Court-type note: federal filings permit `§` in substantive sentences (per the
CATALOG note on LS-CITE-02). This implementation assumes CA state practice —
matching the Phase-0.5 fixtures. Flip the behavior when court_context plumbing
lands (PLAN open question #6).

Helper scope: `_paren_depth_before` is local to this rule for now. When
LS-CITE-03 (subdivision / subd.) lands it will want the same split; promote
to `shared/` at that point, not before.
"""

from __future__ import annotations

import re
from typing import ClassVar

from shared.document import Document
from shared.finding import Finding, Location
from shared.rule_base import Rule


# `§` or `§§` (or a longer run, though `§§§+` is not a real LS shape).
_SECTION_SYMBOL_RE = re.compile(r"§+")

# Word form of "section"/"sections", case-insensitive, requiring a following
# statute-number-shaped token so document-structural references ("Section IV")
# and generic prose ("this section of the code") don't match.
_SECTION_WORD_RE = re.compile(
    r"\b(sections?)\b(?=\s+\d)",
    re.IGNORECASE,
)


class SectionSymbolPlacementRule(Rule):
    rule_id: ClassVar[str] = "LS-CITE-02"
    name: ClassVar[str] = "Section symbol placement"
    manual_section: ClassVar[str] = "Citations §2 (p. 16)"
    tier: ClassVar[int] = 3

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []

        for para in document.paragraphs:
            text = para.text
            if not text or ("§" not in text and not _has_section_word(text)):
                continue

            depth_before = _paren_depth_array(text)

            # Direction 1: `§` / `§§` at depth 0 → violation.
            for m in _SECTION_SYMBOL_RE.finditer(text):
                if depth_before[m.start()] != 0:
                    continue
                run_len = m.end() - m.start()
                fix = "sections" if run_len >= 2 else "section"
                symbol = "§" * run_len
                findings.append(
                    _make_finding(
                        rule_id=self.rule_id,
                        manual_section=self.manual_section,
                        paragraph_index=para.index,
                        text=text,
                        char_start=m.start(),
                        char_end=m.end(),
                        message=(
                            f"Section symbol '{symbol}' used in running prose "
                            "outside parentheses; LS Manual requires the word "
                            f"'{fix}' spelled out when not inside parens."
                        ),
                        suggested_fix=fix,
                    )
                )

            # Direction 2: `section` / `sections` at depth > 0 → violation.
            for m in _SECTION_WORD_RE.finditer(text):
                if depth_before[m.start()] == 0:
                    continue
                word = m.group(1)
                fix = "§§" if word.lower() == "sections" else "§"
                findings.append(
                    _make_finding(
                        rule_id=self.rule_id,
                        manual_section=self.manual_section,
                        paragraph_index=para.index,
                        text=text,
                        char_start=m.start(),
                        char_end=m.end(),
                        message=(
                            f"The word '{word}' used inside parentheses; LS "
                            f"Manual requires the section symbol '{fix}' "
                            "inside parens."
                        ),
                        suggested_fix=fix,
                    )
                )

        findings.sort(key=lambda f: (f.location.paragraph_index, f.location.char_start))
        return findings


def _has_section_word(text: str) -> bool:
    """Cheap filter: skip paragraphs with no candidate 'section' tokens."""
    return _SECTION_WORD_RE.search(text) is not None


def _paren_depth_array(text: str) -> list[int]:
    """Return a list where `depth[i]` is the paren depth *before* position `i`.

    Treats `(` and `[` as openers, `)` and `]` as closers. Depth is clamped at
    zero so a stray closer doesn't produce negative values — a defensive choice;
    malformed paragraphs shouldn't crash the rule.
    """
    depth = 0
    out = [0] * (len(text) + 1)
    for i, c in enumerate(text):
        out[i] = depth
        if c == "(" or c == "[":
            depth += 1
        elif c == ")" or c == "]":
            if depth > 0:
                depth -= 1
    out[len(text)] = depth
    return out


def _make_finding(
    *,
    rule_id: str,
    manual_section: str,
    paragraph_index: int,
    text: str,
    char_start: int,
    char_end: int,
    message: str,
    suggested_fix: str,
) -> Finding:
    snippet_start = max(0, char_start - 20)
    snippet_end = min(len(text), char_end + 20)
    return Finding(
        rule_id=rule_id,
        severity="error",
        manual_section=manual_section,
        location=Location(
            paragraph_index=paragraph_index,
            char_start=char_start,
            char_end=char_end,
        ),
        snippet=text[snippet_start:snippet_end],
        message=message,
        suggested_fix=suggested_fix,
    )
