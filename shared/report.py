"""Plain-text report renderer.

Consumes a list[Finding] and produces a human-readable report. HTML renderer
comes in Phase 2; both consume the same Finding shape.
"""

from __future__ import annotations

from collections import defaultdict

from shared.finding import Finding

_SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}
_SEVERITY_MARK = {"error": "[!]", "warning": "[?]", "info": "[i]"}


def render_text(findings: list[Finding], *, document_name: str | None = None) -> str:
    """Render findings as a plain-text report.

    Groups by rule_id and sorts within each group by document location.
    """
    lines: list[str] = []
    header = "LS Style Manual Review"
    if document_name:
        header += f" — {document_name}"
    lines.append(header)
    lines.append("=" * len(header))
    lines.append("")

    if not findings:
        lines.append("No findings. Document passed all checks run.")
        return "\n".join(lines)

    by_severity: dict[str, int] = defaultdict(int)
    for f in findings:
        by_severity[f.severity] += 1
    summary = ", ".join(
        f"{by_severity[s]} {s}" for s in ("error", "warning", "info") if by_severity[s]
    )
    lines.append(f"Summary: {len(findings)} finding(s) — {summary}")
    lines.append("")

    # Group by rule_id so the report reads by concern, not by position.
    by_rule: dict[str, list[Finding]] = defaultdict(list)
    for f in findings:
        by_rule[f.rule_id].append(f)

    # Sort rule groups by worst-severity then rule_id.
    def _group_sort_key(item: tuple[str, list[Finding]]) -> tuple[int, str]:
        rule_id, group = item
        worst = min(_SEVERITY_ORDER[f.severity] for f in group)
        return (worst, rule_id)

    for rule_id, group in sorted(by_rule.items(), key=_group_sort_key):
        # Sort findings within group by document position.
        group.sort(key=lambda f: (f.location.paragraph_index, f.location.char_start))
        head = group[0]
        lines.append(f"── {rule_id} — {head.manual_section}")
        for f in group:
            mark = _SEVERITY_MARK.get(f.severity, "[?]")
            loc = f"¶{f.location.paragraph_index}"
            if f.location.char_end > f.location.char_start:
                loc += f" [{f.location.char_start}:{f.location.char_end}]"
            lines.append(f"  {mark} {loc}  {f.message}")
            if f.snippet:
                lines.append(f"       “{f.snippet}”")
            if f.suggested_fix:
                lines.append(f"       → suggested: {f.suggested_fix}")
            if f.confidence is not None:
                lines.append(f"       confidence: {f.confidence:.2f}")
        lines.append("")

    return "\n".join(lines)
