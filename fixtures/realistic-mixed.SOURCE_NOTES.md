# Sierra Vista draft — notes

Drafting notes for `draft-sierra-vista.docx`. Companion to `scripts/build_sierra-vista.py`.

## Seed citations used

All citations come from `fixtures/seed-citations.verified.md`. Nothing invented.

### Cases (17 of 17 from the seed list)

| Cite | Where used |
|---|---|
| *Blank v. Kirwan* (1985) 39 Cal.3d 311 | Legal standard |
| *Aubry v. Tri-City Hospital Dist.* (1992) 2 Cal.4th 962 | Legal standard |
| *Schifando v. City of Los Angeles* (2003) 31 Cal.4th 1074 | Legal standard; conclusions to each section |
| *Zelig v. County of Los Angeles* (2002) 27 Cal.4th 1112 | Legal standard |
| *Miller v. McKinnon* (1942) 20 Cal.2d 83 | Argument IV.A (account stated) and IV.C (estoppel summation) |
| *Reams v. Cooley* (1915) 171 Cal. 150 | Argument IV.A |
| *Katsura v. City of San Buenaventura* (2007) 155 Cal.App.4th 104 | Argument IV.A and IV.C |
| *G.L. Mezzetta, Inc. v. City of American Canyon* (2000) 78 Cal.App.4th 1087 | Legal standard; IV.A; IV.B |
| *First Street Plaza Partners v. City of Los Angeles* (1998) 65 Cal.App.4th 650 | Legal standard; IV.A; IV.B |
| *Air Quality Products, Inc. v. State of California* (1979) 96 Cal.App.3d 340 | Argument IV.C |
| *Amelco Electric v. City of Thousand Oaks* (2002) 27 Cal.4th 228 | Argument IV.A |
| *P&D Consultants, Inc. v. City of Carlsbad* (2010) 190 Cal.App.4th 1332 | Argument IV.A |
| *City of Long Beach v. Mansell* (1970) 3 Cal.3d 462 | Argument IV.C (lead case) |
| *Lentz v. McMahon* (1989) 49 Cal.3d 393 | Argument IV.C |
| *Janis v. California State Lottery Com.* (1998) 68 Cal.App.4th 824 | Argument IV.C |
| *Carma Developers (Cal.), Inc. v. Marathon Development California, Inc.* (1992) 2 Cal.4th 342 | Argument IV.B (lead case) |
| *Guz v. Bechtel National, Inc.* (2000) 24 Cal.4th 317 | Argument IV.B |

### Statutes (9 of 13 from the seed list)

Used: Code Civ. Proc. §§ 430.10, 430.30; Ed. Code §§ 17604, 17605; Pub. Cont. Code §§ 20111, 20118.4; Gov. Code § 53060; Civ. Code §§ 1550, 1565.

Not used (not germane to this fact pattern): Code Civ. Proc. § 430.41 (meet-and-confer declaration is referenced in notice but not cited by section); Pub. Cont. Code § 22300 (retention substitution); Gov. Code § 815 (tort immunity — no tort claim here).

### Subdivision-shape notes honored

- `Ed. Code, § 17604` / `§ 17605` — cited without `subd. (...)`; none exists.
- `Gov. Code, § 53060` — cited without `subd. (...)`; none exists.
- `Civ. Code, §§ 1550, 1565` — cited bare; the statutes use numbered clauses, not lettered subdivisions.
- `Pub. Cont. Code, § 20118.4` — used `subd. (a)` and `subd. (b)`, both of which the seed confirms exist.
- `Code Civ. Proc., § 430.10` — used `subd. (e)` and `subd. (f)`; seed confirms subdivisions (a)–(h).

## LS rule judgment calls

Where the brief was ambiguous or where python-docx forced a choice:

1. **"Two spaces after every colon"** — applied to colons followed by running text (e.g., "The Complaint pleads three causes of action against the District:  (1)..."). Did *not* apply to caption-block label colons like `Date: June 18, 2026` — those read as data-label colons rather than sentence-colons, and a double space there would look off in the caption grid. If the rule-checker flags those as false positives, that's a good calibration signal for Phase 1.
2. **Argument subheadings (IV.A / IV.B / IV.C)** — wrote them as left-aligned, ALL-CAPS bold single paragraphs (e.g., `"A.  THE FIRST CAUSE OF ACTION FOR ACCOUNT STATED FAILS BECAUSE..."`). The brief specifies ALL-CAPS bold for top headings but doesn't explicitly address sub-argument headings. I kept them ALL-CAPS bold, left-aligned, for consistency.
3. **Block quote** — sourced from Plaintiff's own complaint (the safer route the brief recommended). Placed citation on its own line at the left margin with `first_line_indent = 0` and restored the normal body-text line-spacing (exactly-24) for the citation line, while the block itself is single-spaced per LS-BLOCK-02.
4. **"(Id., §§ 7.3, 9.1.)"** — used `Id.` italicized (including the period) as the first word of a citation sentence. That follows the brief's LS convention (`Id.` capitalized only at the start of a citation sentence).
5. **Caption grid** — rendered as a single two-column python-docx table with a horizontal rule line (`_______________`) in the left column per typical CA Superior Court caption style. The brief didn't specify grid vs. bar, so I went with the visually-cleaner grid; python-docx draws clean borders only via direct XML manipulation, so I let the table default to no borders and added an underscore line instead. Works visually, avoids XML surgery.

## python-docx quirks worth flagging

1. **Line spacing storage** — `paragraph_format.line_spacing = Pt(24)` writes `<w:spacing w:line="480" w:lineRule="exact"/>` correctly (480 twentieths of a point = 24 pt). However, `shared.document.Document` reads this back as `304800.0` (EMU value) because `Length` is a subclass of `int` and the `isinstance(_, (int, float))` branch in `_build_paragraphs` short-circuits the `.pt` access. Raw XML confirms the file is correct; it's a shared-wrapper normalization bug, not a fixture bug. Worth fixing in `shared/document.py` when Rule 1 (Tier 2 formatting) lands.
2. **Run-level font assignment** — python-docx sets `rFonts` attributes via `style.font.name` but only for the ASCII variant. The build script sets all four (`ascii`, `hAnsi`, `cs`, `eastAsia`) via direct XML to prevent Word from substituting another face for any codepoint range.
3. **Default paragraph spacing** — python-docx's Normal style ships with `space_after = 8pt` which throws off exact-24-pt line spacing between paragraphs. Every helper in the build script explicitly sets `space_before = space_after = Pt(0)`.
4. **Table cell first paragraph** — you can't `cell.add_paragraph()` for the first line without ending up with a blank leading paragraph; use `cell.paragraphs[0]` for the first line instead.

## Approximate size

- 97 paragraphs (includes caption/notice/signature — the caption table adds additional nested paragraphs not counted here).
- 38 body paragraphs with exact-24 line spacing and 0.5" first-line indent.
- ~20,200 chars of body text.
- Rough page estimate: ~8–9 pages of body text (within or just above the 6–8 target; Word's actual pagination typically lands lower than the chars/line heuristic because of ragged-line padding).
- Total filing with caption + notice + signature: ~11 pages.

## v2 addendum — Wave-B verifier fix-ups

Applied in response to `draft-sierra-vista.VIOLATIONS.md`:

1. **LS-CITE-07** — deleted the comma before `et seq.` in the closing account-stated paragraph (`…Public Contract Code section 20118.4 et seq.`). Confirmed zero `, et seq.` occurrences remain in the draft.
2. **LS-CAP-02 (Board)** — capitalized "Board" in all five flagged instances where the antecedent is unambiguously the District's own governing Board (¶¶32, 38, 41, 61, 63 of the verifier's numbering). The two remaining lowercase "governing board" uses live in the generic paragraph describing Ed. Code §§ 17604/17605 as a statutory concept, which the verifier expressly treated as non-findings; left them lowercase.
3. **LS-CITE-08a (pin cites)** — added pin cites to the two bare first cites:
   - `Amelco Electric v. City of Thousand Oaks (2002) 27 Cal.4th 228, 234, 242–243` — and dropped the now-redundant immediately-following `(Id. at pp. 234, 242–243.)` short cite.
   - `City of Long Beach v. Mansell (1970) 3 Cal.3d 462, 493, 496–497` — and dropped the now-redundant immediately-following `(Mansell, 3 Cal.3d at pp. 493, 496–497.)` short cite. Subsequent short cite to `Mansell` at p. 496 in the IV.C summation paragraph remains and is consistent with the first-cite pin range.
4. **LS-SP-04 (info, not required)** — left as-is. The single-space after `Telephone:` / `Facsimile:` in the attorney-info header reads as form-field label spacing, parallel to the caption-table labels that the verifier brief explicitly carved out. If a future rule-checker flags it anyway, it's a good false-positive calibration signal.

Near-regression caught during fixes: when removing the Mansell short cite, I initially replaced it with `(Ibid.)` — which LS forbids. Caught before commit; replaced with a comma-joined subordinate clause (`, in which the Supreme Court…`) that keeps the prose flowing without introducing a short-cite sentence at all.

No downstream citations broken. Post-fix verification: zero `, et seq.`, zero `supra`, zero `ibid`, zero disallowed subdivision forms, both first cites carry pins, and body text is ~20,200 chars (~8.5 body pages).
