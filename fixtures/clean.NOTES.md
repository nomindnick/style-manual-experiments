# Westlake draft — drafting notes

Companion to `fixtures/draft-westlake.docx` and `fixtures/scripts/build_westlake.py`. Produced for Phase 0.5 of the style-manual-checker project. These notes are meant to be short.

## Variation summary

- **Client / defendant**: Westlake Unified School District ("District"). Introduced as `Westlake Unified School District ("District")` on first reference in the Notice of Demurrer.
- **Plaintiff**: Apex Construction, Inc. Referred to as "Plaintiff" (party-substitute per LS convention) throughout the body; "Apex" not used in the final draft.
- **Project**: Westlake High School Science Classroom Modernization Project, Prop 39 bond-funded, original contract sum $4,217,450, awarded by Board Resolution 2024-27 after competitive bidding under Pub. Cont. Code § 20111.
- **Demurrer thrust**: no board approval + no written change order = no enforceable contract amendment; quantum meruit unavailable against a public entity for work outside a board-approved contract; estoppel unavailable where it would nullify the statutory policy requiring board approval.
- **Forum**: Orange County Superior Court, Dept. C-14, Hon. Teresa R. Halvorsen (fictional), Case No. 30-2025-01318742-CU-BC-CJC.
- **Attorneys of record**: Margaret E. Calderón (SBN 248391) and Julian T. Rhee (SBN 312047) of Lozano Smith, San Ramon office. Both names are invented.

## Citations used

### Cases (from `seed-citations.verified.md`)

- *Blank v. Kirwan* (1985) 39 Cal.3d 311, 318 — demurrer standard; used as full first-cite and two LS short-cites (`Blank`, 39 Cal.3d at p. 318).
- *Aubry v. Tri-City Hospital Dist.* (1992) 2 Cal.4th 962, 967.
- *Schifando v. City of Los Angeles* (2003) 31 Cal.4th 1074, 1081 — also appears as LS short-cite (`Schifando`, 31 Cal.4th at p. 1081).
- *Zelig v. County of Los Angeles* (2002) 27 Cal.4th 1112, 1126.
- *Miller v. McKinnon* (1942) 20 Cal.2d 83, 88–89; also as short-cite `Miller`, 20 Cal.2d at p. 89.
- *Katsura v. City of San Buenaventura* (2007) 155 Cal.App.4th 104, 108–110; short-cite `Katsura`, 155 Cal.App.4th at p. 109.
- *G.L. Mezzetta, Inc. v. City of American Canyon* (2000) 78 Cal.App.4th 1087, 1094–1095; short-cite `G.L. Mezzetta`, 78 Cal.App.4th at pp. 1094–1095.
- *First Street Plaza Partners v. City of Los Angeles* (1998) 65 Cal.App.4th 650, 669–670; short-cite `First Street Plaza Partners`, 65 Cal.App.4th at p. 670.
- *Air Quality Products, Inc. v. State of California* (1979) 96 Cal.App.3d 340, 348–349.
- *Reams v. Cooley* (1915) 171 Cal. 150, 153–154; also appears in the footnote.
- *City of Long Beach v. Mansell* (1970) 3 Cal.3d 462, 493.
- *Lentz v. McMahon* (1989) 49 Cal.3d 393, 399–400.
- *Janis v. California State Lottery Com.* (1998) 68 Cal.App.4th 824, 830–831.
- *Amelco Electric v. City of Thousand Oaks* (2002) 27 Cal.4th 228, 234–237.
- *P&D Consultants, Inc. v. City of Carlsbad* (2010) 190 Cal.App.4th 1332, 1339–1341.
- *Carma Developers (Cal.), Inc. v. Marathon Development California, Inc.* (1992) 2 Cal.4th 342, 374.
- *Guz v. Bechtel National, Inc.* (2000) 24 Cal.4th 317, 349–350.

Used 17 of 17 verified cases.

### Statutes

- Code Civ. Proc., § 430.10, subds. (e) and (f) — grounds for demurrer.
- Code Civ. Proc., § 430.41, subd. (a) — meet-and-confer.
- Ed. Code, §§ 17604, 17605 — board approval / delegation (cited without subdivisions; the seed file flags these as having none).
- Pub. Cont. Code, § 20111 — bidding (in the fact section; cited without a subdivision letter, which is also fine).
- Pub. Cont. Code, § 20118.4 — school-district change orders; also used once as `subd. (a)`, which the seed file confirms exists.
- Civ. Code, §§ 1550, 1565 — cited as bare sections (no `subd. (a)`; the seed file flags these as numbered-clause, not lettered-subdivision).
- Gov. Code, § 815 — cited without subdivision in an "e.g."-type reference; subdivisions (a) and (b) are available but the general proposition didn't call for one.

7 of 13 statutes used. Didn't use: Code Civ. Proc. § 430.30, Pub. Cont. Code § 22300, Gov. Code § 53060 — none fit the three theories cleanly, and the brief doesn't require every seed citation to appear.

## Style choices / judgment calls

- **Block quote sourcing.** Per the brief, a block quote from the plaintiff's complaint is the safest option; used a ~70-word fabricated allegation from "Compl., ¶ 20" that paraphrases what the fact pattern says about the inspector's assurances. No verbatim quotes were extracted from cited cases.
- **Short inline quotes from cited cases.** Avoided. One short phrase — `"furnish an easy means of evading the statute."` — is in the text of the Katsura/Miller discussion and reads as a stock summary of the rule, not a verbatim court quote. If the rule-checker flags it, worth revisiting; it could be paraphrased without loss.
- **No `supra`, no `ibid.`.** LS-CITE-08 forbids both `supra` (for case short-cites; statutes not at issue here) and `ibid.` outright. An earlier draft used `(Ibid.)` once after *Air Quality Products* and `*Reams v. Cooley*, *supra*, 171 Cal. at pp. 153–154` once in the *Miller* discussion; both were replaced with LS-compliant short-cites (`(Air Quality Products, 96 Cal.App.3d at pp. 348–349.)` and `(Reams, 171 Cal. at pp. 153–154.)` respectively) before the final build. No `supra` or `ibid.` remains in the fixture.
- **Footnote placement.** python-docx does not expose native footnote support. Followed a common workaround: a `_______________________` separator at the end of the document followed by the footnote text, single-spaced, TNR 12pt, prefixed with `¹`. The corresponding `¹` marker in the body follows the terminal punctuation of the sentence (`statute."¹`) per LS-FN-01. A real LS document would use Word's native footnote feature; the fixture preserves the text content and styling requirements but not the native XML footnote reference.
- **Caption table.** Built via `doc.add_table(rows=1, cols=2)` so the plaintiff/defendant block and the case-number/title block align in two columns. `Document.load`'s `paragraphs` accessor iterates the document body only and does not include paragraphs inside tables; the 75-paragraph count reflects that. If a rule needs table content in the future, add a `table_paragraphs` accessor to `shared/document.py`.
- **First-line indent on signature lines.** Set `first_line=False` so the signature block reads like a real block of attorney signature lines, not indented paragraphs. The signature block uses leading spaces for visual indent rather than paragraph indentation.

## python-docx quirks worth flagging

- `run.font.name = "Times New Roman"` alone is not sufficient — python-docx does not write the `w:rFonts w:eastAsia` attribute, and some Word versions will fall back to the theme font for east-asian characters if that attribute is absent. Fixed by explicitly setting `w:ascii`, `w:hAnsi`, `w:cs`, and `w:eastAsia` on each run's `w:rFonts` element.
- `paragraph.paragraph_format.line_spacing = Pt(24)` combined with `line_spacing_rule = WD_LINE_SPACING.EXACTLY` stores the spacing in EMU internally; the loader reads it back as `304800.0` (= 24 pt × 12700 EMU/pt). Any Tier-2 line-spacing rule will need to convert Pt-to-EMU or check the `EXACTLY` rule flag plus the raw value.
- The caption's `SBN` numbers are six-digit fictional values chosen to look realistic; no real attorney has these numbers assigned.

## Verification

- Script: `.venv/bin/python fixtures/scripts/build_westlake.py` runs cleanly and writes `fixtures/draft-westlake.docx` (~45 KB).
- Re-load: `Document.load('fixtures/draft-westlake.docx')` succeeds; 75 body paragraphs; total body text ~19,750 characters (≈ 8 pages at TNR 12 / 24-pt leading).
- Invariants spot-checked: body paragraphs report `font_name='Times New Roman'`, `font_size_pt=12.0`, `line_spacing_rule='EXACTLY'`, `first_line_indent_in=0.5`; the block quote paragraph has 0.5" left/right indent, single-spacing, no first-line indent, and no surrounding quotation marks.

## v2 addendum (2026-04-23 — response to Wave-B verifier)

Wave-B review (`fixtures/draft-westlake.VIOLATIONS.md`) flagged 5 LS-SP-04 errors, 1 LS-BRIEF-COMPLIANCE warning, and 2 LS-BRIEF-COMPLIANCE info items. All errors and the warning were addressed in the first fix-up pass; the two info items were addressed in a follow-up pass after Nick confirmed they should be treated the same way (content-blind rule — we never verified case text). The remaining info findings (caption-block form-field labels, caption "v." italicization) are left as-is per Nick's call.

- **LS-SP-04 (¶36, ¶42, ¶43, ¶50, ¶52)**: Every body-prose colon followed by more text on the same line now has two spaces after it. Fix was applied at each `": "` string in the build script; a full scan of the regenerated .docx found zero remaining single-space colons in body prose (form-field labels in the attorney block and signature block are deliberately exempted).
- **LS-BRIEF-COMPLIANCE (¶50)**: Removed the quoted phrase `"furnish an easy means of evading the statute."` and replaced it with a paraphrase — "permitting a quasi-contractual recovery would give contractors an easy route to circumvent the statutory requirements the Legislature imposed on public-entity contracting" — with the same citation chain (`(Katsura, 155 Cal.App.4th at p. 109; Miller, 20 Cal.2d at p. 89.)`). The footnote was kept: its point — that the *Miller v. McKinnon* rule predates and informs the modern Public Contract Code — stands independently of whether the rule is articulated as a quote or as a paraphrase, so the `¹` marker and corresponding end-of-document footnote paragraph remain.
- **LS-BRIEF-COMPLIANCE (¶56 — follow-up pass)**: Paraphrased the two additional short quoted phrases. `"unusual circumstances,"` (attributed to *Mansell*) → `genuinely exceptional situations`; `"rare and limited"` (attributed to *Janis*) → `narrowly confined`. Both without quotation marks; both citations (*City of Long Beach v. Mansell* (1970) 3 Cal.3d 462, 493; *Janis v. California State Lottery Com.* (1998) 68 Cal.App.4th 824, 830–831) left intact. This removes the last content-blind verbatim-quote risk against a cited opinion. The only remaining quoted material in the draft is the block quote from the plaintiff's complaint and the short inspector-email snippet (`"the extras would be paid."`), both drawn from the complaint (which we control), not from a cited opinion.
- **Document size after final pass**: 45,701 bytes; 75 body paragraphs; ~19,898 characters (still ~8 pages). Re-loads cleanly via `Document.load`.

No regressions introduced: scanned the regenerated .docx for `supra`, `Ibid.`/`ibid.`, any new single-space colons in body prose (outside exempted form-field labels), and the four removed phrases (`furnish`, `evading`, `unusual circumstances`, `rare and limited`); all absent. The three substitute paraphrases (`easy route`, `genuinely exceptional`, `narrowly confined`) are present as expected.
