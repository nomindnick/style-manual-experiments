# Verification report — sierra-vista

**Verifier**: wave-B
**Verified at**: 2026-04-23
**Draft**: fixtures/draft-sierra-vista.docx
**Brief**: fixtures/DRAFT_BRIEF.md (rules cross-checked against StyleManual.pdf)

## Summary

- 8 findings: 1 error, 5 warnings, 2 info
- Verdict: NEEDS FIX

Formatting (Tier 2) is essentially spotless — every run in body and caption table is Times New Roman 12pt; body paragraphs are line-spacing EXACTLY 24 pt with 0.5" first-line indent; the block quote at P42 is 0.5" both margins, single-spaced, no surrounding quote marks, and is followed at P43 by a left-margin citation (`(Compl., ¶ 32.)`) per LS-BLOCK-02; no superscript ordinals; every `Id.` is italic with the period inside the italic run; every cited case name is italicized. Citation hallucination check: every case and every statute cross-references cleanly to `fixtures/seed-citations.verified.md` — no off-list cites. The main defects are one clear `et seq.` punctuation error, several judgment-call capitalization misses on the District's "Board," and two first-cite pin-cite omissions that the drafter cured with immediately-following pinned short cites.

## Findings

### LS-CITE-07 — error — 1

- **¶63**: `et seq.` is preceded by a comma. The LS Manual (Citations rule 7, p. 19) states explicitly: "when using 'et seq.,' it is not preceded by a comma … always lowercase, and is followed by a period at the conclusion of 'seq.' only." The manual's own examples — `(Gov. Code, §§ 6250 et seq.)` and `Government Code sections 6250 et seq., governs …` — show no comma before the phrase.
  - **Snippet**: "…Public Contract Code section 20118.4, et seq."
  - **Recommendation**: Delete the comma before `et seq.`; write `Public Contract Code section 20118.4 et seq.` Alternatively restructure into a parenthetical citation sentence like `(Pub. Cont. Code, § 20118.4 et seq.)` — still no comma before `et seq.`

### LS-CAP-02 — warning — 5

LS Capitalization rule 2 (p. 6) requires capitalizing "board," "board of education," etc. when referring to a specific agency. The Sierra Vista Unified School District's governing board is the specific Board of the defined Defendant client and is a repeated subject of the Demurrer, yet the draft consistently uses lowercase "governing board" / "board." These are the references where the antecedent is unmistakably the District's own Board (not a generic governing-board rule statement):

- **¶32**: "the District's governing board never approved…"
  - **Snippet**: "the District's governing board never approved"
  - **Recommendation**: Capitalize as "governing Board" (or define "(the 'Board')" on first reference and then use "the Board").
- **¶38**: "ratified by the District's governing board by Resolution No. 2023-24-41"
  - **Snippet**: "the District's governing board by Resolution No."
  - **Recommendation**: Same — capitalize "Board."
- **¶41**: "The District's governing board has never approved, ratified, or authorized payment…"
  - **Snippet**: "The District's governing board has never approved"
  - **Recommendation**: Capitalize "Board."
- **¶61**: "the inspector was a member of the District's governing board"
  - **Snippet**: "a member of the District's governing board"
  - **Recommendation**: Capitalize "Board."
- **¶63**: "If the governing board never approved the claimed $187,000 obligation…"
  - **Snippet**: "If the governing board never approved the claimed $187,000"
  - **Recommendation**: Context makes this a reference to the District's Board (the antecedent of the sentence is the District's own act) — capitalize "Board."

Generic references the report does NOT flag: P59 discussing "the governing board" as a statutory concept under Ed. Code § 17604/17605 (generic); P80 "subject to board review" (generic); P81 "absence of board action" (generic).

### LS-CITE-08a — warning — 2

LS Manual Citations rule 8 (p. 20): "all case citations in a pleading … should include a pin cite." The following first cites to a case appear as in-sentence cites without pin cites; in each instance the drafter supplied a pin cite through an immediately-following parenthetical short cite or `Id.` citation sentence, but the first cite itself is bare and the rule is stated without that exception.

- **¶64**: First cite to *Amelco Electric v. City of Thousand Oaks* is bare: "the Supreme Court's decision in Amelco Electric v. City of Thousand Oaks (2002) 27 Cal.4th 228 confirms the broader rule …". The pin (`pp. 234, 242–243`) appears only in the following sentence's `(Id. at pp. 234, 242–243.)`.
  - **Snippet**: "Amelco Electric v. City of Thousand Oaks (2002) 27 Cal.4th 228 confirms"
  - **Recommendation**: Add a pin to the first cite — e.g., "27 Cal.4th 228, 234, 242–243".
- **¶78**: First cite to *City of Long Beach v. Mansell* is bare: "The governing decision is City of Long Beach v. Mansell (1970) 3 Cal.3d 462." The pin (`pp. 493, 496–497`) is supplied in the next sentence via `(Mansell, 3 Cal.3d at pp. 493, 496–497.)`.
  - **Snippet**: "City of Long Beach v. Mansell (1970) 3 Cal.3d 462.  There the Supreme Court"
  - **Recommendation**: Add a pin to the first cite — e.g., "3 Cal.3d 462, 493".

### LS-SP-04 — info — 2

LS Font-Spacing rule 3 (p. 11): "Two spaces should follow every colon." The verification brief carves out form-field label colons in the caption table; these two are structurally identical form-field labels in the attorney-info header but sit outside the caption table itself, so they are not unambiguously covered by the carve-out.

- **¶7**: "Telephone: (916) 443-1800" — single space after `:`.
  - **Snippet**: "Telephone: (916)"
  - **Recommendation**: Judgment call. Either leave as a label-style single space (consistent with caption-table labels `Date:  …` which the build script renders with two spaces but the rule-checker should tolerate), or normalize to two spaces.
- **¶8**: "Facsimile: (916) 443-1801" — same.
  - **Snippet**: "Facsimile: (916)"
  - **Recommendation**: Same as ¶7.

Non-finding for reference: caption-table labels inside the `w:tbl` (`Date:  June 18, 2026`, `Time:  8:30 a.m.`, `Dept.:  Department 7`, `Judge:  Hon. Marisol D. Hernandez`, `Action Filed:  October 14, 2025`, `Trial Date:  Not yet set`) all use two spaces and are fine regardless.

## Non-findings (things I checked and cleared)

Logged here because I want the check trail visible, not because the draft is deficient.

- **LS-SP-02** (two-space sentence separation): zero single-space violations after filtering abbreviations and initials. Every `. ` / `? ` / `! ` terminating a sentence is followed by two spaces, including the substantive-sentence → parenthetical-citation-sentence transitions that are usually where drafters slip.
- **LS-SP-07** (Oxford comma): spot-checked the list constructions in the draft (P32 "account stated, declaratory relief, and equitable estoppel"; P33 "an inspector's informal acknowledgment, a post-contractual 'implied' warranty theory, nor the doctrine of equitable estoppel"; P69 "parties capable of contracting, mutual consent, a lawful object, and sufficient cause or consideration"; P87 "account stated, declaratory relief, and equitable estoppel"). All carry the serial comma.
- **LS-CITE-06g** (no `ibid.`): none.
- **LS-CITE-08b** (no superscript on 4th / 9th / 2d / 3d): no `<w:vertAlign w:val="superscript"/>` on any ordinal run anywhere.
- **LS-ETAL-01** (`et al.` form): not used in the draft.
- **LS-QUOTE-01** (periods / commas inside closing quote): all quoted fragments end with the period / comma inside the curly closer, e.g., "'represented and was understood to have bound the District to' an additional" (comma after `to,` sits outside only where the quoted phrase is mid-sentence and continues — rechecked, these are correct).
- **LS-QUOTE-02** (colons / semicolons outside closing quote): no `:"` / `;"` patterns in the text.
- **LS-CITE-02** (`§` inside parens only; `section` outside): spot-checked every `§` (22 occurrences) — all inside parentheses. Every `section` in running text outside parens spells the word. Same for `§§` on the two multi-section cites (`(Ed. Code, §§ 17604, 17605; Pub. Cont. Code, § 20118.4.)` at P82).
- **LS-CITE-02a** (`¶` usage): four occurrences, all inside parens (`(Compl., ¶ …)`); body-text paragraph references spell the word (e.g., "Compl., ¶¶ 17-20" is inside parens; no `¶` appears in running prose).
- **LS-CITE-03** (`subd.` vs `subdivision`): "subd." appears only inside parentheticals (`subd. (a)`, `subd. (b)`, `subd. (e)`, `subd. (f)`, `subds. (e), (f)`); "subdivision" appears spelled out once, in-sentence, at P73 ("Code of Civil Procedure section 430.10, subdivision (f)"). Directional rule fully honored.
- **LS-CITE-04** (code citation format in parens): spot-checked — `(Code Civ. Proc., § 430.10, subd. (e).)` at P23, `(Pub. Cont. Code, § 20118.4, subd. (a).)` at P60, `(Gov. Code, § 53060.)` at P73, etc. All have comma after code name, space before `§`, comma between section and subdivision, period inside the closing paren.
- **LS-CITE-04a** (no bare `CCP` / `CCR` / `EC`): none.
- **LS-CITE-06c** (`id.` italic including period): all three `Id.` instances (P39, P50, P64) are in italic runs with the period inside the italic run; the comma following `Id.` is outside the italic run per LS Manual p. 19 Note ("The comma is not italicized"). Correct.
- **LS-CITE-06d** (text after `id.` not italicized): rechecked; text following `Id.` is plain in all three instances.
- **LS-CITE-08d** (no `supra` for case short cites): zero `supra` in the draft. Short cites use LS form — `(G.L. Mezzetta, Inc., 78 Cal.App.4th at p. 1092)`, `(Mansell, 3 Cal.3d at p. 496)`, `(Schifando, 31 Cal.4th at p. 1081)`, `(Carma, 2 Cal.4th at p. 374)`, etc.
- **LS-CITE-13** (modifications): no `(emphasis added)` or similar in the draft; nothing to check.
- **LS-CITE-HAL**: every case and every statute cited resolves to `fixtures/seed-citations.verified.md`. Cases cited: *Blank v. Kirwan*, *Aubry v. Tri-City Hospital Dist.*, *Schifando v. City of Los Angeles*, *Zelig v. County of Los Angeles*, *Miller v. McKinnon*, *Reams v. Cooley*, *Katsura v. City of San Buenaventura*, *G.L. Mezzetta, Inc. v. City of American Canyon*, *First Street Plaza Partners v. City of Los Angeles*, *Air Quality Products, Inc. v. State of California*, *Amelco Electric v. City of Thousand Oaks*, *P&D Consultants, Inc. v. City of Carlsbad*, *City of Long Beach v. Mansell*, *Lentz v. McMahon*, *Janis v. California State Lottery Com.*, *Carma Developers (Cal.), Inc. v. Marathon Development California, Inc.*, *Guz v. Bechtel National, Inc.* — 17 of 17 on the seed list. Statutes cited: Code Civ. Proc. §§ 430.10, 430.30; Ed. Code §§ 17604, 17605; Pub. Cont. Code §§ 20111, 20118.4; Gov. Code § 53060; Civ. Code §§ 1550, 1565 — 9 of 13 seed statutes, no off-list. All subdivision references honor the seed list's subdivision-shape notes (no bogus `subd. (a)` invented for sections that lack lettered subdivisions).
- **LS-FONT-01** (TNR 12pt on all runs): iterated every `w:r` in `word/document.xml` (body) and in the caption `w:tbl`; 100% have `w:rFonts w:ascii="Times New Roman"` and `w:sz w:val="24"`. Zero inheritance-only runs that would fall back to the Normal style default.
- **LS-SP-08** (24-pt exact line spacing + 0.5" first-line indent on body paragraphs): every body paragraph carries `w:spacing w:line="480" w:lineRule="exact"` (= 24pt) and `w:ind w:firstLine="720"` (= 0.5"). The `shared.document.Document.load` accessor now correctly surfaces this as `line_spacing=24.0, line_spacing_rule='EXACTLY', first_line_indent_in=0.5` after the EMU bug fix.
- **LS-BLOCK-01** (block quote 0.5"/0.5" margins, single-spaced): ¶42 has `left_indent=0.5"`, `right_indent=0.5"`, line-spacing `SINGLE` (1.0). Word count: 62 — comfortably above the 50-word threshold. Correct.
- **LS-BLOCK-02** (citation below block at left margin with normal indentation): ¶43 `(Compl., ¶ 32.)` has `left_indent=None`, `first_line_indent=0` (i.e., flush-left), line-spacing `EXACTLY 24pt` (restored body spacing). Correct.
- **LS-BLOCK-03** (no quote marks around block): ¶42 text starts "I have completed my walk-through…" and ends "…to the District's business office." — no surrounding `"` / `"` / straight quotes. Correct.
- **LS-FN-02 / LS-FN-03**: draft contains no footnotes (pseudo- or real). Non-applicable here (unlike the `westlake` draft, this one did not need a footnote; the brief didn't require one).
- **LS-FN-05**: no footnote markers in the text, so no marker-vs-punctuation order issue to check.
- **LS-CAP-05** (`section` / `subdivision` / `chapter` / `paragraph` lowercase mid-sentence): zero `Section ` mid-sentence occurrences. All in-sentence references use lowercase "section" / "subdivision."
- **LS-CAP-06a / 06b / 06d** ("court" / "Court"): all uses of "Court" capitalized refer either to the specific court for which the pleading is drafted (P20 "above-entitled Court"; P49 "the Court accepts as true", "the Court does not", "the Court may take judicial notice"; P68 "the claim invites the Court to rewrite"; P73 "asks the Court to decree"; P87 "requests that the Court sustain") — correct per LS-CAP-06d — or to the Supreme Court / Court of Appeal as proper nouns (P64, P70, P78, P79, P82) — correct.
- **LS-CAP-02 for the District and Plaintiff**: "District" is consistently capitalized as the defined party-substitute for the defendant client (47 occurrences). "Plaintiff" is consistently capitalized as the opposing-party substitute (21 occurrences). Generic `district` / `school district` lowercase where generic (P33, P51, P59, P60, P72 adjective "school-district", P73 "school-district", P80 "school-district", P81 "school district" generic, P82 "school-district" adjective + "the district's" in the generic "contractor's risk, not the district's" statement). The one marginal call — "the district's" at P82 in the closing aphorism — is defensible as parallel to the generic "the contractor's" that anchors the same clause; treating as non-finding.
- **P50 lowercase "plaintiff" (three occurrences)**: rule-of-law restatement about demurrer plaintiffs generally (the Schifando burden-to-amend rule). Reads as the generic rule-of-law usage rather than a reference to this Plaintiff. Non-finding.

## Brief vs. PDF discrepancies

None observed. Every rule the verification brief listed maps cleanly to the StyleManual text I read (pages 5–24 covered the relevant sections). The only ambiguity is cosmetic: the brief lists `LS-CAP-06a/06b/06d` as separate rule IDs but the manual's "Common Capitalization Mistakes" section (p. 9) bundles them into a single bulleted list; the verifier treats each as a separate check but the manual's single bullet list is authoritative.

Drafting-brief observation (not a PDF discrepancy): the `DRAFT_BRIEF.md` is silent on sub-argument heading format (IV.A / IV.B / IV.C). The StyleManual at p. 7 Example 1 illustrates mixed-case sub-headings (`A. Plaintiffs Have Misinterpreted Section 65913.5.`) paired with an ALL-CAPS top-level header (`I. PLAINTIFFS HAVE MISINTERPRETED SECTION 65913.5.`), but the example's purpose is to illustrate the "Section" capitalization rule, not to prescribe sub-heading case. The drafter rendered sub-headings ALL-CAPS bold for visual consistency with the top-level headings; the manual does not explicitly forbid that choice. Not flagged as a finding, but worth surfacing as a potential Phase-1 rule-calibration question: is sub-heading case a real LS rule, or just one option among several?

## Notes

- **Document loader**: the EMU→pt line-spacing bug the Sierra Vista drafter reported in their NOTES is fixed in `shared/document.py` — verified by loading the draft and observing `line_spacing=24.0` on body paragraphs rather than 304800. Ran raw python-docx in parallel as a sanity check; agreement confirmed.
- **Caption block**: rendered as a python-docx table without cell borders, with an underscore rule (`_______________________________________`) in the left column instead of a true border. Visually clean, and all runs inside the table carry TNR 12pt (verified via `doc._doc.tables` iteration). Not a rule violation in the Tier-2 rules listed — just a style choice worth noting for Phase 1 when a caption-layout rule might get defined.
- **Page estimate**: ~9 body-text pages + caption + notice + signature. Within the brief's 6–8 target, slightly over the upper bound; consistent with the drafter's own estimate in NOTES.
- **Spot-check performance**: full verification run (text checks, XML checks, PDF rule cross-references) completed comfortably; no tooling issues.
