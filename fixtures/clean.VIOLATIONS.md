# Verification report — westlake

**Verifier**: wave-B
**Verified at**: 2026-04-23
**Draft**: fixtures/draft-westlake.docx
**Brief**: fixtures/DRAFT_BRIEF.md (rules cross-checked against StyleManual.pdf)

## Summary

- 10 findings: 5 errors, 1 warning, 4 info
- Verdict: NEEDS FIX

## Findings

### LS-SP-04 — error — 5

Single space after a colon in running body prose (rule requires two spaces).

- **¶36**: "three causes of action: (1) breach of the Contract..." — single space after colon.
  - **Snippet**: `"action: (1) breach"`
  - **Recommendation**: Change `action: (1)` to `action:  (1)` (two spaces).
- **¶42**: "strict and jurisdictional: compliance is a prerequisite..." — single space after colon.
  - **Snippet**: `"jurisdictional: compliance"`
  - **Recommendation**: Insert second space after the colon.
- **¶43**: "establish an unbroken rule: absent a board-approved, written change order..." — single space after colon.
  - **Snippet**: `"unbroken rule: absent"`
  - **Recommendation**: Insert second space after the colon.
- **¶50**: "foundational rule of Miller v. McKinnon: where a contract..." — single space after colon.
  - **Snippet**: `"McKinnon: where"`
  - **Recommendation**: Insert second space after the colon.
- **¶52**: "is likewise unavailable: the Supreme Court squarely rejected..." — single space after colon.
  - **Snippet**: `"unavailable: the Supreme"`
  - **Recommendation**: Insert second space after the colon.

### LS-BRIEF-COMPLIANCE — warning — 1

Potential verbatim court quote attributed with direct quotation marks; drafter's NOTES acknowledges risk. Brief rule 3 bars fabricated verbatim quotes from cited cases; verifier cannot confirm the text without pulling the opinions (and cannot do so under the privilege constraint).

- **¶50**: Attributes `"furnish an easy means of evading the statute."` to Miller/Katsura via short-cite "(Katsura, 155 Cal.App.4th at p. 109; Miller, 20 Cal.2d at p. 89.)". Drafter self-flagged this phrase in draft-westlake.NOTES.md as reading like a stock rule-summary but could be verbatim; risk is nontrivial because the phrase is presented inside quotation marks with a pinpoint citation, which readers will treat as direct quotation.
  - **Snippet**: `'would "furnish an easy means of evading the statute."¹'`
  - **Recommendation**: Paraphrase without quotation marks (e.g., "because it would offer contractors an easy route to circumvent the statute"), or, if retention is desired, verify the phrase in Miller/Katsura against the published opinions and keep only if it is a true verbatim excerpt. If paraphrased, remove the accompanying footnote if no longer needed.

### LS-SP-04 — info — 4

Colons followed by a single space in attorney-info form-field labels (not inside the caption table, but functioning as form-field labels in the attorney block and date line). The verification brief's default is that LS-SP-04 does not apply to form-field labels in a tabular caption. These labels are in the body paragraphs rather than the caption table, so the rule's application is ambiguous; recording as informational since they are visually aligned label/value pairs, not running prose.

- **¶5**: `"Telephone: (925) 302-2000"` — form-field label.
- **¶6**: `"Facsimile: (925) 302-2010"` — form-field label.
- **¶7**: `"Email: mcalderon@lozanosmith.com"` — form-field label.
- **¶64**: `"Dated: April 23, 2026"` — form-field label preceding the signature block.
  - **Recommendation**: No action necessary if the rule is interpreted (consistent with the brief default) to exempt form-field labels outside running prose. If Nick wants the rule to be strict across all colons in the document, a build-script pass can insert the second space.

### LS-BRIEF-COMPLIANCE — info — 2

Two additional short phrases in quotation marks attributed to specific opinions; canonical phrasings of the rules at issue, so likely verbatim, but verifier cannot confirm without reading the cases. Flagging for visibility only.

- **¶56**: `"unusual circumstances,"` attributed to the California Supreme Court in *City of Long Beach v. Mansell* (1970) 3 Cal.3d 462, 493. "Unusual circumstances" is the canonical Mansell formulation; very likely verbatim, but not verified.
- **¶56**: `"rare and limited"` attributed to the Court of Appeal in *Janis v. California State Lottery Com.* (1998) 68 Cal.App.4th 824, 830–831.
  - **Snippet**: `'estoppel claims against public entities are "rare and limited"'`
  - **Recommendation**: If Nick wants zero verbatim-quote risk in the clean fixture, paraphrase both. If the Mansell "unusual circumstances" formulation is well enough established to treat as a term of art, that alone may be acceptable.

### LS-CAPTION — info — 1

Caption block uses upright "v." between party names. LS practice (and most California trial-court practice) italicizes "v." in caption blocks. The verification brief does not include a rule on this, so flagging as informational only.

- **Caption, row 1, col 0, ¶5**: `"v."` is set in upright text. Case-name "v." inside body-text citations is correctly italicized elsewhere; caption "v." is non-italic.
  - **Recommendation**: Optional — italicize the caption's "v." in the build script for closer fidelity to LS convention.

## Brief vs. PDF discrepancies

None observed.

## Notes

- **Tier 1 (other than LS-SP-04)**: `Ibid.`/`ibid.`, `et al.`, `et seq.`, `supra` — none present. LS-QUOTE-01 / LS-QUOTE-02 / LS-FN-05 — all compliant (no misplaced punctuation; the footnote marker `¹` in ¶50 correctly follows terminal punctuation `."¹`). Oxford comma — three candidate "X and Y" patterns inspected; each is a two-item conjunction, not a three-item list. No violation.
- **Tier 2 formatting**: All runs in every body-top-level paragraph report Times New Roman 12pt (XML-confirmed on every `<w:r>`). All body-prose paragraphs (those with `first_line_indent == 0.5`) have `line_spacing == 24.0` and `line_spacing_rule == EXACTLY`. The block quote at ¶33 has 0.5" left + right indent, single-spacing, no first-line indent, and no surrounding quotation marks; the following paragraph at ¶34 (`(Compl., ¶ 20.)`) sits at the left margin, satisfying LS-BLOCK-01/02/03. Pseudo-footnote paragraphs at ¶73 and ¶74 are TNR 12pt single-spaced.
- **Tier 3 citations**: Every first-cite full case citation found in the body (via regex) is on `seed-citations.verified.md`. Statute citations (Code Civ. Proc. § 430.10 subds. (e)/(f), § 430.41 subd. (a); Ed. Code §§ 17604, 17605 [no subdivisions cited]; Pub. Cont. Code §§ 20111, 20118.4 subd. (a); Civ. Code §§ 1550, 1565 [no subdivisions]; Gov. Code § 815 [no subdivision]) all match the verified seed list and honor the subdivision-shape notes. `§` / `section` / `subd.` / `subdivision` placement (inside vs. outside parens) is correct throughout. All case names in both full and short cites are italicized (XML-verified; the build script uses explicit `<w:i w:val="0"/>` for non-italic runs and `<w:i/>` for italic runs, which requires the reader to check the `val` attribute — my first pass naively treated any `<w:i>` as italic and had to be corrected). Both `Id.` occurrences (¶50 and ¶56) are fully italicized including the period, and the text following `Id.` is non-italic.
- **Tier 4 capitalization**: "District" / "Plaintiff" / "Board" are correctly capitalized when used as party-substitute designations for the defendant client / the opposing party / the defendant's defined governing body, and correctly lowercased in generic references (`school district`, `school-district contracts`, `a plaintiff who had performed services`, `the governing board`, `by board action`, etc.). "the Court" is capitalized in references to the specific pleading court (¶18 "the above-entitled Court", ¶55 "asks the Court", ¶62 "requests that the Court") and in proper-name references ("Court of Appeal", "Supreme Court"); "the court" is lowercased in generic demurrer-standard statements (¶38) and in "the Katsura court" (¶50). LS-CAP-05: no mid-sentence capitalized "Section"/"Subdivision"/"Chapter"/"Paragraph".
- **Tier 1 quote punctuation**: Commas and periods are inside closing quotes throughout (e.g., `"extras."`, `"rare and limited"`, `"unusual circumstances,"`). No colon/semicolon inside a closing quote.
- **Signal italics**: "see" / "see also" / "See" are non-italic in ¶53, ¶59, and ¶74. LS practice and the Bluebook generally italicize introductory signals, but the verification brief does not list signal-italicization as a rule to check; not flagged.
- **LS-CITE-08b superscript**: XML scan found zero `<w:vertAlign w:val="superscript"/>` elements in the document; `4th`, `3d`, `2d` are all rendered as plain text.
- **Overall**: The draft is close to clean. The LS-SP-04 body-prose misses (five instances) are consistent — likely a single formatting habit in the build script (using `": "` instead of `":  "`). If those are fixed and the "furnish an easy means" phrase is paraphrased or verified, the draft should be clean for Phase 0.5 purposes.
