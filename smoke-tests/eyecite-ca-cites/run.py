"""Smoke test: how well does eyecite parse LS-style citations?

Runs eyecite.get_citations() against a curated set of citations spanning:
  - CA Supreme / Court of Appeal in CSM format (year before reporter)
  - CA codes with § notation
  - CA Code of Regulations
  - PERB / EERB decisions
  - OAH decisions (special ed due process)
  - Ops.Cal.Atty.Gen.
  - Federal cases in Bluebook format
  - Westlaw-only federal cases
  - LRP / special-education reporter
  - NLRB and Labor Arbitration Reports

For each, we print: input → what eyecite returned (type + key fields).
"""

from eyecite import get_citations
from eyecite.models import (
    CaseCitation,
    FullCaseCitation,
    ShortCaseCitation,
    SupraCitation,
    IdCitation,
    FullLawCitation,
    FullJournalCitation,
    UnknownCitation,
)

SAMPLES = [
    # (label, input, notes/expectations)
    ("CA Supreme (CSM)",
     "Greyhound Corp. v. Super. Ct. (1961) 56 Cal.2d 355",
     "Year-before-reporter format"),
    ("CA Supreme (CSM) w/ pin",
     "Western States Petroleum Assn. v. Super. Ct. (1995) 9 Cal.4th 559, 574",
     ""),
    ("CA Court of Appeal (CSM)",
     "Cal. School Bds. Assn. v. State Bd. of Ed. (2010) 186 Cal.App.4th 1298",
     ""),
    ("CA Court of Appeal 3d (CSM)",
     "Lawrence v. Bank of Am. (1985) 163 Cal.App.3d 431",
     ""),
    ("CA Court of Appeal 5th (CSM)",
     "Morgado v. City & County of San Francisco (2017) 13 Cal.App.5th 1, 7",
     "Newer reporter; pin cite included"),
    ("CA Code — Gov. Code",
     "(Gov. Code, § 3752.)",
     "Full citation sentence with parens"),
    ("CA Code — multiple sections",
     "(Gov. Code, §§ 66000 et seq.)",
     "§§ and et seq."),
    ("CA Code — subdivision",
     "(Civ. Code, § 1751, subd. (1).)",
     ""),
    ("CA Code — in-sentence",
     "Education Code section 44956 grants rights to certificated employees.",
     "Section spelled out, in-sentence"),
    ("Cal. Code Regs. — full",
     "(Cal. Code Regs., tit. 5, § 74015, Register 98, No. 2 (Jan. 9, 1998) p. 402-21.)",
     ""),
    ("Cal. Code Regs. — subdivision",
     "(Cal. Code Regs., tit. 22, § 1085-2, subd. (a)(2)(A).)",
     ""),
    ("PERB decision",
     "Chula Vista Elementary School District (1997) PERB Decision No. 1232",
     "Administrative body, no conventional reporter"),
    ("PERB w/ PERC pin",
     "Univ. of Cal. Berkeley (Aug. 1, 1984) PERB Dec. No. 420-14, 8 PERC ¶ 15196, p. 910.",
     "Month/day/year + paragraph symbol"),
    ("EERB (pre-1978)",
     "Lompoc Unified School Dist. (EERB 1977) EERB Dec. No. 13, 1 PERC, p. 80.",
     ""),
    ("OAH — special ed",
     "Sacramento City Unified School Dist. (OAH Aug. 12, 2017) Case No. 20170985.",
     "OAH body; case number not reporter"),
    ("Ops.Cal.Atty.Gen.",
     "80 Ops.Cal.Atty.Gen. 203 (1997)",
     ""),
    ("Federal (Bluebook)",
     "Ashcroft v. Iqbal, 556 U.S. 662, 679 (2009)",
     "Year at end"),
    ("Federal 9th Cir.",
     "Barron v. Reich, 13 F.3d 1370, 1374 (9th Cir. 1994)",
     ""),
    ("Federal district (Westlaw-only)",
     "Gunter v. North Wasco County Sch. Dist. Bd. of Ed. (D. Or. Dec. 22, 2021) Case No. 3:21-cv-1661-YY, 2021 WL 6063672, *7-10",
     "CSM-flavored year-parens w/ federal + Westlaw"),
    ("Federal in Bluebook Westlaw",
     "Kheriaty v. Regents of the Univ. of Cal. (C.D. Cal. Dec. 8, 2021) Case No. SACV 21-1367 JVS (KESx), 2021 WL 6298332, *6-7",
     ""),
    ("LRP (special ed reporter)",
     "Los Angeles Unified School Dist. (Aug. 13, 2013) 113 LRP 39561, at 27-28.",
     ""),
    ("NLRB",
     "Otlans Roofing Corp. (1970) 182 NLRB 137 (74 LRRM (BNA) 1447.)",
     ""),
    ("Labor Arbitration",
     "Armstrong Rubber Co. (Jan. 7, 1952) 17 LA 71.",
     ""),
    ("Short cite — Silacci (LS style)",
     "(Silacci, 45 Cal.App.4th at 562.)",
     "LS short-cite form; no supra"),
    ("Id. — simple",
     "(Id.)",
     ""),
    ("Id. — with pin",
     "(Id. at 895.)",
     ""),
    ("Id. — with subdivision",
     "(Id., § 6254, subd. (a).)",
     ""),
]


def kind(cite):
    return type(cite).__name__


def key_fields(cite):
    """Extract the fields that tell us whether eyecite 'got it right'."""
    fields = {}
    if hasattr(cite, "groups") and cite.groups:
        fields["groups"] = dict(cite.groups)
    if hasattr(cite, "metadata") and cite.metadata:
        md = cite.metadata
        for name in ("plaintiff", "defendant", "year", "court", "pin_cite", "extra",
                     "reporter", "volume", "page", "publisher"):
            v = getattr(md, name, None)
            if v:
                fields[name] = v
    if hasattr(cite, "corrected_citation"):
        try:
            fields["corrected"] = cite.corrected_citation()
        except Exception:
            pass
    return fields


def main():
    print(f"eyecite version check via imports ok. Running {len(SAMPLES)} samples.\n")
    rows = []
    for label, text, note in SAMPLES:
        cites = get_citations(text)
        rows.append((label, text, note, cites))
        print("=" * 78)
        print(f"[{label}]")
        print(f"  input: {text}")
        if note:
            print(f"  note : {note}")
        if not cites:
            print("  RESULT: no citations extracted")
        else:
            for c in cites:
                print(f"  -> {kind(c)}: '{getattr(c, 'matched_text', lambda: '?')()}'")
                fields = key_fields(c)
                for k, v in fields.items():
                    print(f"       {k}: {v!r}")

    # Summary pass
    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    for label, text, _, cites in rows:
        ct = len(cites)
        kinds = ", ".join(sorted({kind(c) for c in cites})) or "NONE"
        print(f"  {label:40s}  n={ct:2d}  kinds=[{kinds}]")


if __name__ == "__main__":
    main()
