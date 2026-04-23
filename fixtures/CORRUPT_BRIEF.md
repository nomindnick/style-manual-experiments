# Corruption brief — Phase 0.5 fixture corruption

You are Wave C. Your job is to take a clean Wave-A draft and inject a known set of LS Style Manual violations to produce a fixture that the rule engine can be evaluated against. The intentional violations go in a sidecar JSON ground-truth file so we can score Phase-1 rules later.

## Your tools and inputs

1. The clean source .docx (one of `fixtures/draft-eastvale.docx` / `fixtures/draft-sierra-vista.docx`) and its build script (`fixtures/scripts/build_*.py`).
2. `fixtures/seed-citations.verified.md` — the only citations that exist for sure. Hallucinated cites you introduce should NOT be on this list.
3. `fixtures/DRAFT_BRIEF.md` — the LS rules the drafter was asked to follow. The corruption you're injecting violates these rules.
4. `fixtures/VERIFY_BRIEF.md` — the verification spec used in Wave B. This tells you exactly how each rule will be checked, which informs how to plant a violation that the rule will reliably detect.

## Output

Three artifacts, all named after your fixture (`<fixture>` is `kitchen-sink-violations` or `realistic-mixed`):

1. **`fixtures/scripts/build_<fixture>.py`** — start as a copy of your assigned source build script, then modify to inject the violations. Preserve all the clean-doc structure; the diff should be clearly the corrupted bits and nothing else. Add a docstring header explaining what was changed and pointing to the sidecar JSON.
2. **`fixtures/<fixture>.docx`** — the corrupted document, produced by running your build script.
3. **`fixtures/<fixture>.violations.json`** — the ground-truth file (schema below).

## Sidecar JSON schema

```json
{
  "fixture": "<fixture>",
  "source_draft": "fixtures/draft-<source>.docx",
  "build_script": "fixtures/scripts/build_<fixture>.py",
  "description": "<one-line summary of the corruption profile>",
  "violations": [
    {
      "rule_id": "LS-SP-02",
      "severity": "error",
      "paragraph_index": 32,
      "snippet_before": "...exact 30-50 char window from the source draft...",
      "snippet_after":  "...exact 30-50 char window from the corrupted .docx...",
      "description": "Single space between sentences (was two).",
      "verification_hint": "Search for '. The' followed by uppercase in body paragraph 32; the rule should detect a single-space-after-period."
    }
  ]
}
```

Notes on the schema:

- `paragraph_index` is the 0-based index as `shared.document.Document.paragraphs` sees it (caption table is invisible to that accessor; if you corrupt caption text, use `paragraph_index: -1` and add a `location_note` field with the table-cell description).
- `snippet_before` / `snippet_after` are exact text windows so a human can find the violation by grep.
- `severity` is `error`, `warning`, or `info` — match the LS rule's tier of seriousness.
- One JSON entry per discrete violation, even if the same rule_id is violated multiple times.

## What violations to inject — KITCHEN SINK

Target a thorough Phase-1 + neighbor coverage. Aim for ~17 distinct violations across the rules below. **Apply each violation in a different paragraph** so they don't pile up.

| # | Rule | Severity | What to do |
|---|---|---|---|
| 1 | LS-SP-02 | error | Two body paragraphs: collapse `". "` (two spaces) to `". "` (one space) at one inter-sentence break each. Target two different argument paragraphs so the rule has multiple hits. |
| 2 | LS-SP-04 | error | One body paragraph: collapse `":  "` (two spaces after colon) to `": "` (one space). Pick a body-prose colon, not a caption-form colon. |
| 3 | LS-SP-07 | error | One body paragraph: drop the Oxford comma in a `X, Y, and Z` list. (You may need to find a list of three or more to corrupt; the demurrer enumerates causes of action — that's a good target.) |
| 4 | LS-ETAL-01 | error | One occurrence: introduce `Et al.` (capitalized) or `, et al.` (with comma before) somewhere it would naturally appear (after a party name in the caption, or in a string cite). If neither location is plausible, add it to the introduction's party description. |
| 5 | LS-QUOTE-01 | error | One body paragraph that quotes from the complaint: move a closing `."` to `".` (period outside the quotation mark). |
| 6 | LS-QUOTE-02 | error | One occurrence: move `";` to `;"` (semicolon inside quotes). If no natural semicolon-after-quote exists, add a brief sentence with one. |
| 7 | LS-FN-05 | error | The pseudo-footnote marker (`¹`) in the body should currently follow terminal punctuation (`...timely.¹`). Move one instance to *precede* it (`...timely¹.`). |
| 8 | LS-CITE-02 | error | One body paragraph: change one in-paragraph spelling-out of `section` (outside parens) to `§` — for example, "Education Code section 17604" → "Education Code § 17604". |
| 9 | LS-CITE-03 | error | One body paragraph: change one outside-parens `subdivision` to `subd.` — for example, "section 430.10, subdivision (e)" in body text → "section 430.10, subd. (e)". |
| 10 | LS-CITE-06g | error | Introduce `Ibid.` exactly once as a citation sentence, replacing what would have been a short cite. |
| 11 | LS-CITE-07 | error | Introduce one `, et seq.` (comma before `et seq.`) — for example, change `section 17604` to `section 17604, et seq.` in a paragraph that doesn't currently use `et seq.` |
| 12 | LS-CITE-08b | error | Add a superscript on `4th` or `9th` in one reporter token. python-docx: split the run, set `<w:vertAlign w:val="superscript"/>` on the inner run. Pick a citation that isn't load-bearing for other rule checks. |
| 13 | LS-CITE-08d | error | Introduce `supra` in one case short cite — change `(Blank, 39 Cal.3d at p. 318.)` to `(Blank, supra, 39 Cal.3d at p. 318.)`. |
| 14 | LS-CITE-06c | error | Remove italics from one `id.` (the period included). The XML edit: strip `<w:i/>` from that run. |
| 15a | LS-CAP-02 | error | One occurrence: lowercase a clearly defined-term reference. "the District" → "the district" in a body paragraph where it's plainly referring to the named defendant. |
| 15b | LS-CAP-02 | error | One occurrence: capitalize a clearly generic reference. "a school district" → "a school District" in a body paragraph where it's plainly generic. |
| 16 | LS-CAP-05 | error | One occurrence: capitalize `Section` mid-sentence. "section 430.10" → "Section 430.10" in body text (not at sentence start). |
| 17a | LS-CITE-HAL | error | One occurrence: transpose two digits in a real case's volume or page number — e.g., "39 Cal.3d 311" → "39 Cal.3d 313" or "27 Cal.4th 228" → "72 Cal.4th 228". The case name and year stay; the cite no longer resolves on CourtListener. |
| 17b | LS-CITE-HAL | error | One occurrence: invent a wholly fake case — replace a real case citation with `<Plaintiff> v. <Defendant> (year) vol Cal.App.4th page` using a name that is NOT on the seed list. Pick a fact-pattern-plausible name like `Lakeside School Dist. v. Coastal Builders, Inc.` |

That's 18 total violations (15a/15b/17a/17b counted separately). It's OK to skip one if you genuinely can't find a natural place to insert it — note the skip in your report.

## What violations to inject — REALISTIC MIXED

This fixture should look like a real LS draft that went through normal proofreading and missed a few things. Five plausible-typo violations:

| # | Rule | Severity | What to do |
|---|---|---|---|
| 1 | LS-SP-02 | error | Two body paragraphs: single-space between sentences. (Most common typo in LS drafts — well-suited to "realistic.") |
| 2 | LS-CAP-02 | warning | One subtle miss: lowercase one "the District" reference where it should be "the District." Pick a paragraph deep in the argument where the proofreader's eye might glaze. |
| 3 | LS-CITE-02 | error | One paragraph: change one in-parens `(Code Civ. Proc., § 430.10, ...)` to `(Code Civ. Proc., section 430.10, ...)` — the kind of mistake that happens when a writer copies in a sentence-form cite by accident. |
| 4 | LS-CITE-HAL | error | One paragraph: transpose two digits in a single case page number. Subtle — looks like a typo, but the cite no longer resolves. |

That's 5 total. Resist the temptation to add more — the realistic profile is the *low* count.

## Process

1. Read this brief end-to-end.
2. Read your assigned source build script (`fixtures/scripts/build_<source>.py`) and the source .docx structure.
3. Copy the build script to `fixtures/scripts/build_<fixture>.py`. Update its docstring header and `OUTPUT_PATH`.
4. For each violation, edit the build script to introduce the change. Do NOT edit the .docx directly. Keep the diff readable: each violation should be a localized edit in one place in the script. Prefer to keep clean-text constants intact and patch only the small region needed.
5. Run the script with `.venv/bin/python fixtures/scripts/build_<fixture>.py` to produce the .docx.
6. Verify the violations are present:
   - For text violations: `unzip -p fixtures/<fixture>.docx word/document.xml | grep -o '<your snippet>'` should find them.
   - For Document-loader visible violations: `from shared.document import Document; d = Document.load('fixtures/<fixture>.docx'); print(d.paragraphs[<idx>].text)` confirms the snippet.
7. Write `fixtures/<fixture>.violations.json` with one entry per violation per the schema above.
8. Spot-check that you did NOT introduce additional unintended violations beyond the planned list — the ground truth must be complete. Use the same techniques the verifier brief described (grep for `Ibid` / `supra` / `, et seq` / `: ` after sentence terminators / `§` outside parens) to confirm.

## Honesty constraints

- The sidecar JSON must be **complete and accurate**. If you introduce a violation, log it. If you accidentally introduce a violation that wasn't on the planned list, log it too (with a `note: "unplanned"` field) — don't quietly hide it.
- Do not invent fake citations beyond the LS-CITE-HAL entries. Every other citation in the document should remain on the verified seed list.
- Keep the rest of the document intact. The corruption profile is the planned violations and nothing more.

## Report back

When done, report (briefly):
- Confirmation that the build script + .docx + JSON were produced.
- List of injected violations (rule_id + paragraph_index + one-word descriptor).
- Any planned violations you skipped, with reason.
- Any unplanned side-effects you noticed and logged.
- Any places where the brief was ambiguous and you made a judgment call.
