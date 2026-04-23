# Drafting brief — Phase 0.5 demurrer fixtures

This brief is the source of truth for the three Wave-A drafting subagents. Each subagent gets one variation (Westlake / Eastvale / Sierra Vista) and produces one clean .docx. Read this entire file before you start.

## Goal

Produce a `.docx` that **looks like a real Lozano Smith demurrer in California superior court** and that **conforms exactly to the LS Style Manual's published rules** (so the rule-checker has a true negative to compare against). Anyone reading the output should think "this is a competently-written demurrer" — not "this is a synthetic fixture."

## Output

For your variation `<name>` (one of `westlake`, `eastvale`, `sierra-vista`):

1. **Build script** at `fixtures/scripts/build_<name>.py` — uses `python-docx` to construct the document. The script is the source; we check it in alongside the .docx so future edits are reviewable.
2. **Document** at `fixtures/draft-<name>.docx` — produced by running the script.
3. **Notes** at `fixtures/draft-<name>.NOTES.md` — short. Record: (a) which seed citations you used, (b) any LS rule where the manual was ambiguous and you made a judgment call, (c) any python-docx quirks worth flagging.

Run the script with `.venv/bin/python fixtures/scripts/build_<name>.py` from the repo root. Confirm the .docx file is created (size > 0 and python-docx can re-open it). Do **not** commit changes — just produce the artifacts.

## Length

**6–8 pages of body text** (excluding caption). Aim for the upper end. Real demurrers are not short.

## Document structure

Standard CA trial-court demurrer:

1. **Caption block** — court (Superior Court of California, County of <County>), case number (use realistic-looking but fictional like `Case No. 30-2025-01234567`), parties, document title (`DEMURRER TO PLAINTIFF'S COMPLAINT; MEMORANDUM OF POINTS AND AUTHORITIES IN SUPPORT THEREOF`), hearing date/time/dept, judge, action filed date, trial date, attorneys-of-record block.
2. **NOTICE OF DEMURRER AND DEMURRER** — short formal section: notice of hearing, demurrer language ("Defendant <DISTRICT> hereby demurs to the Complaint of plaintiff <CONTRACTOR> on the following grounds:"), enumerated grounds tied to Code Civ. Proc., § 430.10 subdivisions.
3. **MEMORANDUM OF POINTS AND AUTHORITIES** — heading, then:
   - **I. INTRODUCTION** (1–2 paragraphs framing the dispute and the demurrer's thrust)
   - **II. STATEMENT OF FACTS / RELEVANT ALLEGATIONS** (1.5–2 pages summarizing the plaintiff's complaint allegations — drawn from your variation's fact pattern; cite to ¶s of the complaint)
   - **III. LEGAL STANDARD** (the demurrer-standard cases — Blank, Aubry, Schifando, Zelig)
   - **IV. ARGUMENT** with three subheadings (one per inappropriate cause of action your variation involves) — each subheading ~1.5 pages with case + statute citations
   - **V. CONCLUSION** (short — 1 paragraph)
4. **Signature block** at the end with attorney name, bar number (fictional, e.g., `SBN 234567`), firm (`LOZANO SMITH`), and date.

## LS Style Manual conformance — what to do

Every rule below is one the verifier will check. **Get all of them right.**

### Formatting (Tier 2)

- **Font**: Times New Roman 12pt for everything (body, headings, footnotes, caption). Apply to runs, not just style — python-docx's defaults are not TNR. Set `run.font.name = 'Times New Roman'` and `run.font.size = Pt(12)` on every run, including caption and footnote runs.
- **Line spacing**: Exactly 24 pt for body paragraphs. In python-docx: `paragraph.paragraph_format.line_spacing = Pt(24)` and `paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY`.
- **First-line indent**: 0.5" on body paragraphs (`paragraph.paragraph_format.first_line_indent = Inches(0.5)`). Do **not** indent headings or block quotes.
- **Footnote** font: Times New Roman 12pt (matches body for court filings — LS-FN-03). Footnote text single-spaced (LS-FN-02).
- **Block quotes** (≥ 50 words, at least one in your draft): indented 0.5" both margins, single-spaced, no surrounding quotation marks; citation appears on its own line below the block at the left margin with normal indentation (LS-BLOCK-01/02/03).

### Spacing / punctuation (Tier 1)

- **Two spaces between sentences** — every sentence terminator (`. ` / `! ` / `? `) followed by a new sentence gets two spaces. Includes between a substantive sentence and a following parenthetical citation sentence.
- **Two spaces after every colon** when the colon is followed by more text on the same line.
- **Oxford comma** required.
- **"et al." / "et seq."** — both lowercase, period only at end, not italicized.

### Citations (Tier 3)

CSM format (state court):

- **Case format**: *Case Name v. Case Name* (year) vol reporter page[, pin]. Italicize the case name. Year before reporter, in parens. Examples drawn from the verified seed:
  - First cite: `Blank v. Kirwan (1985) 39 Cal.3d 311, 318.` (italicize "Blank v. Kirwan")
  - Short cite: `(Blank, supra, 39 Cal.3d at p. 318.)` — wait, **LS does not use `supra` for case short cites.** LS short-cite form is: `(Blank, 39 Cal.3d at p. 318.)` (LS-CITE-08d). Use that form.
- **No superscript** on `4th`, `9th`, etc. — write `Cal.App.4th`, not `Cal.App.4ᵗʰ`. python-docx does not superscript by default; fine. Do not enable superscript.
- **§ vs. "section"**: `§` only inside parens; spell out `section` outside parens. `§§` for multiple sections. Same for `subd.` (inside parens) vs. `subdivision` (outside). Same for `¶` (inside parens) vs. `paragraph` (outside).
- **"id." conventions**:
  - Italicize "id." including the period.
  - Use lowercase "id." inside parens; capitalize "Id." only when it begins a citation sentence (i.e., a standalone parenthesized citation sentence).
  - Text after "id." is not italicized.
  - Do **not** use "ibid." — LS forbids it.
- **Code citations** in citation sentences:
  - In citation sentences (in parens): `(Code Civ. Proc., § 430.10, subd. (e).)` — comma after "Code", space before §, comma between section and subdivision.
  - In substantive sentences (outside parens): "Code of Civil Procedure section 430.10, subdivision (e)" — spell out "section" / "subdivision"; LS allows the abbreviated code title in citation sentences but not in the running text. **Practical compromise**: in body text either spell out the code name fully ("Code of Civil Procedure section 430.10") OR use the abbreviated form when followed by a section number (LS-CITE-04a forbids bare abbreviations like "CCP" without the section). When in doubt, spell it out.
- **Citation sentences in parens with period inside**:
  - `(Blank v. Kirwan (1985) 39 Cal.3d 311, 318.)` — note the period is inside the closing paren.
  - When the citation is mid-sentence (in-sentence cite), the period goes outside the parens at end of the host sentence.

### Capitalization (Tier 4 — the LS-specific stuff)

- **Defined party-substitute** for the client: "the District" capitalized when referring to the specific defendant client (e.g., "Westlake Unified School District" introduced on first reference, then "(the 'District')", then "the District" everywhere after — capitalized).
- **Plaintiff** as a party-substitute designation: capitalize "Plaintiff" / "Plaintiff's" when used as a party substitute (LS practice for opposing parties is the substitute designation, not the proper name).
- **Lowercase generic** terms when not referring to the specific party: "a school district" (generic), "the district court" (generic court reference), etc.
- **Lowercase**: "court" generic, "demurrer", "complaint", "section", "subdivision", "paragraph", "chapter", "title" (except in headings or at the start of a sentence).
- **Capitalize**: "Court" when referring to the specific superior court for which the pleading is drafted; "Superior Court of [County] County" when written out as a proper name; "Legislature" (when CA Legislature); "Constitution" when referring to a specific constitution.
- **Headings** are in ALL CAPS bold (typical for LS). They count as headings, so capitalization rules don't apply inside them.

### Quotation punctuation (Tier 1)

- Periods and commas **inside** the closing quotation mark.
- Colons and semicolons **outside** the closing quotation mark.

### Footnote markers (Tier 1)

- Footnote markers go *after* terminal punctuation (e.g., `... was timely.¹`, not `... was timely¹.`).

## Citation usage — hard rules

1. **Use only citations from `fixtures/seed-citations.verified.md`.** Do not invent any new case names, volume/reporter/page numbers, or statute sections. The seed list was verified against CourtListener and leginfo specifically so the clean draft has zero hallucinated cites.
2. **Honor the subdivision-shape notes** at the bottom of the verified file. Do not write `Ed. Code, § 17604, subd. (a)` — that section has no lettered subdivisions. Same for Ed. Code § 17605, Gov. Code § 53060. For Civ. Code §§ 1550 and 1565, the structure is numbered clauses (`1.`, `2.`, ...), not lettered subdivisions; cite as `Civ. Code, § 1550` (optionally referencing a clause in text).
3. **Do not fabricate verbatim quotes from cited cases.** The verifier confirmed the cases exist; it did not extract their text. Paraphrase propositions and cite generally — do not put words in quotation marks attributed to a court.
4. **Acceptable verbatim quoting**: from CA statutes (the leginfo text is public and you can cite to its plain language at a high level — but if you must quote, keep it short and verifiable; safer to paraphrase) and from the *plaintiff's complaint* (which is the document being demurred to — those allegations are what you wrote in your fact pattern).
5. **Block quote**: include at least one. Sourcing options that are safe:
   - A statutory excerpt (verified short text from leginfo that you've checked) — keep brief.
   - Or — preferred and safer — a quoted **allegation from the plaintiff's complaint** that you write yourself (since the complaint is the demurrer's target, you control its text). Format with `(Compl., ¶ 14.)` or similar citation below the block.
6. **Use a variety of citation forms** so the rules have things to check: full first-cite, LS short-cite (`(Blank, 39 Cal.3d at p. 318.)`), `id.`, parenthetical citation sentence, in-sentence citation, statute cite with subdivision (only where subdivisions exist), `et seq.`

## Variation-specific facts

You will be told in your spawn prompt which variation is yours. Each variation has:

- **Defendant district** (your client) — full name + short defined-term form.
- **Plaintiff contractor** (opposing party) — full name + short defined-term form.
- **Project type** — what the contract was for.
- **Theories pleaded** — three or four causes of action you'll demur to.
- **Demurrer thrust** — the key reasons each theory fails as to a school district.

Invent realistic-but-fictional supporting details: county, hearing department, dates, dollar amounts, contract numbers, board resolution numbers. Keep dates within the last 18 months (today is 2026-04-23). Do not use real California school district names other than the one assigned (the assigned names are fictional composites).

## Process

1. Read this brief end-to-end.
2. Read `/home/nick/Projects/style-manual-experiments/fixtures/seed-citations.verified.md`.
3. Read `/home/nick/Projects/style-manual-experiments/shared/document.py` to confirm what your output will be parsed as (so you know what metadata the rule engine cares about).
4. Glance at `/home/nick/Projects/style-manual-experiments/source-docs/StyleManual.pdf` if anything in this brief is unclear — the manual is firm IP and stays local; do not transmit it anywhere.
5. Write `fixtures/scripts/build_<name>.py`. Structure it readably (helper functions for caption / heading / body paragraph / block quote / footnote).
6. Run it with `.venv/bin/python fixtures/scripts/build_<name>.py`.
7. Confirm the output by re-loading it via `.venv/bin/python -c "from shared.document import Document; d = Document.load('fixtures/draft-<name>.docx'); print(len(d.paragraphs), 'paragraphs'); print(d.text[:500])"`.
8. Write `fixtures/draft-<name>.NOTES.md` (short — see Output section).
9. Report back: paragraph count, approximate page estimate (you can sanity-check by computing total characters / ~2400 chars per page at TNR 12 / 24pt-line — rough but useful), citations used (list them), any rules you weren't sure about.
