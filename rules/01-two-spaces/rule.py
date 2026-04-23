"""LS-SP-02 — Two spaces between every sentence (incl. citation sentences).

The rule scans each paragraph for "single space between sentences" patterns and
emits a Finding for each one. The hard part is *not* the spacing check; it is
distinguishing real sentence boundaries from the sea of period-bearing tokens
in a litigation filing — `Cal.App.4th`, `U.S.`, `F.3d`, `Inc.`, `v.`, `Ed.`,
`subd.`, single-letter initials, and so on.

Suppression strategy, in this order:

1. Eyecite citation spans suppress periods that fall *inside* a recognized
   citation token (most legal-abbreviation false positives live here).
2. A small abbreviation list catches what eyecite leaves on the table —
   honorifics, Latin connectors (`v.`), entity suffixes (`Inc.`), CA
   code-name leaders (`Gov.`, `Pub.`, `Cont.`, `Civ.`, `Ed.`), citation glue
   (`subd.`, `art.`), and party-name initials.
3. Three-dot ellipsis (`...`) is treated as mid-sentence per LS-SP-03;
   four-dot ellipsis (`....`) is end-of-sentence and remains in scope.

This is a starter list — additions go here as fixtures surface them.
"""

from __future__ import annotations

import re
from typing import ClassVar

from shared.document import Document
from shared.eyecite_wrapper import CitationSpan, citation_spans
from shared.finding import Finding, Location
from shared.rule_base import Rule


# Tokens that, ending in a period at a candidate sentence boundary, are
# abbreviations rather than terminators. Stored without the trailing period;
# comparison is case-insensitive.
_ABBREVIATIONS: frozenset[str] = frozenset(
    {
        # Honorifics
        "mr", "mrs", "ms", "dr", "hon", "prof", "rev", "esq", "sr", "jr",
        # Latin / connectors that pair with capitals
        "v", "vs", "cf", "viz",
        # Entity suffixes (frequent in case names)
        "inc", "corp", "co", "ltd", "bros", "mfg", "assn",
        # CA code-name leaders eyecite doesn't tag
        "cal", "gov", "pub", "cont", "civ", "proc", "penal", "ed", "bus",
        "prof", "lab", "ins", "fam", "welf", "educ", "health", "safety",
        "fin", "comm",
        # Court / reporter abbrevs
        "super", "ct", "app", "dist", "bd", "bds", "reg", "regs", "mun",
        "com",  # commission ("State Lottery Com.")
        # Citation-internal glue
        "subd", "subds", "art", "ch", "sec", "secs", "vol", "p", "pp",
        "no", "nos", "id", "ibid",
        # Months — usually digit-followed but defensive
        "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sept", "sep",
        "oct", "nov", "dec",
        # Misc
        "ex", "exh", "exs",
        # Tail of multi-word abbreviations: "et al." preceded by a comma in
        # case names, "et seq." inside statute citations.
        "al", "seq",
    }
)


# Candidate sentence-boundary regex.
#
# Matches: terminator + optional close-quote/paren + EXACTLY one space +
# lookahead for a sentence-opener (capital letter or open-quote/paren).
#
# By construction, this matches only the violation pattern — two spaces
# would put a non-opener at the lookahead position and the lookahead fails.
_BOUNDARY_RE = re.compile(
    r"[.!?]"                                    # terminal punctuation
    r"[\"\)\]’”]?"                    # optional closer
    r" "                                        # one literal space (the violation)
    r"(?=[A-Z\"\(\[“‘])"              # next char starts a sentence
)

# Last word of letters in a string — used to look up the abbreviation table.
_PRECEDING_WORD_RE = re.compile(r"([A-Za-z]+)$")


class TwoSpacesBetweenSentencesRule(Rule):
    rule_id: ClassVar[str] = "LS-SP-02"
    name: ClassVar[str] = "Two spaces between sentences"
    manual_section: ClassVar[str] = "Spacing §2 (p. 10)"
    tier: ClassVar[int] = 1

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []

        spans_by_para: dict[int, list[CitationSpan]] = {}
        for s in citation_spans(document):
            spans_by_para.setdefault(s.paragraph_index, []).append(s)

        for para in document.paragraphs:
            text = para.text
            if not text:
                continue
            spans = spans_by_para.get(para.index, ())

            for m in _BOUNDARY_RE.finditer(text):
                term_pos = m.start()  # position of the terminal punctuation

                if any(s.contains(term_pos) for s in spans):
                    continue
                if _is_three_dot_ellipsis(text, term_pos):
                    continue
                if _preceding_token_is_abbreviation(text, term_pos):
                    continue

                space_pos = m.end() - 1  # index of the lone space
                snippet_start = max(0, term_pos - 20)
                snippet_end = min(len(text), m.end() + 20)
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity="error",
                        manual_section=self.manual_section,
                        location=Location(
                            paragraph_index=para.index,
                            char_start=space_pos,
                            char_end=space_pos + 1,
                        ),
                        snippet=text[snippet_start:snippet_end],
                        message=(
                            "Single space between sentences; "
                            "LS Manual requires two spaces."
                        ),
                        suggested_fix="  ",
                    )
                )

        return findings


def _is_three_dot_ellipsis(text: str, period_pos: int) -> bool:
    """True iff `period_pos` lies in a run of exactly three consecutive dots.

    LS-SP-03 treats `...` as a mid-sentence ellipsis (not a terminator) and
    `....` as end-of-sentence (a terminator). Only the three-dot case is
    suppressed here.
    """
    if text[period_pos] != ".":
        return False
    start = period_pos
    while start > 0 and text[start - 1] == ".":
        start -= 1
    end = period_pos + 1
    while end < len(text) and text[end] == ".":
        end += 1
    return (end - start) == 3


def _preceding_token_is_abbreviation(text: str, period_pos: int) -> bool:
    """True iff the alphabetic token ending at `period_pos` is an abbreviation
    or a single-capital-letter initial (`A.`, `J.`, `L.`).
    """
    m = _PRECEDING_WORD_RE.search(text[:period_pos])
    if not m:
        return False
    word = m.group(1)
    if word.lower() in _ABBREVIATIONS:
        return True
    if len(word) == 1 and word.isupper():
        return True
    return False
