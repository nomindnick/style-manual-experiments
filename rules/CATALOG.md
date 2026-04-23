# Rule Catalog

Every rule identified from the Lozano Smith *Style Manual* (revision dated 2022-12-29). Rules are the unit of implementation. IDs follow `LS-{SECTION}-{NUM}[letter]` and are derived from the manual's own section numbering for traceability.

## Legend

**Tier**
1. Pure text regex / pattern
2. Document-structure (inspects `.docx` XML: font, spacing, indent)
3. Citation + state-tracking (parse cites, maintain defined-term / prior-citation state)
4. Semantic (requires LLM judgment)

**Source**
- `LS` — Lozano Smith-specific rule
- `CSM` — Incorporated from the *California Style Manual* by reference
- `BB` — Incorporated from *The Bluebook* (federal)
- `LS mod` — LS modification of a CSM/BB rule

**Status**
- ⭐ `planned-p1` — Phase 1 MVP rule (one of the four starter rules)
- `planned` — Phase 2 expansion target
- `queued` — Will implement eventually; not prioritized
- `deferred` — Waiting on an open question or upstream decision
- `descoped` — Not implementing; see note
- `implemented` — Shipped

---

## CAP — Capitalization (manual pp. 6–9)

| ID | Rule | Tier | Source | Status |
|---|---|---|---|---|
| LS-CAP-01 | General rule: follow CSM Part A §§ 4.1–4.11 | — | CSM | descoped |
| LS-CAP-02 | Capitalize "district" / "school district" / "board" / "board of education" / "city" / "city council" / "county" / "board of supervisors" and similar when referring to a specific agency; lowercase when generic | 4 | LS | ⭐ planned-p1 |
| LS-CAP-03 | Do not capitalize "legislation" / "legislative"; capitalize "Legislature" when referring to the California Legislature | 4 | LS | planned |
| LS-CAP-04 | Party-substitute designation: a word (e.g., "Plaintiff", "Respondent") may be capitalized when used alone if the full proper name was used earlier and the writer specified the capitalized form for subsequent references | 3 | LS | planned |
| LS-CAP-04a | Client agencies/officials in judicial filings referred to by name, not by party designation | 4 | LS | queued |
| LS-CAP-04b | Opposing parties referred to by substitute designation | 4 | LS | queued |
| LS-CAP-04c | When client is defendant/respondent, preferred designation is "respondent" (not "defendant") | 4 | LS | queued |
| LS-CAP-04d | Designations match between parties (plaintiff ↔ defendant; petitioner ↔ respondent) | 3 | LS | planned |
| LS-CAP-05 | Do not capitalize "part" / "chapter" / "article" / "title" / "section" / "subdivision" except in headings or at beginning of sentence | 3 | CSM | planned |
| LS-CAP-05a | Defined-term exception: `section X` may become capitalized "Section X" if explicitly defined as a term | 3 | LS | queued |
| LS-CAP-06a | Do not capitalize (unless defined per LS-CAP-04): party, defendant, plaintiff, respondent, petitioner, complaint, petition, writ of mandate, superior court, appellate court, court of appeal, court of appeals, court used generically | 3 | LS | planned |
| LS-CAP-06b | Capitalize "Superior Court of ___ County" | 1 | LS | planned |
| LS-CAP-06c | Capitalize "the Court" when referring to the U.S. Supreme Court in federal pleadings | 4 | LS | queued |
| LS-CAP-06d | Capitalize "the Court" when referring to the court for which the pleading is drafted | 4 | LS | queued |

**Notes**
- LS-CAP-01 is descoped because full CSM Part A coverage is out of scope (per PLAN.md); only LS-specific capitalization rules are implemented.
- LS-CAP-02 is Rule 3 in Phase 1. It will share defined-term state with LS-CAP-04: if "District" was defined as a party substitute in a prior paragraph, that is strong evidence the later bare "district" should be capitalized.
- LS-CAP-04 family is complex; only the structural piece (LS-CAP-04, LS-CAP-04d) is planned. The judgment-heavy pieces (LS-CAP-04a/b/c) are queued pending eval work.

---

## FONT — Fonts (manual p. 9)

| ID | Rule | Tier | Source | Status |
|---|---|---|---|---|
| LS-FONT-01 | Times New Roman, 12 pt for all formal work product (unless local rule says otherwise) | 2 | LS | planned |
| LS-FONT-02 | Email: Calibri, 12 pt | 2 | LS | descoped |
| LS-FONT-03 | Emphasis: bold / italics / bold italics preferred; underline used sparingly | 2 | LS | deferred |

**Notes**
- LS-FONT-02 is descoped because emails are out of scope (litigation filings only).
- LS-FONT-03 "sparingly" is not deterministically checkable; deferred pending decision on whether to flag excessive underlining as Tier 4.

---

## SP — Spacing, paragraphs, sentences, ellipses, colons, commas (manual pp. 10–12)

| ID | Rule | Tier | Source | Status |
|---|---|---|---|---|
| LS-SP-01 | Letters / memos: single-spaced, no indent, hard return between paragraphs | 2 | LS | descoped |
| LS-SP-02 | **Two spaces between every sentence (including between substantive and citation sentences)** | 1 | LS | ⭐ planned-p1 |
| LS-SP-03 | Ellipses: three periods (four at end of sentence); single space on each side of each period (exception: word-count compression for court filings) | 1 | LS | planned |
| LS-SP-04 | Two spaces after every colon | 1 | LS | planned |
| LS-SP-05 | Semicolons: may replace period to link closely related independent clauses | 4 | LS | descoped |
| LS-SP-06 | Commas between independent clauses joined by coordinating conjunctions; after introductory clauses/phrases/words | 4 | CSM | descoped |
| LS-SP-07 | Oxford comma required | 1 | LS | planned |
| LS-SP-08 | State trial / federal trial court filings: "Exactly 24 pt" line spacing; 0.5" indent | 2 | LS | planned |
| LS-SP-09 | State appellate / Supreme Court: 1.5 line spacing; 0.5" indent | 2 | LS | planned |
| LS-SP-10 | Federal appellate: double-spaced; 0.5" indent | 2 | LS | planned |

**Notes**
- LS-SP-02 is Rule 1 in Phase 1 — the simplest end-to-end exercise.
- LS-SP-05 / LS-SP-06 descoped as stylistic guidance not reliably checkable.
- LS-SP-08 / LS-SP-09 / LS-SP-10 depend on knowing the court type — see open question in PLAN.md.

---

## FN — Footnotes (manual p. 12)

| ID | Rule | Tier | Source | Status |
|---|---|---|---|---|
| LS-FN-01 | Footnote font matches body (Times New Roman) | 2 | LS | planned |
| LS-FN-02 | Footnote text single-spaced | 2 | LS | planned |
| LS-FN-03 | Court filings: footnote font size matches body | 2 | LS | planned |
| LS-FN-04 | Non-court docs: footnotes normally 12 pt, never below 11 pt | 2 | LS | descoped |
| LS-FN-05 | Footnote marker placement: after clause or sentence, including *after* terminal punctuation | 1 | LS | planned |

**Notes**
- LS-FN-04 descoped because non-court docs are out of scope.

---

## QUOTE — Quotation punctuation (manual p. 12)

| ID | Rule | Tier | Source | Status |
|---|---|---|---|---|
| LS-QUOTE-01 | Periods and commas inside the closing quotation mark | 1 | LS | planned |
| LS-QUOTE-02 | Colons and semicolons outside the closing quotation mark | 1 | LS | planned |
| LS-QUOTE-03 | Question marks / exclamation points: inside if part of original quoted language, outside if not | 4 | LS | deferred |

---

## BLOCK — Block quotations (manual pp. 12–13)

| ID | Rule | Tier | Source | Status |
|---|---|---|---|---|
| LS-BLOCK-01 | Quotations of ≥ 50 words are block-indented 0.5" on both margins and single-spaced | 2 | LS | planned |
| LS-BLOCK-02 | Citation to authority appears *below* the block at the left margin with normal indentation | 2 | LS | planned |
| LS-BLOCK-03 | No outside quotation marks around block-quoted text | 2 | LS | planned |

---

## LIST — Bulleted, numbered, or other lists (manual pp. 13–14)

| ID | Rule | Tier | Source | Status |
|---|---|---|---|---|
| LS-LIST-01 | Lists indented 0.5" on both margins and single-spaced | 2 | LS | planned |
| LS-LIST-02 | If sub-bullets exceed 20 words, hard return between items | 2 | LS | queued |
| LS-LIST-03 | Inline (non-broken-out) lists: `(1)` / `(a)` delineators, items separated by semicolons, penultimate has "or"/"and" following the semicolon, last item concludes with a period | 3 | LS | queued |

---

## WIDOW — Widows and orphans (manual p. 14)

| ID | Rule | Tier | Source | Status |
|---|---|---|---|---|
| LS-WIDOW-01 | No widows or orphans; headings accompanied by ≥ 2 lines of text on the same page | 2 | LS | deferred |

**Notes**
- Without a rendering engine, page breaks are unknown. Reframing as "widow/orphan control enabled in paragraph properties (`w:widowControl`)" is a possible Tier 2 implementation. Decision deferred.

---

## EGIE — E.g. / I.e. (manual p. 14)

| ID | Rule | Tier | Source | Status |
|---|---|---|---|---|
| LS-EGIE-01 | "e.g.," means "for example"; "i.e.," means "that is" — use correctly | 4 | LS | descoped |

**Notes**
- Distinguishing "for example" vs. "that is" from surrounding context is semantic; low value relative to cost. Descoped pending a reason to reconsider.

---

## ETAL — Et al. (manual p. 14)

| ID | Rule | Tier | Source | Status |
|---|---|---|---|---|
| LS-ETAL-01 | "et al." is lowercase with a period only at the end; not preceded by a comma | 1 | LS | planned |

---

## HYPH — Hyphen use (manual pp. 14–15)

| ID | Rule | Tier | Source | Status |
|---|---|---|---|---|
| LS-HYPH-01 | Single hyphen for joining words | 1 | LS | queued |
| LS-HYPH-02 | Double hyphen (en dash equivalent) for separating sentence clauses for emphasis | 1 | LS | queued |

**Notes**
- Detecting "correct" vs. "incorrect" use often requires understanding whether the writer is joining words or emphasizing a clause. Likely flagged as Tier 4 on re-scoping.

---

## CITE — Citations (manual pp. 15–28)

The densest section. Several of these are the Phase-1 focus.

| ID | Rule | Tier | Source | Status |
|---|---|---|---|---|
| LS-CITE-01 | Citation sentences in parens, treated as complete sentences; period *inside* parens (not federal) | 3 | LS | planned |
| LS-CITE-01a | In-sentence citations may be in parens but are not treated as separate sentences; period outside parens at end of sentence | 3 | LS | planned |
| LS-CITE-02 | **"section" spelled out outside parens; `§` inside parens; `§§` for multiple sections** | 3 | LS | ⭐ planned-p1 |
| LS-CITE-02a | Same rule applies to "paragraph" → `¶` | 3 | LS | planned |
| LS-CITE-03 | "subdivision" outside parens; `subd.` inside | 3 | LS | planned |
| LS-CITE-04 | CA codes: comma after "Code" and space before `§`; comma before and after subdivision reference in sentence; comma precedes subdivision when in parens | 1 | LS | planned |
| LS-CITE-04a | Do not abbreviate code titles (no "CCP", etc.) in judicial filings or sentences | 1 | LS | planned |
| LS-CITE-04b | Abbreviations of code sections only in citation sentences, per CSM format | 3 | CSM | queued |
| LS-CITE-05 | Cal. Code Regs.: same format rules as other CA codes | 3 | CSM | planned |
| LS-CITE-05a | Do not abbreviate "Cal. Code Regs." to "CCR" | 1 | LS | planned |
| LS-CITE-06a | "Id." capitalized only when it begins a citation sentence | 1 | LS | planned |
| LS-CITE-06b | "id." used only for citations within parens (within sentence or standalone citation sentence) | 3 | LS | planned |
| LS-CITE-06c | "id." (including the period) always italicized | 1 | LS | planned |
| LS-CITE-06d | The font following "id." is generally not italicized | 1 | LS | planned |
| LS-CITE-06e | "id." not used when the immediately preceding citation sentence has more than one authority, unless all to same code | 3 | LS | queued |
| LS-CITE-06f | Shortest form citation may be used; "id." alone when same page as preceding | 3 | LS | queued |
| LS-CITE-06g | Do not use "ibid." (LS divergence from CSM) | 1 | LS mod | planned |
| LS-CITE-06h | "id." reserved for legal authorities; not used for non-legal (pleadings, transcripts, declarations, RJN, record) except to comply with word/page limits | 3 | LS | queued |
| LS-CITE-07 | "et seq." not preceded by comma, not italicized, lowercase, period only at end; LS uses two "section" references | 1 | LS mod | planned |
| LS-CITE-08a | CSM case citation format: `Case v. Case (year) vol reporter page[, pin]` with italicized case name | 3 | CSM | planned |
| LS-CITE-08b | No superscript on `4th` / `9th` / etc. in reporter or circuit token | 1 | LS | planned |
| LS-CITE-08c | Pin cite to page of opinion included in pleadings (and most other work product) | 3 | LS | queued |
| LS-CITE-08d | Subsequent short cite format `(Silacci, 45 Cal.App.4th at 562.)` — do **not** use `supra` for case short cites | 3 | LS mod | planned |
| LS-CITE-08e | Narrow exception: use `supra` for a case discussed early and returned to after lengthy unrelated discussion | 3 | LS | queued |
| LS-CITE-09 | Westlaw-only citations: include case number, actual date, pin to `*PIN/PAGE CITE` | 3 | LS | queued |
| LS-CITE-09a | Unpublished state appellate Westlaw cases not citable in court documents (except narrow CRC exceptions) | 3 | LS | queued |
| LS-CITE-10 | Admin / labor / arbitration case cites: case name, issuing body + date, case number — per-body format rules (OAH, PERB, EERB, LRRM, LRP, Ops.Cal.Atty.Gen., NLRB, Labor Arbitration Reports) | 3 | LS | queued |
| LS-CITE-11 | Defined case names for short citations required only when (a) multiple cited authorities share a name or (b) short cite name differs from original | 3 | LS | queued |
| LS-CITE-12 | Abbreviations not used in substantive sentences; Bluebook Table 6 is reference for case-citation abbreviations | 3 | BB | queued |
| LS-CITE-13 | Modifications to text (emphasis added, quotations omitted, etc.): follow a comma at end of the citation sentence | 3 | LS | planned |
| LS-CITE-14a | Citation signals italicized in federal filings, not in state | 2 | LS | planned |
| LS-CITE-14b | Comma after italicized signal ("e.g.," / "see, e.g.,") not italicized | 1 | LS | planned |
| LS-CITE-14c | Proper use of signals (`See`, `See also`, `Cf.`, `Contra`, `But see`, etc.) | 4 | BB / CSM | deferred |
| LS-CITE-15 | Explanatory parentheticals: substantive content in brackets, not additional parens; start lowercase and remove extraneous "the" when non-quoting | 3 | LS | queued |
| LS-CITE-16 | Order of cited authority per CSM §§ 1.5, 2.5(c) and Bluebook B1.2 | 3 | CSM / BB | deferred |
| LS-CITE-17 | No hanging signal / `§` / `¶` at end of line | 2 | LS | queued |
| LS-CITE-HAL | **Hallucination check: every extracted citation should resolve to a real authority on CourtListener (or equivalent)** | 3 + external | LS (novel) | ⭐ planned-p1 |

**Notes**
- LS-CITE-02 is Rule 2 in Phase 1. Implementation needs a reliable "inside-parens vs. outside-parens" detector, which may itself justify shared citation-context plumbing used later by LS-CITE-03, LS-CITE-06 family, and others.
- LS-CITE-HAL is Rule 4 in Phase 1 and is the one novel "extension" beyond the manual's rules; it is scoped to "does this citation exist" and does *not* include the deeper "does this case stand for the proposition" check (explicitly out of scope per PLAN.md).
- **Rule 4 scope refinement after Phase 0 eyecite smoke test:** hallucination check covers *case citations only* for Phase 1 (state + federal, including Westlaw-only). Statutory citations, Cal. Code Regs., and PERB / EERB / OAH / LRP administrative decisions appear in the report as "not auto-verified — please confirm manually" until the Phase 2 custom extractor lands. See `smoke-tests/eyecite-ca-cites/FINDINGS.md`.
- LS-CITE-14c (signal appropriateness) is deferred: choosing `See` vs. no-signal vs. `Cf.` requires understanding what the cited authority actually says relative to the text proposition — high-value but high-risk, punted to Phase 2+ evaluation.

---

## RECORD — Citations to the record / court documents (manual pp. 28–30)

| ID | Rule | Tier | Source | Status |
|---|---|---|---|---|
| LS-RECORD-01 | Court filing citations: define short cite on first use; cite to page and line | 3 | LS | queued |
| LS-RECORD-02 | Declaration citations: define short cite on first use; cite to paragraph | 3 | LS | queued |
| LS-RECORD-03 | Request for Judicial Notice: define short cite on first use; cite to exhibit | 3 | LS | queued |
| LS-RECORD-04a | Record abbreviations defined on first use: RT, CT, HT, AR, JA | 1 | LS | queued |
| LS-RECORD-04b | Single-page range within a record: small hyphen (`AR at 110:4-5.`) | 1 | LS | queued |
| LS-RECORD-04c | Cross-page range: em dash / larger hyphen (`JA at 55:2—57:15.`) | 1 | LS | queued |
| LS-RECORD-04d | Multiple volumes: volume number prepends abbreviation (`2HT at 210:4-19.`) | 1 | LS | queued |
| LS-RECORD-05 | Do not use "id." for record citations unless word/page limit forces it | 3 | LS | queued |

---

## FED — Different rules for federal court filings (manual p. 30)

Most of these are court-type variants of existing rules rather than new rules. They are not individually catalogued; instead, rules flagged with "(not federal)" or "(federal only)" carry the distinction in their implementation. Listed for completeness:

- Parentheses do **not** surround citation sentences in federal filings (variant of LS-CITE-01)
- Citation sentences end with a period; don't need to be parenthesized (variant of LS-CITE-01)
- All citation signals italicized (variant of LS-CITE-14a)
- Trailing comma on italicized signal not italicized (LS-CITE-14b — identical)
- Year and court come at end of case citation (Bluebook format — variant of LS-CITE-08a)
- SCOTUS parallel cites may be required (per local rule; Tier 3, `queued`)
- `§` permissible in substantive sentences (variant of LS-CITE-02)
- "subdivision" / `subd.` not required in federal citations of California statutes (variant of LS-CITE-03)

---

## Phase 1 summary

| Phase 1 Rule | Catalog ID | Tier |
|---|---|---|
| 1 — Two spaces between sentences | LS-SP-02 | 1 |
| 2 — Section symbol placement | LS-CITE-02 | 3 |
| 3 — District/Board capitalization | LS-CAP-02 | 4 (LLM) |
| 4 — Citation hallucination check | LS-CITE-HAL | 3 + external |

These four cover every tier of the rule-class spectrum; de-risking them de-risks the architecture.
