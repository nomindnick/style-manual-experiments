# LS-CITE-02 — implementation notes

**Manual section:** Citations §2 (p. 16)
**Tier:** 3 (needs paren-depth tracking; no LLM or external services)

## What the rule does

Walks every paragraph twice:

1. **Outside-parens pass.** Every `§` / `§§` at paren-depth 0 is a violation; the fix is the spelled-out word ("section" / "sections").
2. **Inside-parens pass.** Every `section` / `sections` at paren-depth > 0, when followed by a statute-number-shaped token (`\s+\d`), is a violation; the fix is `§` / `§§`.

Paren-depth is computed with a one-pass scan that counts `(` and `[` as openers and `)` and `]` as closers. Brackets participate because LS uses them for sub-references inside citation sentences (LS-CITE-15); e.g., `(Compl., Ex. A [General Conditions, § 9.1].)` — the `§` is at depth 2 and must not fire.

## Why the "section" side has a precision gate and the `§` side does not

`§` is unambiguous. Any out-of-parens occurrence is either the LS violation or a deliberate federal-court deviation (see below). No ambiguous dual-use form exists.

"section" is used for many things: document structure ("Section IV of this brief"), generic references ("this section of the code"), and statutory references (the only shape the rule is about). Requiring a trailing statute-number token (`\d+…`) is the cheapest way to distinguish the statutory case — and a precision win that matches the PLAN operating principle ("precision over recall").

The gate skips:
- `Section IV` — Roman numeral
- `Section A` — letter
- `this section of` — no digit

The gate keeps:
- `section 20118.4` — digit with dotted subsection
- `sections 17604 and 17605` — plural with digit
- `Section 430.10` — case-insensitive

## Paren-depth lives in the rule for now

LS-CITE-03 (subdivision / `subd.`) will need the same inside/outside-parens split. Per the PLAN "second caller" discipline, the helper stays local to this rule until Rule 3 pressure-tests it. At that point, promote `_paren_depth_array` (and possibly a richer "paren spans" view) to `shared/`.

The helper does **not** belong in `shared/eyecite_wrapper.py`. That wrapper is for citation-token spans (suppressing internal periods on `Cal.App.4th`, `U.S.`, etc.). Paren-depth is a different question and should stay separate.

## Court-type assumption

Rule 2 implements **California state-court** behavior. Federal filings permit `§` in substantive sentences per the manual (CATALOG note under LS-CITE-02 in the FED-variant section). This implementation would flag a legitimate federal `§` in running prose as a violation.

Deferred until `court_context` plumbing lands (PLAN open question #6). The Phase-0.5 fixtures are all CA superior-court demurrers; no federal fixture exists yet to pressure-test the deviation.

## Edge cases considered

- **`§` inside brackets (`[… § 9.1 …]`).** Brackets count as openers, so depth > 0 and the symbol is "inside parens." Confirmed against `clean.docx ¶31` (contract-clause sub-reference inside a citation sentence).
- **Nested parens with subdivisions (`§ 20118.4, subd. (a)`).** `subd.` is LS-CITE-03's concern; this rule only fires on the `§` / `section` tokens. In `(Pub. Cont. Code, § 20118.4, subd. (a).)` the `§` lives at depth 1 (valid) and we never inspect `(a)`.
- **Multiple `§§` vs single `§`.** Detected by run length on the regex match; fix suggestion matches: `§` → `section`, `§§` → `sections`.
- **Case on "section" word.** Match is case-insensitive; the fix preserves the singular/plural form of the matched word (`section` / `sections`). Capital-S at sentence start doesn't matter under this rule — LS-CAP-05 is the capitalization rule.
- **Mismatched parens.** Depth is clamped at zero so a stray closing `)` doesn't produce negative depth. A malformed paragraph doesn't crash the rule.
- **`¶` / "paragraph".** LS-CITE-02a handles these. Rule 2 ignores them entirely.

## False-positive surface that future fixtures may surface

- **`§` in a federal filing substantive sentence.** Will fire as a violation today; needs `court_context` to silence.
- **`sec.` / `§ 9` without a dot-digit continuation.** `\s+\d` matches a single digit, so `section 9` still fires inside parens — correct. But abbreviated forms like `Sec. 9` don't use the word "section" and are handled by LS-CITE-04b.
- **Section numbers with a leading letter (`section A.1`).** Rare in CA statutes; not covered by the gate. If a fixture surfaces this, loosen the lookahead to `(?=\s+[A-Z0-9])` and revisit.
- **Unicode `⁋` or other pilcrow/section-like glyphs.** Only matches literal `§` (U+00A7). If other glyphs appear, extend the regex.

## Test layout

`test_rule.py` runs from the repo root. Synthetic tests exercise both directions plus the precision gate and bracket/paren mechanics. Integration tests assert exact paragraph indices against each fixture's `*.violations.json` sidecar.

- `clean.docx`: zero findings (includes `[General Conditions, § 9.1]` and dozens of valid `section X` / `(§ X)` uses — good coverage of the negative side).
- `kitchen-sink-violations.docx`: ¶69 (single `§`-in-prose violation; same paragraph also contains a valid `(§ 20118.4.)` which must not fire).
- `realistic-mixed.docx`: ¶60 ("section"-inside-parens violation; same paragraph also contains a valid "Public Contract Code section 20118.4" in prose which must not fire).
