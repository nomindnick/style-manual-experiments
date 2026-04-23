# LS-SP-02 — implementation notes

**Manual section:** Spacing §2 (p. 10)
**Tier:** 1 (regex / pure-text, with eyecite-span suppression)

## What the rule does

Walks every paragraph for the pattern `<terminator><optional close> <single space> <capital-or-opener>` and emits a Finding for each match — i.e., wherever the writer used one space between sentences instead of two. The hard work is suppression of false positives.

## Suppression layers

1. **Eyecite citation spans.** Periods inside a recognized citation token (`Cal.App.4th`, `U.S.`, `F.3d`, `Cal.2d`, etc.) are silently ignored. This is what `shared/eyecite_wrapper.py` exists for. Eyecite spans cover only the volume/reporter/page token (and `at PIN` for short cites); the trailing pin-cite period and the closing `)` of a citation sentence sit *outside* the span, so the citation-sentence boundary `318.)<space>The` remains visible — exactly what we want.

2. **Abbreviation list (`_ABBREVIATIONS`).** Catches what eyecite leaves on the table: honorifics, Latin connectors (`v.`), entity suffixes (`Inc.`, `Corp.`, `Co.`), CA code-name leaders (`Gov.`, `Pub.`, `Cont.`, `Civ.`, `Ed.`, `Bus.`, etc.), court/reporter abbrevs (`Ct.`, `App.`, `Dist.`, `Com.`), citation-internal glue (`subd.`, `art.`, `p.`, `pp.`), `id.` / `ibid.`, exhibit references (`Ex.`, `Exs.`), and the multi-word tails `et al.` / `et seq.` (added as `al`, `seq`).

3. **Single-letter-initial check.** Any preceding token that is a single uppercase letter is treated as a name initial (`G.L. Mezzetta`, `Margaret A. Delacroix`).

4. **Three-dot ellipsis.** `...` is mid-sentence per LS-SP-03; not flagged. `....` is end-of-sentence and remains in scope.

## Things that came up while writing this

- **`Inc.` and similar entity suffixes:** in principle could end a sentence (`The defendant is Acme Corp.`) — but in litigation drafts they almost always sit in a case name followed by `v.` (lowercase, candidate doesn't match) or `(year)` (paren is in our opener class, candidate matches and we suppress). Choosing to suppress costs us a rare true-positive at the gain of avoiding many false ones; aligns with PLAN's "precision over recall" principle.
- **`et seq.` and `et al.`:** Both can end sentences in theory. In LS practice, `et seq.` always sits inside `(See ..., et seq.)` and is followed by `)`; `et al.` is forbidden by LS-ETAL-01 anyway. Suppressing the tails is safe.
- **`Com.` (commission):** appears in case names like `California State Lottery Com. (1998) 68 Cal.App.4th ...`. Eyecite catches the `68 Cal.App.4th ...` part but not the `Com.` token, so the abbreviation list has to.
- **Year-paren as a sentence opener:** the candidate regex includes `(` in the next-char class so that LS's `prose.  (Cite.)` pattern is checked — single-spaced `prose. (Cite.)` will fire as a violation. This is correct under LS-SP-02 ("two spaces between every sentence including between substantive and citation sentences").
- **eyecite's stderr noise.** When `get_citations` can't resolve a short-cite antecedent, it prints an "Unknown overlap case" diagnostic to stderr. Non-fatal; don't suppress unless it becomes a UX problem.

## False-positive surface that future fixtures may surface

Phase-1 fixtures cover the common shapes. If new docs surface the following, extend `_ABBREVIATIONS`:

- `Comm'n.` (commission with apostrophe) — current `_PRECEDING_WORD_RE` doesn't capture across `'`, so the token reads as `n`; would not match. Likely needs a special case.
- `U. S.` (with space — older typography)
- `Ph.D.`, `J.D.` (degree initials in declarations)
- Foreign Latin like `e.g.` if it precedes a capital after `;` rather than `,` — currently the candidate-followers don't include `;` so we'd miss any `e.g. X` boundary anyway.

## Test layout

`test_rule.py` runs from the repo root. Synthetic tests cover the suppression branches; integration tests assert exact paragraph indices against each fixture's `*.violations.json` sidecar (Source of truth). Three fixtures: `clean.docx` (zero findings), `kitchen-sink-violations.docx` (¶43, ¶65), `realistic-mixed.docx` (¶62, ¶72).
