# Claude Code notes

Experiment repo for a local, privilege-safe reviewer that checks Lozano Smith litigation drafts against the LS Style Manual and flags potentially hallucinated citations. See [`PLAN.md`](PLAN.md) for the full plan; this file is the short orientation for Claude sessions.

## Start-of-session context to load

- **[`PLAN.md`](PLAN.md)** — goals, scope, architecture, phasing, decisions, open questions. Read first.
- **[`rules/CATALOG.md`](rules/CATALOG.md)** — every rule from the manual with `LS-{SECTION}-{NUM}` ID, tier, source, and status. Source of truth for what's planned / queued / deferred / descoped.
- **[`smoke-tests/eyecite-ca-cites/FINDINGS.md`](smoke-tests/eyecite-ca-cites/FINDINGS.md)** — what eyecite parses well and what it doesn't; relevant to Rule 4 scope.
- **Memory index** at `~/.claude/projects/-home-nick-Projects-style-manual-experiments/memory/MEMORY.md` — user context and feedback rules.

## Hard constraints

- **No firm or client content leaves the machine.** Local Ollama is the approved LLM runtime. CourtListener is the *only* sanctioned external call, and only for citation strings. See the privilege memory.
- **`/source-docs/` is gitignored and stays that way.** Firm-authored materials (the Style Manual, any templates Nick may add later) are firm IP; never committed, never uploaded to third-party services, never quoted at length. See the firm-IP memory.
- **Repo is public on GitHub** (`nomindnick/style-manual-experiments`). Assume every commit is world-readable.

## Working conventions

- **Use the venv for Python:** `.venv/bin/python` — never the system `python3`. `requirements.txt` is pinned; bump deliberately. Built and tested against Python 3.12.
- **Per-rule layout:** `rules/NN-slug/{rule.py, test_rule.py, fixtures/, NOTES.md}`. Each rule is a small research project; `NOTES.md` captures false positives, prompt iterations, and edge cases as they're found.
- **Rule interface:** subclass `shared.rule_base.Rule`, implement `check(Document) -> list[Finding]`. Declare `rule_id` / `name` / `manual_section` / `tier` as class attributes.
- **Common contract:** `shared.finding.Finding` is what every rule emits and every renderer consumes. Don't invent bespoke output shapes.
- **Shared helpers graduate lazily.** If a *second* rule needs something, promote to `shared/`. Resist speculative abstractions built ahead of a real caller.
- **Smoke tests under `smoke-tests/`** — not a full pytest suite yet. Each rule ships its own `rules/NN-slug/test_rule.py` (synthetic + integration against the real `.docx` fixtures); run from the repo root.

## Running things

```bash
# Per-rule tests
.venv/bin/python rules/01-two-spaces/test_rule.py
.venv/bin/python rules/02-section-symbol/test_rule.py

# eyecite exploration
.venv/bin/python smoke-tests/eyecite-ca-cites/run.py
```

## Current phase

- **Phase 0** — done (this file, `PLAN.md`, `rules/CATALOG.md`, smoke test, `shared/`).
- **Phase 0.5** — done. Three fixtures live under `fixtures/`: `clean.docx`, `kitchen-sink-violations.docx` (+ `*.violations.json` ground truth, 19 violations / 16 rule_ids), `realistic-mixed.docx` (+ `*.violations.json`, 5 violations). Reproducible from `fixtures/scripts/build_*.py`. Citations vetted in `fixtures/seed-citations.verified.md`. Reusable subagent briefs (`DRAFT_BRIEF.md`, `VERIFY_BRIEF.md`, `CORRUPT_BRIEF.md`) document the construction pipeline.
- **Phase 1 — in progress** — one focused session per rule:
  1. ✅ `LS-SP-02` — two spaces between sentences (Tier 1) — shipped. Built `shared/eyecite_wrapper.py` (CitationSpan + per-paragraph spans, lru-cached) alongside; suppression layers and false-positive surface documented in `rules/01-two-spaces/NOTES.md`.
  2. ✅ `LS-CITE-02` — section symbol placement (Tier 3) — shipped. Bidirectional check with paragraph-local paren-depth scanner (brackets count too); CA state-court only, federal deviation documented. Scanner stays in-rule until LS-CITE-03 needs it. See `rules/02-section-symbol/NOTES.md`.
  3. **next** — `LS-CAP-02` — district / board / etc. capitalization (Tier 4, LLM; may split into eval + integration sub-sessions)
  4. `LS-CITE-HAL` — citation hallucination check (Tier 3 + CourtListener)

## Things to avoid

- Implementing features ahead of the current phase.
- Tracked-changes `.docx` output — deferred; `python-docx` doesn't natively support it and the yak-shave isn't justified in the experiment repo.
- Adding rules beyond the starter four before Phase 1 ships.
- Cloud LLM SDKs (OpenAI, Anthropic cloud, Google, etc.). Ollama only.
- Large speculative abstractions in `shared/` before a second caller exists.
