"""Adapter over eyecite returning per-paragraph citation spans.

Why this exists: most rules don't care about parsed citation metadata — they
just need to know "is this stretch of text inside a citation?" so they can
suppress false positives on legal-abbreviation tokens (`Cal.App.4th`, `U.S.`,
`F.3d`, etc.). Going through eyecite for that question, rather than maintaining
a parallel regex, keeps the two views consistent.

Scope (Phase 1): a single function `citation_spans(document)` returning
`list[CitationSpan]`. Caching lives on the Document via lru_cache — eyecite
parsing isn't free, and Rule 1 plus future rules will all hit the same text.

What a span covers: the literal substring eyecite recognized as the citation
token (volume + reporter + page, plus "at PIN" for short cites). It does NOT
extend to the trailing pin-cite period, year-paren, or closing paren — those
sit outside the span and remain visible to sentence-boundary detection, which
is the behavior LS-SP-02 wants.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from eyecite import get_citations

from shared.document import Document


# Map eyecite class names to the small vocabulary rules will branch on.
# Anything not in the map falls through to the lowercased class name; rules
# should treat unknown kinds as "some kind of citation, suppress conservatively."
_KIND_BY_TYPE_NAME: dict[str, str] = {
    "FullCaseCitation": "case-full",
    "ShortCaseCitation": "case-short",
    "IdCitation": "id",
    "SupraCitation": "supra",
    "FullLawCitation": "law",
    "ShortLawCitation": "law",
    "FullJournalCitation": "journal",
    "UnknownCitation": "unknown",
}


@dataclass(frozen=True)
class CitationSpan:
    paragraph_index: int
    char_start: int
    char_end: int
    kind: str

    def contains(self, offset: int) -> bool:
        """True if `offset` falls within [char_start, char_end)."""
        return self.char_start <= offset < self.char_end


def citation_spans(document: Document) -> list[CitationSpan]:
    """Return citation spans for every paragraph in the document.

    Cached per-Document; safe to call repeatedly from multiple rules.
    """
    return _cached_spans(id(document), document)


@lru_cache(maxsize=None)
def _cached_spans(_doc_id: int, document: Document) -> list[CitationSpan]:
    spans: list[CitationSpan] = []
    for para in document.paragraphs:
        text = para.text
        if not text:
            continue
        for cite in get_citations(text):
            start, end = cite.span()
            kind = _KIND_BY_TYPE_NAME.get(
                type(cite).__name__, type(cite).__name__.lower()
            )
            spans.append(
                CitationSpan(
                    paragraph_index=para.index,
                    char_start=start,
                    char_end=end,
                    kind=kind,
                )
            )
    return spans
