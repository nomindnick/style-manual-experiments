# eyecite smoke test — findings

**Library:** eyecite 2.7.6 (installed 2026-04-23)
**Samples:** 27 citations spanning LS-style state, federal, statutory, administrative, short-form, and `Id.` cites
**Script:** `run.py`

## Verdict in one line

**eyecite handles LS-style *case citations* well in both CSM (year-before-reporter) and Bluebook (year-at-end) formats. It does not parse CA statutory citations beyond flagging the `§` symbol, and it does not know about PERB / EERB / OAH / LRP administrative reporters at all.**

## What works

| Citation type | Example | Result |
|---|---|---|
| CA Supreme (CSM) | `Greyhound Corp. v. Super. Ct. (1961) 56 Cal.2d 355` | `FullCaseCitation` with volume/reporter/page/year and both party names extracted |
| CA Court of Appeal (all series 2d-5th) | `Cal. School Bds. Assn. v. State Bd. of Ed. (2010) 186 Cal.App.4th 1298` | Same — parses cleanly |
| Pin cites | `(1995) 9 Cal.4th 559, 574` | `pin_cite: '574'` captured |
| Federal Bluebook | `Ashcroft v. Iqbal, 556 U.S. 662, 679 (2009)` | `court: 'scotus'` inferred |
| Federal 9th Cir. | `Barron v. Reich, 13 F.3d 1370, 1374 (9th Cir. 1994)` | `court: 'ca9'` inferred |
| Federal Westlaw | `2021 WL 6063672, *7-10` | Extracted as FullCaseCitation with pin |
| LS short-cite | `(Silacci, 45 Cal.App.4th at 562.)` | `ShortCaseCitation` ✓ |
| NLRB | `182 NLRB 137` | Treated as FullCaseCitation |
| Labor Arbitration | `17 LA 71` | Treated as FullCaseCitation |
| Ops.Cal.Atty.Gen. | `80 Ops.Cal.Atty.Gen. 203 (1997)` | Parses cleanly |

## What works poorly

**CSM year-parens + Westlaw federal** — when the LS/CSM style year-in-parens is combined with a Westlaw federal cite, eyecite pulls the defendant name wrong, concatenating court + date + case number into the defendant field:

```
input:  Gunter v. North Wasco County Sch. Dist. Bd. of Ed. (D. Or. Dec. 22, 2021) Case No. 3:21-cv-1661-YY, 2021 WL 6063672, *7-10
output: defendant = 'D. Or. Dec. 22, 2021) Case No. 3:21-cv-1661-YY'
```

The Westlaw volume/reporter/page + pin are still correct, so the citation is usable for CourtListener lookup — but party-name metadata can't be trusted in this form.

## What does not work

| Citation type | Example | eyecite output |
|---|---|---|
| CA statute with § | `(Gov. Code, § 3752.)` | `UnknownCitation: '§'` — the code name and section number are **not** captured as structured fields |
| CA statute `§§` | `(Gov. Code, §§ 66000 et seq.)` | Same — just `§§` |
| CA statute with subdivision | `(Civ. Code, § 1751, subd. (1).)` | Same |
| CA statute in-sentence | `Education Code section 44956...` | **No citation extracted** — eyecite needs `§` |
| Cal. Code Regs. | `(Cal. Code Regs., tit. 5, § 74015, Register 98...)` | `UnknownCitation: '§'` |
| PERB / EERB decisions | `PERB Decision No. 1232`, `EERB Dec. No. 13` | **No citation** — reporter unknown |
| OAH decisions | `(OAH Aug. 12, 2017) Case No. 20170985.` | **No citation** |
| LRP special-ed reporter | `113 LRP 39561` | **No citation** — reporter unknown |
| `(Id.)`, `(Id. at 895.)` standalone | `(Id.)` | **No citation** — eyecite `Id.` detection is context-dependent; needs a prior citation to attach to |

## Implications for Rule 4 (`LS-CITE-HAL`, hallucination check)

**Viable path for Phase 1:** scope the hallucination check to *case citations* only. eyecite reliably extracts them, and CourtListener's citation-lookup endpoint accepts volume/reporter/page and returns canonical case data (or nothing, which is the hallucination signal).

**Flagged as "not auto-verified" for Phase 1:**
- California statutory citations (Gov. Code, Ed. Code, Civ. Code, Penal Code, Code Civ. Proc., etc.)
- California Code of Regulations
- PERB / EERB / OAH / LRP administrative decisions
- Labor Arbitration Reports
- `id.` / `ibid.` short references

**Phase 2 custom extractor work:** Add regex-based extractors for CA statutes (the surface pattern is very consistent: `<Code-name> Code, § <number>[, subd. (X)]` or `<Code> Code § <number>`) and for PERB / EERB / OAH / LRP decisions. Independent code sections can be validated against the official Cal.gov sources (the statutes exist online in a queryable form). Administrative decisions are harder — likely "flag but don't verify."

**`Id.` context-tracking:** eyecite *does* link `Id.` references when they appear in a longer text alongside a prior full citation. The smoke test here fed `(Id.)` standalone and got nothing — not a bug. Confirm this behavior when Rule 4 / Rule 3 (id. tracking) comes up; write a second smoke test with a paragraph-length input.

## Recommendation

**No plan change to the four Phase 1 rules is required.** eyecite is fit for purpose for the case-citation extraction Rule 4 needs. The scope of Rule 4 is refined to: "case citations only for MVP; non-case authorities surfaced as 'not auto-verified' in the report so the user knows what was and wasn't checked."

**Phase 2 task added:** custom CA-statute / CA-regs / admin-decision extractor.
