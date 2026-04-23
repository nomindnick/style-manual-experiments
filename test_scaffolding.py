"""End-to-end smoke test for the shared/ scaffolding.

Builds a synthetic document, runs a trivial fake rule that always fires, and
checks that the text report renders. This is deliberately not a real rule
test — it exists so we notice when the plumbing between Document, Rule,
Finding, and the report renderer stops connecting.

Run from the repo root with:
    .venv/bin/python test_scaffolding.py
"""

from __future__ import annotations

import json

from shared.document import Document
from shared.finding import Finding, Location
from shared.report import render_text
from shared.rule_base import Rule, run_rules


class _AlwaysFiresRule(Rule):
    """Emits a finding on any paragraph containing the letter 'a'.

    Exists solely to verify the scaffolding end-to-end. Not a real rule; will
    be deleted once Rule 1 (LS-SP-02) ships and the smoke test is replaced.
    """

    rule_id = "LS-TEST-00"
    name = "Always-fires sentinel (scaffolding smoke test)"
    manual_section = "(none — test fixture)"
    tier = 1

    def check(self, document: Document) -> list[Finding]:
        findings: list[Finding] = []
        for p in document.paragraphs:
            idx = p.text.find("a")
            if idx >= 0:
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity="info",
                        manual_section=self.manual_section,
                        location=Location(p.index, idx, idx + 1),
                        snippet=p.text[max(0, idx - 10) : idx + 11],
                        message="Sentinel rule matched the letter 'a'.",
                        suggested_fix=None,
                    )
                )
        return findings


def main() -> int:
    doc = Document.from_text(
        "This is a sample paragraph.\n"
        "No hits on this line.\n"
        "Another line with multiple aaa characters."
    )
    findings = run_rules([_AlwaysFiresRule()], doc)

    # Structural assertions — if any of these fail, the plumbing is wrong.
    assert len(findings) == 2, f"expected 2 findings, got {len(findings)}"
    assert findings[0].rule_id == "LS-TEST-00"
    assert findings[0].location.paragraph_index == 0
    assert findings[1].location.paragraph_index == 2

    # Finding must round-trip to JSON.
    payload = findings[0].to_dict()
    json.dumps(payload)  # will raise if non-serializable

    # Report must render without error.
    report = render_text(findings, document_name="scaffolding-smoke")
    assert "LS-TEST-00" in report
    assert "sample" in report or "Another" in report

    # Passing: print the report so the output is visible when run manually.
    print(report)
    print("\n--- scaffolding smoke test: OK ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
