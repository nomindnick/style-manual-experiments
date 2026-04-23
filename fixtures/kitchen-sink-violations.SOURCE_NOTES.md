# draft-eastvale.docx — drafting notes

Companion to `draft-eastvale.docx` (produced by `fixtures/scripts/build_eastvale.py`). These notes cover the drafting choices worth flagging for the rule-checker run and for later fixture maintenance.

## v2 addendum (2026-04-23) — post-verification fixes

Wave-B verifier produced `fixtures/draft-eastvale.VIOLATIONS.md` with 3 errors / 2 info. All items addressed:

- **LS-SP-04 (3 errors, fixed).** Single-space-after-colon in body prose at the paragraph enumerating causes of action ("…three causes of action against the District:  (1) breach…"), the IV.B opener ("…two independent reasons:  (1) Public Contract Code…"), and the Amelco discussion ("…could not be clearer:  when a public contract…"). Each was expanded to two spaces. Swept the whole script afterward — no other body-prose colons with a single space remain. Caption-block form-field colons (`Telephone:`, `Hearing Date:`, the `[… re: Meet and Confer …]` title descriptor) are exempt per the verification brief and were left as previously set.
- **LS-SP-02 (1 info, fixed).** Triple-space blip after "following competitive bidding." in the Introduction paragraph. Root cause: a stray `"".ljust(1)` segment between two other string segments that each already contributed whitespace, producing `.` + ` ` + `  ` = three spaces. Removed the stray segment; the two-space sentence break is now clean.
- **LS-CAP-06d (1 info, fixed per brief).** Capitalized "Court" on every reference to the specific tribunal hearing this demurrer: Notice of Demurrer ("further evidence and argument the Court may consider"), Notice of Demurrer ("in Department S-26 of the above-entitled Court" — verifier did not flag this instance, caught on drafter sweep), Introduction ("Plaintiff now asks this Court to override…"; "respectfully requests that the Court sustain…"), Section IV.A ("implied-covenant theory asks the Court to impose…"), Conclusion (two occurrences: "the Court sustain the District's demurrer…"; "the Court deems just and proper"). Six token-level fixes total (the verifier counted five paragraphs; the Conclusion paragraph contains two references, accounting for the delta). One lowercase "the court" preserved at ¶53 — it states the abstract demurrer-review rule ("the court treats the demurrer as admitting all material facts properly pleaded") — which the verifier explicitly identified as defensibly generic and not flagged. Other proper-noun court references ("Supreme Court," "Court of Appeal") were already capitalized. References to the court that decided a cited case (e.g., "the Carma court stated…") remain lowercase — those are generic references to other tribunals, not to this tribunal.

Rebuild confirmed: `fixtures/draft-eastvale.docx` (46,259 bytes, 95 body paragraphs, 21,700 chars), re-loadable via `Document.load`. Post-fix audit: 0 body-prose single-space colons, 0 sentence-break triple-spaces, 5 "the Court" + 1 "this Court" capitalized references to this tribunal, 1 intended lowercase "the court" in the abstract-doctrine paragraph.

**One item the verifier missed, caught on my sweep**: "the above-entitled court" in the Notice of Demurrer paragraph (Notice-of-Demurrer section, not listed in the VIOLATIONS.md ¶25/¶38/¶40/¶63/¶85 list). Capitalized to "the above-entitled Court" on the same LS-CAP-06d rationale — "the above-entitled court" is formulaic notice-of-hearing phrasing referring specifically to the tribunal where the hearing will be held.

**No push-back.** All verifier findings were well-founded on re-inspection; nothing flagged was a false positive.

## Variation

- **Defendant**: Eastvale Joint Union High School District ("District")
- **Plaintiff**: Riverbend Mechanical Services, LLC ("Plaintiff"; "Riverbend" used sparingly)
- **Project**: HVAC retrofit of Eastvale High School's main classroom building, contract sum $2,847,500
- **County / court**: San Bernardino County Superior Court, Dept. S-26, Hon. Teresa M. Halvorsen (all fictional)
- **Case no.**: CIVSB 2532109 (fictional; format mirrors San Bernardino conventions)
- **Attorneys of record**: Margaret A. Delacroix (SBN 289431) and Jonathan R. Pemberton (SBN 312778), fictional, Sacramento office (One Capitol Mall, Suite 640)

## Seed citations used

All citations drawn verbatim from `fixtures/seed-citations.verified.md`. No new citations invented.

### Cases

| Citation | Where used |
|---|---|
| *Blank v. Kirwan* (1985) 39 Cal.3d 311 | Intro to II; III (full first cite + short cite `(Blank, 39 Cal.3d at p. 318.)`) |
| *Aubry v. Tri-City Hospital Dist.* (1992) 2 Cal.4th 962 | III (full first cite + short cite `(Aubry, 2 Cal.4th at p. 967.)`) |
| *Schifando v. City of Los Angeles* (2003) 31 Cal.4th 1074 | III, IV.A, IV.C (full + short `(Schifando, 31 Cal.4th at p. 1081.)`) |
| *Zelig v. County of Los Angeles* (2002) 27 Cal.4th 1112 | II |
| *Guz v. Bechtel National, Inc.* (2000) 24 Cal.4th 317 | I, IV.A (full + short `(Guz, 24 Cal.4th at p. 350.)` + `(Id. at p. 350.)`) |
| *Carma Developers (Cal.), Inc. v. Marathon Development California, Inc.* (1992) 2 Cal.4th 342 | IV.A (full + short `(Carma, 2 Cal.4th at p. 374.)`) |
| *P&D Consultants, Inc. v. City of Carlsbad* (2010) 190 Cal.App.4th 1332 | IV.B |
| *G.L. Mezzetta, Inc. v. City of American Canyon* (2000) 78 Cal.App.4th 1087 | IV.B, IV.C |
| *First Street Plaza Partners v. City of Los Angeles* (1998) 65 Cal.App.4th 650 | IV.B, IV.C |
| *Air Quality Products, Inc. v. State of California* (1979) 96 Cal.App.3d 340 | IV.B |
| *Lentz v. McMahon* (1989) 49 Cal.3d 393 | IV.B, IV.C |
| *City of Long Beach v. Mansell* (1970) 3 Cal.3d 462 | IV.B (bracketed parenthetical) |
| *Janis v. California State Lottery Com.* (1998) 68 Cal.App.4th 824 | IV.B (bracketed parenthetical) |
| *Amelco Electric v. City of Thousand Oaks* (2002) 27 Cal.4th 228 | IV.B |
| *Miller v. McKinnon* (1942) 20 Cal.2d 83 | I, IV.C |
| *Reams v. Cooley* (1915) 171 Cal. 150 | IV.C |
| *Katsura v. City of San Buenaventura* (2007) 155 Cal.App.4th 104 | IV.C |

### Statutes

| Statute | Where used | Form |
|---|---|---|
| Code Civ. Proc., § 430.10 | Notice of Demurrer (grounds); III | `§ 430.10, subd. (e)` and `subds. (e), (f)` (subdivisions verified) |
| Code Civ. Proc., § 430.41 | III | bare section cite (meet-and-confer) |
| Pub. Cont. Code, § 20111 | II (low-responsible-bidder award) | bare section cite |
| Pub. Cont. Code, § 20118.4 | I, IV.B (two references) | bare section cite — verified has (a)/(b) subds. but drafting avoided forcing one |
| Pub. Cont. Code, § 22300 | IV.C | bare section cite (retention substitution) |
| Ed. Code, § 17604 | I, IV.B | bare section cite (no subdivisions — honored) |
| Ed. Code, § 17605 | I, IV.B | bare section cite (no subdivisions — honored) |
| Gov. Code, § 53060 | IV.C | bare section cite (no lettered subdivisions — honored) |
| Gov. Code, § 815 | IV.C | `subd. (a)` (verified subdivision) |
| Civ. Code, §§ 1550, 1565 | IV.B | compound section cite (clause structure — no subd. letter used) |
| Code Civ. Proc., §§ 430.10 et seq. | III | `et seq.` lowercase, unitalicized per LS-CITE guidance |

## LS style conformance notes

### Did

- **Two spaces between every sentence** in body text (including between a substantive sentence and a following parenthetical citation sentence).
- **Two spaces after every sentence-level colon** (e.g., "the same flawed premise:  that…"; "Dated:  April 22, 2026"; "Hearing Date:  July 14, 2026").
- **Oxford comma** throughout.
- **"et seq."** lowercase, unitalicized, period only at the end.
- **`§` only inside parens; "section" in running text** (e.g., "Public Contract Code section 20118.4" in prose, `(Pub. Cont. Code, § 20118.4.)` in citation sentences).
- **LS short cites** of the form `(Blank, 39 Cal.3d at p. 318.)` — no `supra` for cases.
- **`Id.` italicized including the period**; text following `Id.` is non-italic.
- **`Ibid.` avoided** entirely (LS forbids it).
- **`ab initio`** italicized (Latin legal phrase).
- **Case names italicized** in full and short citations.
- **Periods/commas inside close-quote marks** where applicable.
- **`Cal.App.4th` / `Cal.4th` / `Cal.App.3d`** written without superscript.
- **Font**: Times New Roman 12pt applied on every run (not just Normal style), with east-asian/cs fallbacks set so Word won't substitute Calibri for ambiguous characters.
- **Line spacing**: `Pt(24)` with `WD_LINE_SPACING.EXACTLY` on every body paragraph.
- **First-line indent**: 0.5" on body paragraphs; headings and block quotes do not receive a first-line indent.
- **Block quote**: one included (General Conditions Article 12 text, quoted from the plaintiff's complaint — a source the draft controls, so no fabricated court language). Indented 0.5" both margins, single-spaced, no surrounding quotation marks. Citation `(Compl., ¶ 11 & Ex. A, art. 12.2.)` appears on its own line below at the left margin with normal first-line indent.
- **No fabricated verbatim quotes from cited cases**. Every case proposition is paraphrased. The only quotation-mark-enclosed text attributed to an external source is (a) Complaint allegations I wrote myself, (b) the defined-term-introducing parentheticals (`("District")`), and (c) one short phrase from Code Civ. Proc. § 430.10 (statutory text is permitted per the brief).
- **Party-substitute "Plaintiff" capitalized** throughout; "the District" capitalized after first reference; generic "the court" / "a school district" lowercase.

### Judgment calls / mild ambiguities

1. **Caption-block label colons.** I applied the "two spaces after colon when followed by more text on same line" rule to caption-block field labels (`Telephone:  (916)…`, `Hearing Date:  July 14, 2026`, `Dated:  April 22, 2026`). The LS Style Manual rule is plausibly targeted at running prose rather than field-label alignment, but I treated form-field colons conservatively as "colon followed by more text" and doubled the space. One exception: the time-format colon in `8:30 a.m.` is unchanged (it is not a sentence/label colon).

2. **Caption-block layout uses a 1-row/2-col table.** python-docx does not produce a vertical rule between the parties and case-info columns automatically, and I did not add one. This matches the *content* of a typical California superior-court caption but is visually simpler than a pleading-paper caption with a left vertical rule and numbered lines. That simplification is acceptable for a rule-checker fixture (the rules focus on prose and citations, not caption geometry).

3. **`et seq.` un-italicized.** The LS brief says "both lowercase, period only at end, not italicized" for *et seq.* and *et al.* I implemented that. Bluebook practice generally italicizes *et seq.*, so this is a deliberate LS-specific departure. Flagging in case later review questions it.

4. **`ab initio` italicized.** The brief does not explicitly list other Latin phrases. I italicized *ab initio* as a standard Latin-phrase convention in legal prose. If the rule-checker later flags un-italicized Latin, this choice is consistent; if it flags italicized Latin, re-visit.

5. **`Id.` vs. `id.`** I used capitalized `Id.` every time, because every `Id.` in the draft begins a standalone parenthesized citation sentence (which per the brief is the capitalized form). I did not use lowercase `id.` because I had no in-sentence `id.` occasion.

6. **Footnotes: none.** The document contains no footnotes. LS-FN-02 / LS-FN-03 formatting is therefore moot for this fixture but I kept the `configure_default_styles` defaults (TNR 12pt) consistent so that adding a footnote later would inherit correct formatting.

7. **LS short-cite on a single-defendant case with a unique surname plaintiff**: I used the first party's short form (`(Blank, 39 Cal.3d at p. 318.)`, `(Guz, 24 Cal.4th at p. 350.)`, `(Carma, 2 Cal.4th at p. 374.)`, `(Schifando, 31 Cal.4th at p. 1081.)`, `(Katsura, 155 Cal.App.4th at p. 109.)`). Consistent with the brief's stated LS form.

## python-docx quirks worth flagging

- **Font fallback.** Setting `run.font.name = 'Times New Roman'` alone leaves python-docx's `w:rFonts` element with only the `ascii` attribute. Word will substitute Calibri for characters classified as "east-asian" or "cs." I explicitly set `ascii`, `hAnsi`, `cs`, and `eastAsia` on the `rFonts` element both at the Normal-style level and per-run. Without this, Tier-2 font checks on an extracted run could report `Calibri` for a character the user did not see as Calibri in Word.
- **Line spacing.** python-docx requires both `paragraph.paragraph_format.line_spacing = Pt(24)` AND `paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY`. If you set only the first, the value is interpreted as a line multiplier (24x!) by some readers. I set both on every body paragraph via the `_set_body_format` helper.
- **Table cell paragraphs and `Document.paragraphs`.** The caption table's cell paragraphs do NOT appear in `shared.document.Document.paragraphs`, which iterates `doc.paragraphs` only. That iterator walks the body root, skipping tables. Rules that need caption-block content (e.g., a future "check that the caption cites the correct judge") will need to descend into `doc.tables`. Not a bug in the fixture; just an awareness point for rule authors.

## Stats

- **Paragraphs (body, excluding caption table cells)**: 95
- **Body text characters**: ~21,700
- **Rough page estimate**: ~9 pages of body text at the brief's 2,400 chars/page benchmark (caption adds ~1 additional page). This slightly exceeds the 6-8 target; the content density is consistent with a realistic LS demurrer and I opted not to trim a citation or argument thread to hit the midpoint.
- **File size**: 46,260 bytes.
- **Re-loadable via `shared.document.Document.load`**: confirmed.
