"""The Finding type — the common contract every rule emits.

A Finding is a JSON-serializable record describing one instance of a style-manual
violation or concern. Every renderer (plain-text report, eventual HTML, future
docx-comment emitter) consumes Finding objects.

Schema: see PLAN.md. Treat the shape here as authoritative; update PLAN.md if
this changes.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Severity = Literal["error", "warning", "info"]


@dataclass
class Location:
    """Where in the document the finding occurred.

    `paragraph_index` is the 0-based index into the document's paragraph list.
    `char_start` / `char_end` are offsets *within* that paragraph's text.
    Rules that don't have a meaningful character range (e.g., document-level
    font rules) may set both to 0 and leave `paragraph_index` as the target.
    """

    paragraph_index: int
    char_start: int = 0
    char_end: int = 0


@dataclass
class Finding:
    rule_id: str
    severity: Severity
    manual_section: str
    location: Location
    snippet: str
    message: str
    suggested_fix: str | None = None
    confidence: float | None = None
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, **json_kwargs: Any) -> str:
        return json.dumps(self.to_dict(), **json_kwargs)
