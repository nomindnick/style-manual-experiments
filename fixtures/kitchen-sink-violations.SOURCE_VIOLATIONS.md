# Verification report — eastvale

**Verifier**: wave-B
**Verified at**: 2026-04-23T21:45:03Z
**Draft**: fixtures/draft-eastvale.docx
**Brief**: fixtures/DRAFT_BRIEF.md (rules cross-checked against StyleManual.pdf pp. 6-13)

## Summary

- 3 findings: 3 errors, 0 warnings, 2 info
- Verdict: NEEDS FIX

## Findings

### LS-SP-04 — error — 3

Style Manual p. 11, section 3 ("Colons"): "Two spaces should follow every colon." The manual states the rule flatly, with no carve-out distinguishing introducer colons from label colons. Three body-text colons in the draft have only a single space after them.

- **¶50**: colon introducing the enumerated list of causes of action has one space, not two.
  - **Snippet**: `"...three causes of action against the District: (1) breach of the implied covenant..."`
  - **Recommendation**: In the build script, change `: (1)` to `:  (1)` in the IV/Statement-of-Allegations paragraph that enumerates the three causes of action.

- **¶68**: colon introducing the two independent reasons the contract claim fails has one space.
  - **Snippet**: `"...fails as a matter of law for two independent reasons: (1) Public Contract Code section 20118.4 requires..."`
  - **Recommendation**: Change `reasons: (1)` to `reasons:  (1)` in the first paragraph of Section IV.B.

- **¶73**: colon introducing an explanatory clause has one space.
  - **Snippet**: `"...The rule could not be clearer: when a public contract contains express change-order provisions..."`
  - **Recommendation**: Change `clearer: when` to `clearer:  when` in the Amelco discussion paragraph in Section IV.B.

### LS-CAP-06d — info — 1

Style Manual p. 9 ("Do capitalize ... 'the Court' when referring to the court for which a pleading is drafted"). The draft uses lowercase "the court" / "this court" several times in ways that address the tribunal the demurrer is filed in (¶¶25, 38, 40, 63, 85). Per the PDF rule these should be "Court." Recording as `info` rather than `error` because (a) the rule is catalogued as Tier 4 and currently "queued" (not yet in the Phase-1 scope) and (b) the DRAFT_BRIEF text at lines 81-83 is itself ambiguous on this — it lists capitalization for the specific tribunal among capitalization rules, but the examples and enforcement focus are on party-substitute terms. The drafter's lowercase choice is internally consistent across the document. Flagged for future review rather than as a hard violation.

- **¶¶25, 38, 40, 63, 85**: examples include "any further evidence and argument the court may consider" (¶25); "Plaintiff now asks this court to override" (¶38); "the District respectfully requests that the court sustain this demurrer" (¶40, ¶85); "Plaintiff's ... theory asks the court to impose" (¶63). The abstract "the court treats the demurrer as admitting" at ¶53 is defensibly generic and not flagged.
  - **Snippet**: `"...respectfully requests that the court sustain this demurrer without leave to amend."`
  - **Recommendation**: If the LS-CAP-06d interpretation is enforced, upper-case "Court" wherever the reference is to the San Bernardino Superior Court hearing this demurrer. Leave the abstract/doctrinal "the court treats the demurrer" (¶53) lowercase.

### LS-SP-02 — info — 1

Three spaces (instead of two) between sentences at ¶38. Not a Style Manual violation per se (the rule is "two spaces between every sentence," and three still satisfies "between"), but likely an oversight from manual spacing in the build script. Noted for clean-up.

- **¶38**: `"...following competitive bidding.   The contract — like every contract..."`
  - **Snippet**: three consecutive spaces after "bidding."
  - **Recommendation**: In the Introduction paragraph, collapse the extra space after "competitive bidding." to two.

## Brief vs. PDF discrepancies

None observed. The DRAFT_BRIEF's two-space-after-colon rule (lines 52-53) tracks Style Manual p. 11 §3. The LS-CITE-06g "no `ibid.`" rule tracks the manual's divergence. The CATALOG's characterization of LS-CITE-07 as "et seq. not italicized" (Bluebook would italicize) is consistent with the manual and is what the draft follows.

## Notes

- **Citations (LS-CITE-HAL)**: clean. Every case citation extracted from the draft (17 distinct cases, plus repeat short cites) is present on `seed-citations.verified.md`. No off-list citations appeared. Statute citations (Code Civ. Proc. §§ 430.10, 430.41; Pub. Cont. Code §§ 20111, 20118.4, 22300; Ed. Code §§ 17604, 17605; Gov. Code §§ 815, 53060; Civ. Code §§ 1550, 1565) all track the verified seed, and the subdivision-shape notes are honored (no fabricated subdivisions on Ed. Code §§ 17604/17605 or Gov. Code § 53060; Civ. Code §§ 1550/1565 cited without inventing lettered subdivisions).

- **Citation formatting**: all case names italicized in full and short cites (verified via XML `<w:i/>` inspection of every `v.` pattern). All four `Id.` occurrences italicized including the trailing period (¶¶61, 63, 70, 73); text following `Id.` is non-italic in each case. LS short-cite form `(Blank, 39 Cal.3d at p. 318.)` used consistently — no `supra` for case short cites. Inside-parens/outside-parens discipline for `§`/`section` and `subd.`/`subdivision` is clean.

- **Tier-2 formatting**: all runs in `word/document.xml` resolve to Times New Roman at 24 half-points (12 pt), including `cs`, `eastAsia`, and `hAnsi` font-slot overrides. No `<w:vertAlign w:val="superscript"/>` runs present — `Cal.4th` / `Cal.App.4th` / `Cal.2d` / `Cal.App.3d` are all plain text, as required by LS-CITE-08b. No underlines; no non-default colors.

- **LS-SP-08 body paragraph formatting**: every body paragraph (excluding caption table, headings, block quote, signature block) has `line_spacing = 24.0 pt` with rule `EXACTLY` and `first_line_indent = 0.5"`. Zero exceptions.

- **LS-BLOCK-01/02/03 (block quote at ¶46)**: indented 0.5" left and right, `line_spacing = SINGLE`, no surrounding quotation marks. Citation `(Compl., ¶ 11 & Ex. A, art. 12.2.)` immediately follows at ¶47 at the left margin with the normal 0.5" first-line indent. Conforms to all three block-quote rules.

- **Caption-block colons** (`Telephone:`, `Hearing Date:`, `Dated:`, etc.) use two-space form. Per the verification brief these are not flagged regardless of outcome; noted here for completeness that the draft applies the convention consistently.

- **`ab initio` italicized** at ¶¶72, 79. The LS Style Manual is silent on Latin legal phrases other than `et al.` / `et seq.`, so this is treated as a non-finding per the verification-brief instruction and the drafter's NOTES judgment call.

- **Pseudo-footnotes**: the draft contains no pseudo-footnotes (no footnote content at all — the document has no `word/footnotes.xml` and no body-bottom footnote paragraphs). LS-FN-02 / LS-FN-03 are moot for this fixture.

- **LS-CAP-02 (District capitalization)**: clean. "District" is capitalized throughout when referring to the client (defined in ¶20 as `("District")`); lowercase "district" / "school district" appears only in clearly generic contexts (e.g., "a California school district is a party" ¶38; "against a school district" ¶39; "school-district public works" ¶68; paraphrased statute language at ¶70). Party-substitute "Plaintiff" is capitalized consistently (28 occurrences); the five lowercase "plaintiff" uses are in abstract demurrer-doctrine discussion (¶54) or as a lowercase descriptor before the full name on first reference (¶20). Both are defensible.

- **Superintendent / Board of Trustees**: capitalized when referring to the District's specific officer and body; lowercase "board" / "governing board" appears in generic/statutory paraphrase. One mild ambiguity: ¶38 "the District's governing board" uses lowercase, which could arguably be "Board" given the possessive ties it to the specific body. Not flagged — the generic statutory phrase "governing board" is a reasonable reading and the pattern is consistent elsewhere.

- **Brief bug to flag for later**: DRAFT_BRIEF line 62 contains a self-correction about `supra` that reads awkwardly ("Short cite: `(Blank, supra, 39 Cal.3d at p. 318.)` — wait, LS does not use `supra`...") — the "wait" clause is an editorial marker that probably should be cleaned up before the brief is reused, but it does not affect rule interpretation.
