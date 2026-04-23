# Verification brief — Phase 0.5 fixture verification

You are verifying one Wave-A draft .docx against the Lozano Smith Style Manual. **Be skeptical.** The drafting subagent intended to comply with every rule listed below; your job is to find places where it fell short. Do not be lenient to make the drafting agent look good — if you're uncertain about a finding, log it as `warning` rather than dropping it.

## Inputs you should consult

1. **The .docx** at `/home/nick/Projects/style-manual-experiments/fixtures/draft-<name>.docx` — your subject of review.
2. **`/home/nick/Projects/style-manual-experiments/source-docs/StyleManual.pdf`** — firm-internal source of truth. Stays local; do not transmit. Use the Read tool with `pages:` to read specific pages.
3. **`/home/nick/Projects/style-manual-experiments/fixtures/DRAFT_BRIEF.md`** — the rules the drafting agent was asked to follow. If the brief and the PDF disagree, **flag the discrepancy** — that's a brief bug, not a draft bug, but we want to know.
4. **`/home/nick/Projects/style-manual-experiments/fixtures/seed-citations.verified.md`** — the only citations the drafter was permitted to use. Spot-check that no off-list cites slipped in.
5. **`/home/nick/Projects/style-manual-experiments/shared/document.py`** — the loader. You can use it via the venv to traverse paragraphs and inspect style metadata. The line-spacing bug from Sierra Vista's report is fixed; line spacing now reads back in points.
6. **`/home/nick/Projects/style-manual-experiments/fixtures/draft-<name>.NOTES.md`** — the drafter's own notes on judgment calls. Read these *after* you've formed your own findings, so the drafter's framing doesn't bias you.

## Tooling

- Use `.venv/bin/python` for any Python — never the system `python3`.
- Read the .docx XML directly when you need ground truth that the loader doesn't expose. Each `.docx` is a zip; `unzip -p fixtures/draft-<name>.docx word/document.xml | head -200` is fine for sanity-check work, but use Python (`docx.oxml.ns.qn`) for anything you need to do programmatically.
- Caption-block paragraphs are inside a `w:tbl` element and the loader's `paragraphs` accessor doesn't see them. To inspect the caption, iterate `doc._doc.tables` from python-docx, or grep the raw XML.

## Rules to verify

For each rule below: confirm whether the draft complies, and if not, record a finding.

### Tier 1 — text/regex

| Rule | What to check | How |
|---|---|---|
| **LS-SP-02** | Every sentence terminator (`.`, `!`, `?`) followed by another sentence is followed by **two spaces**, including before parenthetical citation sentences. | Regex over body paragraphs: `(?<=[.!?])\s+(?=[A-Z(])` — count single-space hits. Carve out sentence-final periods at end of paragraph (no following content). |
| **LS-SP-04** | Two spaces after every colon mid-paragraph. **Note**: the drafter NOTES disagree on whether caption-block label colons (`Date: ...`) count. Default: rule applies to running prose, not to form-field labels in a tabular caption. Flag any colons in body text with single space after; do NOT flag caption-table colons. |
| **LS-SP-07** | Oxford comma. Look for any `X, Y and Z` pattern in body text where Z is the final list item. Hard to detect perfectly; flag obvious misses. |
| **LS-CITE-06g** | No `Ibid.` or `ibid.` anywhere. Simple grep. |
| **LS-CITE-08b** | No superscript on `4th`, `9th`, `2d`, `3d`. Inspect runs for any `<w:vertAlign w:val="superscript"/>` near these tokens. |
| **LS-ETAL-01** | `et al.` lowercase, period only at end, not preceded by a comma. Grep for variations. |
| **LS-QUOTE-01** | Periods and commas inside the closing quotation mark. Look for `"` (or `”`) followed immediately by `.` or `,` — that's the wrong order. |
| **LS-QUOTE-02** | Colons and semicolons outside the closing quotation mark. Look for `:"`, `;"`, `:”`, `;”` — wrong order. |
| **LS-FN-05** | Footnote markers after terminal punctuation (e.g., `... timely.¹` not `... timely¹.`). The drafters use `¹` workaround characters, not real footnotes; check those. |

### Tier 2 — formatting (.docx XML)

| Rule | What to check | How |
|---|---|---|
| **LS-FONT-01** | Times New Roman 12pt on all body, heading, footnote, caption runs. | Iterate every `w:r` in `word/document.xml`; check `w:rFonts w:ascii` and `w:sz w:val` (size is in half-points, so `24` = 12pt). Flag any run that doesn't match — those will end up using Word's default. |
| **LS-SP-08** | Body paragraphs: line spacing exactly 24 pt; first-line indent 0.5". | Iterate body paragraphs (skip caption table, skip block quotes, skip headings); each should have `line_spacing == 24.0` and `line_spacing_rule == 'EXACTLY'` and `first_line_indent_in == 0.5` (within float tolerance). |
| **LS-BLOCK-01** | Block quotes (≥ 50 words) indented 0.5" both margins, single-spaced. | Identify block-quote paragraphs (likely those with non-default left/right indent). Check indent + spacing. |
| **LS-BLOCK-02** | Citation appears below the block at the left margin with normal indentation (i.e., the next paragraph after a block quote is a normal-indent paragraph containing the citation). |
| **LS-BLOCK-03** | No quotation marks surrounding block-quoted text. Inspect the quote paragraphs for opening/closing `"` / `”` at the very start/end. |
| **LS-FN-02 / LS-FN-03** | Footnote font matches body (TNR), single-spaced. The drafters used pseudo-footnotes (separator paragraph + body paragraph at the bottom), not real Word footnotes. Check whether the pseudo-footnote paragraphs have TNR 12pt and single-spacing. Flag the use of the workaround as `info`-level only — real Word footnotes are out of scope per `python-docx` limitations, and the drafting brief approves the workaround implicitly. |

### Tier 3 — citations

| Rule | What to check | How |
|---|---|---|
| **LS-CITE-02** | `§` only inside parens; `section` spelled out outside parens. `§§` for multiple sections inside parens. Grep for any `§` outside parens (false positive risk: section symbols inside in-sentence parenthetical citations are fine, since those are still "inside parens" — the rule is about the symbol vs. word, not the position in the sentence). |
| **LS-CITE-02a** | Same rule for `¶` / `paragraph`. Likely no `¶` in any draft; that's fine. Flag any out-of-parens `¶`. |
| **LS-CITE-03** | `subdivision` outside parens; `subd.` inside parens. Grep both directions. |
| **LS-CITE-04** | Code citation format inside parens: `(Code Civ. Proc., § 430.10, subd. (e).)` — comma after code name, space before §, comma between section and subdivision, period inside closing paren. Spot-check several examples. |
| **LS-CITE-04a** | No bare code abbreviations like `CCP`, `CCR`, `EC` in substantive text. Grep. |
| **LS-CITE-08a** | Case format: `Case Name v. Case Name (year) vol reporter page[, pin]` with italicized case name. Year-in-parens before reporter (CSM style). Spot-check first cites. Also: italic must be applied to the case name run; check via XML for `<w:i/>` on the relevant runs. |
| **LS-CITE-08d** | LS short cite form `(Blank, 39 Cal.3d at p. 318.)` — **no `supra`** for case short cites. Grep for any `supra` in case context. |
| **LS-CITE-06c** | `id.` (including the period) always italicized. Find every `id.` / `Id.`; for each, confirm the run carries `<w:i/>`. The trailing period must also be inside the italic run. |
| **LS-CITE-06d** | The text immediately following `id.` is generally not italicized. Spot-check a few. |
| **LS-CITE-07** | `et seq.` not preceded by comma, not italicized, lowercase. Grep. |
| **LS-CITE-13** | Modifications like `(emphasis added)` follow a comma at end of citation sentence. Spot-check if any appear. |
| **LS-CITE-HAL (spot-check)** | Every case and statute cited in the draft should be on `seed-citations.verified.md`. Extract all citations from the body text via regex (`<Word> v. <Word> (YYYY) NN <Reporter> NNN`) plus statute patterns; cross-reference against the verified list. Any citation not on the list is a finding (potential hallucination). |

### Tier 4 — semantic (manual reading required)

| Rule | What to check | How |
|---|---|---|
| **LS-CAP-02** | "District" capitalized when referring to the named defendant client; lowercase "district" / "school district" only in generic references. Same logic for "Board" / "Court" if used as defined terms. Read the draft top-to-bottom and flag every "district" / "District" that looks miscased given context. Note: "Plaintiff" should also be capitalized as a party-substitute designation throughout. |
| **LS-CAP-05** | "section" / "subdivision" / "chapter" / "paragraph" lowercase in body text except at sentence start or in headings. Grep for `Section ` mid-sentence. |
| **LS-CAP-06a / 06b** | Lowercase generic "court", "demurrer", "complaint", "petition"; capitalize "Superior Court of [County] County" when written as proper name; "the Court" capitalized when referring to the specific court for which the pleading is drafted (LS-CAP-06d). Flag inconsistencies. |

## Output

Write `/home/nick/Projects/style-manual-experiments/fixtures/draft-<name>.VIOLATIONS.md` with this structure:

```markdown
# Verification report — <name>

**Verifier**: <subagent identifier or "wave-B">
**Verified at**: <ISO date>
**Draft**: fixtures/draft-<name>.docx
**Brief**: fixtures/DRAFT_BRIEF.md (rules cross-checked against StyleManual.pdf)

## Summary

- N findings: X errors, Y warnings, Z info
- Verdict: <CLEAN | NEEDS FIX | CONCERNING>

## Findings

### <RULE_ID> — <severity> — <count>

- **¶<paragraph_index>**: <one-line description>
  - **Snippet**: "<10-30 chars context>"
  - **Recommendation**: <how to fix in build script>

(repeat per finding, grouped by rule)

## Brief vs. PDF discrepancies

(if any — list them; otherwise "None observed")

## Notes

(anything else worth flagging — performance issues, .docx oddities, etc.)
```

If the draft is genuinely clean, say so plainly. **Do not invent findings to look thorough.**

## Honesty check

Before submitting your report, ask yourself: would I stake my (subagent's) reputation on every finding being a real violation under the LS Style Manual? If not, downgrade or remove it. Empty findings list with "verdict: CLEAN" is a perfectly fine output if the draft is in fact clean.
