# Seed citations — unverified

Seed list of California cases and statutes for the three demurrer fixtures. Every entry below is a **claim that requires verification** before any drafting subagent uses it. The verifier subagent should:

1. For each **case**: query CourtListener's citation-lookup endpoint (`https://www.courtlistener.com/api/rest/v4/citation-lookup/`) with the volume/reporter/page tuple. If a result returns and the case name + year match, mark verified. If anything diverges, mark `needs-fix` with the discrepancy (or `not-found` if the citation does not resolve).
2. For each **statute**: confirm the section number exists by checking leginfo.legislature.ca.gov. (CourtListener doesn't index CA statutes.) Record the exact subdivision letters available so the drafting subagents don't invent subdivisions.
3. Write the verified output to `fixtures/seed-citations.verified.md` with the same structure plus a `status` column.

**No firm content leaves the machine.** Only citation strings + statute identifiers may be sent to external services.

---

## Demurrer standard

| Citation | Proposition |
|---|---|
| Blank v. Kirwan (1985) 39 Cal.3d 311 | On demurrer, all material allegations are accepted as true |
| Aubry v. Tri-City Hospital Dist. (1992) 2 Cal.4th 962 | Demurrer reaches only the face of the complaint and matters subject to judicial notice |
| Schifando v. City of Los Angeles (2003) 31 Cal.4th 1074 | Plaintiff bears burden to show how complaint can be amended |
| Zelig v. County of Los Angeles (2002) 27 Cal.4th 1112 | Court need not accept contentions, deductions, or conclusions of law |
| Code Civ. Proc., § 430.10 | Grounds for demurrer |
| Code Civ. Proc., § 430.30 | Procedure for demurrer |
| Code Civ. Proc., § 430.41 | Pre-demurrer meet-and-confer |

## Public-entity contract validity / void contracts

| Citation | Proposition |
|---|---|
| Miller v. McKinnon (1942) 20 Cal.2d 83 | Contract made in violation of statutory mandate is void; no recovery in quantum meruit |
| Katsura v. City of San Buenaventura (2007) 155 Cal.App.4th 104 | No quantum meruit recovery against public entity for void contract |
| G.L. Mezzetta, Inc. v. City of American Canyon (2000) 78 Cal.App.4th 1087 | Strict compliance with public contracting statutes is jurisdictional |
| First Street Plaza Partners v. City of Los Angeles (1998) 65 Cal.App.4th 650 | Contracts entered without statutory authority are void ab initio |
| Air Quality Products, Inc. v. State of California (1979) 96 Cal.App.3d 340 | No estoppel where public agency exceeds statutory authority |
| Reams v. Cooley (1915) 171 Cal. 150 | Foundational case: contractor cannot recover for work under invalid public contract |

## Estoppel against public entities

| Citation | Proposition |
|---|---|
| City of Long Beach v. Mansell (1970) 3 Cal.3d 462 | Equitable estoppel may be invoked against gov't, but only in unusual circumstances and never to defeat statutory policy |
| Lentz v. McMahon (1989) 49 Cal.3d 393 | Estoppel against gov't unavailable where it would nullify a strong policy adopted for benefit of public |
| Janis v. California State Lottery Com. (1998) 68 Cal.App.4th 824 | Estoppel against public entity rare and limited |

## Public works / extras / quantum meruit

| Citation | Proposition |
|---|---|
| Amelco Electric v. City of Thousand Oaks (2002) 27 Cal.4th 228 | Total cost / abandonment theory unavailable against public entity in absence of express contract terms |
| P&D Consultants, Inc. v. City of Carlsbad (2010) 190 Cal.App.4th 1332 | Written change-order requirements in public contracts strictly enforced |

## Implied covenant / unjust enrichment

| Citation | Proposition |
|---|---|
| Carma Developers (Cal.), Inc. v. Marathon Development California, Inc. (1992) 2 Cal.4th 342 | Implied covenant cannot vary express terms of contract |
| Guz v. Bechtel National, Inc. (2000) 24 Cal.4th 317 | Implied covenant cannot create obligations not in the contract |

## Statutes (Education / Public Contract / Government / Civil)

| Statute | Topic |
|---|---|
| Ed. Code, § 17604 | Board approval of contracts; ratification |
| Ed. Code, § 17605 | Delegation of contracting authority |
| Pub. Cont. Code, § 20111 | School-district bidding threshold |
| Pub. Cont. Code, § 20118.4 | Change orders on school district public works |
| Pub. Cont. Code, § 22300 | Retention substitution / public works |
| Gov. Code, § 815 | Public-entity tort liability requires statute |
| Gov. Code, § 53060 | Special-services contracts of public agencies |
| Civ. Code, § 1550 | Essentials of a contract |
| Civ. Code, § 1565 | Mutual consent |

---

## Notes for the verifier

- Where CourtListener returns multiple matches for a citation tuple, prefer the one whose case name matches; if none match, mark `needs-fix` with the actual returned case name.
- Statute existence is enough; do **not** attempt to verify substantive propositions. The drafting subagents will use these for general topical alignment, not for verbatim quotes.
- If a case fails verification, do not silently substitute. Mark it and let the human (Nick / Claude) decide whether to swap or drop.
- Keep the verified output to the same Markdown structure so a quick diff shows what changed.
