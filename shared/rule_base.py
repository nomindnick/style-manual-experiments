"""The Rule interface.

Every rule is a class that subclasses Rule and implements `check()`. Rules are
the unit of work: small, self-contained, each in its own subdirectory under
`rules/`.

Design notes:
  - Rules are classes (not bare functions) so they can hold config, pre-compiled
    regexes, or model handles without recreating on every check call.
  - Rules declare their id, name, manual section, and tier as class attributes
    so the catalog stays in sync with the code.
  - `check()` returns a list of Findings. Empty list means the rule passed.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Literal

from shared.document import Document
from shared.finding import Finding

Tier = Literal[1, 2, 3, 4]


class Rule(ABC):
    """Base class for all style-manual rules."""

    # Class attributes — set on every concrete subclass.
    rule_id: ClassVar[str]
    name: ClassVar[str]
    manual_section: ClassVar[str]  # human-readable, e.g., "Capitalization §2 (p. 6)"
    tier: ClassVar[Tier]

    @abstractmethod
    def check(self, document: Document) -> list[Finding]:
        """Inspect the document and return any findings.

        Rules should not raise on expected input shapes. Unexpected errors (a
        required dependency down, a malformed doc) may raise; the engine will
        catch and surface them as run-level diagnostics rather than crashing.
        """


def run_rules(rules: list[Rule], document: Document) -> list[Finding]:
    """Run a sequence of rules over a document and collect findings.

    Rules run in list order. Later phases may add parallelism or skip-on-error
    behavior; for now, exceptions propagate so they are visible in development.
    """
    findings: list[Finding] = []
    for rule in rules:
        findings.extend(rule.check(document))
    return findings
