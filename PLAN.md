# LS Style Manual Checker — Plan

*This repo (`style-manual-experiments`) is the prototyping ground for a locally-run tool that reviews Lozano Smith litigation drafts for compliance with the LS Style Manual and flags potentially hallucinated citations. The MVP with a front end will live in a separate repo, built on the engine proven here.*

---

## Goal

A local reviewer that ingests a draft litigation filing (.docx) and emits a report of LS Style Manual violations plus a hallucinated-citation check. Inspired for the citation-validation piece by [anseljh/prefiling-check-poc](https://github.com/anseljh/prefiling-check-poc), which uses `eyecite` + the CourtListener API.

## Demo target

The first real reader is the litigation partner who authored the LS Style Manual. If he finds it valuable, he has the pull to put it on his and his legal assistant's machines, which opens the path to institutional uptake and eventually a Microsoft Word add-in.

---

## Scope

**In scope**
- Litigation filings (state trial, state appellate, federal trial, federal appellate)
- Four starter rules chosen to exercise every rule tier (see *Phasing*)
- Plain-text report output (engine first; better presentation later)
- California Style Manual cite format for state work, Bluebook for federal
- Fully local execution; Ollama for LLM-based rules; CourtListener API is the single approved external call and only for citation strings

**Out of scope (explicit)**
- Tracked-changes .docx output — deferred; `python-docx` doesn't natively support `w:ins`/`w:del`, and the yak-shave isn't justified in the experiment phase
- Microsoft Word add-in — Phase 3 of the broader roadmap, not this repo
- Full *California Style Manual* coverage — this tool is a *first line of defense*, not a replacement for human review
- Deep "does this case actually stand for the proposition" check — materially different problem class, parked
- Non-litigation document types (letters, memos, emails, CNBs)

---

## Architecture sketch

```
.docx  →  shared/document.py  (text + paragraph metadata)
       →  rules/NN-slug/rule.py  (each emits Finding[] via shared/rule_base.py)
            ├── Tier 1  regex / pure-text rules
            ├── Tier 2  document-structure rules (font, spacing, indent)
            ├── Tier 3  citation + state-tracking rules  (uses shared/eyecite_wrapper.py)
            └── Tier 4  semantic rules                   (uses shared/ollama_client.py)
       →  shared/report.py  (renders Finding[] → text; HTML later)
```

Key seams (not all implemented in Phase 0):

| Module | Purpose | When built |
|---|---|---|
| `shared/finding.py` | `Finding` dataclass, JSON-serializable — the common contract every rule emits and every renderer consumes | Phase 0 |
| `shared/rule_base.py` | Rule interface: `check(Document) -> list[Finding]` | Phase 0 |
| `shared/document.py` | `.docx` loader exposing text, paragraphs, per-paragraph style metadata | Phase 0 (minimal) |
| `shared/report.py` | Plain-text renderer over `list[Finding]` | Phase 0 (minimal) |
| `shared/ollama_client.py` | Thin Ollama wrapper with structured-output support | When Rule 3 needs it |
| `shared/eyecite_wrapper.py` | Adapter over eyecite returning `CitationSpan(paragraph_index, char_start, char_end, kind)` so other rules can ignore character ranges that fall inside a citation | Rule 1 (Phase 1) — pulled forward from "when Rule 4 needs it" so Tier-1 text rules can suppress citation-internal false positives (`Cal.App.4th`, `U.S.`, etc.) |
| `shared/court_listener.py` | Citation-string lookup client | When Rule 4 needs it |

Discipline: anything a *second* rule needs gets promoted to `shared/`. Resist speculative helpers.

---

## Phasing

- **Phase 0** ✅ *done* — this plan, `rules/CATALOG.md`, eyecite smoke test, minimal scaffolding
- **Phase 0.5** ✅ *done* — three California superior-court demurrer fixtures under `fixtures/`: `clean.docx` (passes everything), `kitchen-sink-violations.docx` (19 violations across 16 rule_ids; sidecar `*.violations.json` is ground truth), `realistic-mixed.docx` (5 plausible-typo violations). Citations drawn exclusively from `fixtures/seed-citations.verified.md` (17 cases verified against CourtListener + 13 statutes verified against leginfo). Reusable subagent briefs (`DRAFT_BRIEF.md`, `VERIFY_BRIEF.md`, `CORRUPT_BRIEF.md`) and per-fixture audit trails are checked in for future fixture maintenance. All three fixtures are reproducible from `fixtures/scripts/build_*.py`.
- **Phase 1** *(next — separate session per rule)* — the four starter rules, each plugged into the scaffolding:
  - Rule 1 — Two spaces between sentences (Tier 1) — **also builds the minimal `shared/eyecite_wrapper.py`** in the same session, since the rule needs citation spans to suppress false positives on legal-abbreviation tokens (`Cal.App.4th`, `U.S. 662`, `F.3d 1370`, etc.); a small residual abbreviation list (honorifics, Latin, entity suffixes, code-name leaders eyecite doesn't tag) handles what the wrapper doesn't catch
  - Rule 2 — Section symbol placement: `§` inside parens, `section` outside (Tier 1 → 3) — extends the wrapper as needed
  - Rule 3 — `district` / `Board` / etc. capitalization (Tier 4, LLM)
  - Rule 4 — Citation hallucination check via eyecite + CourtListener (Tier 3 + external) — extends the wrapper as needed
  - For Rule 3: sub-split of (a) eval harness + labeled corpus + model benchmark, (b) pipeline wire-in, decided at session time
- **Phase 2** — expand rule set from the catalog; add HTML renderer; harden the engine; shape fixtures into a regression suite; build custom extractor for CA statutes / regs / PERB / EERB / OAH / LRP (see `smoke-tests/eyecite-ca-cites/FINDINGS.md`)
- **Phase 3** — graduate the engine to a new MVP repo with a front end; eventually, a Word add-in that calls a local service

---

## Key decisions

| Decision | Choice | Why |
|---|---|---|
| Language | Python | eyecite is Python; `python-docx` exists; Ollama Python client is solid |
| Rule ID format | `LS-{SECTION}-{NUM}[letter]` tied to manual section numbering (e.g., `LS-CAP-02`, `LS-CITE-06a`) | Traces cleanly back to the manual; makes revisions diffable |
| Per-rule layout | `rules/NN-slug/{rule.py, test_rule.py, fixtures/, NOTES.md}` | Each rule is a small research project; rule-specific state and notes stay with the rule |
| `Finding` schema | JSON-serializable dataclass (strawman below) | Every renderer, export, and future UI consumes the same shape |
| Output format | Plain text in Phase 0; HTML in Phase 2; tracked-changes .docx deferred | Engine correctness matters more than chrome while iterating on rules |
| Citation extraction | eyecite 2.7.6 for **case citations** (Phase 0 smoke test passed); custom regex extractor for CA statutes / regs / PERB / EERB / OAH / LRP in Phase 2 | Smoke test (see `smoke-tests/eyecite-ca-cites/FINDINGS.md`) confirmed eyecite handles CSM-style state cases, Bluebook federal cases, Westlaw-only federal cases, and LS short-cites; does not parse CA statutory cites beyond the `§` symbol and is unaware of CA admin reporters |
| LLM runtime | Ollama; model choice eval-driven (Gemma 3 family as first candidates) | Local-only; diverse model sizes already installed on dev machine |
| Privacy | All processing local; CourtListener is the only external call and only for citation strings | Preserves attorney-client privilege under CRPC 1.6 |
| Style manual version | `StyleManual.pdf` dated 2022-12-29 (per PDF metadata) | Manual is revised periodically; each rule records the version it implements |
| Court-type awareness | Rules are passed a `court_context` (state trial / state appellate / federal trial / federal appellate) | Some rules differ by court (e.g., citation signal italicization, parenthesization of citation sentences) |

### Finding schema (strawman — subject to Rule 1 pressure-testing)

```json
{
  "rule_id": "LS-CAP-02",
  "severity": "error | warning | info",
  "manual_section": "Capitalization §2 (p. 6)",
  "location": {
    "paragraph_index": 12,
    "char_start": 47,
    "char_end": 54
  },
  "snippet": "...the district has used this authority...",
  "message": "\"district\" may need capitalization — \"District\" was defined as a party substitute in paragraph 3.",
  "suggested_fix": "District",
  "confidence": 0.85,
  "evidence": { "optional rule-specific payload for debugging": null }
}
```

### Operating principles

- **Precision over recall, especially for Tier 4.** A tool that cries wolf loses the user's trust. Each rule tunes toward fewer, higher-confidence findings; add severity `info` for softer signals.
- **Graceful degradation.** If Ollama isn't running or CourtListener is unreachable, the affected rule is skipped with a note in the report — never crash the run.
- **The rule is reviewed, not the draft.** The tool flags; the attorney decides. Every finding includes a message citing the manual section so the user can verify.
- **Ambiguity in the manual is documented, not decided silently.** When the manual leaves a rule unclear, the implementation flags at `warning` and the rule's `NOTES.md` records the ambiguity.

---

## Open questions

Deliberately not resolving these yet. Each has a trigger for when to decide.

1. **Internal document representation.** Parse .docx into an intermediate model, or operate directly on `python-docx` objects? — *Trigger: first Tier 2 rule (font/spacing/indent) forces the call.*
2. **Eval harness placement.** Lives in this repo, or extracted to a separate tool once we have two LLM-based rules? — *Trigger: second Tier 4 rule.*
3. **Windows packaging strategy.** PyInstaller, Briefcase, .zip-with-venv, or local HTTP service + Word add-in? — *Trigger: Phase 3, when the MVP repo comes online.*
4. **Style manual revision tracking.** Manual diff + rule re-check, or something more automated? — *Trigger: first revision of the manual after Phase 1 ships.*
5. **Defined-term / prior-citation state data structure.** Shared by `id.`, short cites, party substitute capitalization, and others. — *Trigger: first rule that needs prior-document state (likely Rule 3).*
6. **Court-type detection vs. user declaration.** Does the user tell the tool what kind of filing it is, or does the tool infer? — *Trigger: first rule that behaves differently across courts (likely Rule 2).*

---

## Non-code conventions

- `NOTES.md` inside a rule directory captures false positives seen, prompt iterations, edge cases. It is the "so that's why we did it that way" record; not deleted when the rule ships.
- Fixture documents under `fixtures/` are checked in; never contain real client content.
- Memory lives outside the repo at `~/.claude/projects/.../memory/`; this file is for human collaborators and future-me/Claude.

---

## Dev environment vs. target

Development happens on Nick's personal Linux laptop (no A/C privilege concerns for dev). The eventual demo target — and first real user — runs Windows on a firm-issued laptop. Code stays portable (`pathlib`, no shell assumptions); packaging gets addressed in Phase 3.
