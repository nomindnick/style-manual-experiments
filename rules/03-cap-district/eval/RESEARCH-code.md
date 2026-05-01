# LS-CAP-02 — code-prompts arm research log

Lab notebook for the code-prompts arm of the district/board/etc.
capitalization rule research.

Hypothesis: small recent open models (gemma4, qwen3.5) treat
code-shaped prompts as a familiar register and may judge more
consistently from compact code-style templates than from prose rule
statements. Several template shapes are on the table — see Open
questions below.

This is one of two parallel research arms; the cross-arm index, the
shared-corpus description, and the final head-to-head comparison live
in the slim `RESEARCH.md`. The other arm's lab notebook is
`RESEARCH-prose.md`.

When we eventually ship `rule.py`, the production-relevant takeaways
graduate to a `NOTES.md` at the rule root; this file stays as the lab
notebook.

## Conventions

- **Shared controlled corpus:** `v0-sentences/sentences.json` (10 cap +
  10 low). Same gold labels as the prose arm — per-sentence behavior
  is directly comparable.
- **Shared fixture corpus:** `candidates.{fixture}.json` filtered to
  the binary subset (145 of 247 candidates). Same as the prose arm's
  fixture eval.
- **Label space.** Two labels: `capitalize` and `lowercase`. The
  `do_not_flag` / out-of-scope bucket is excluded by design (same as
  the prose arm — deterministic prefilter territory).
- **Reproducibility.** Default temperature 0; results files committed
  alongside each corpus. Re-running should produce identical outputs
  absent model changes on the Ollama side.
- **Memory hygiene.** Multi-model sweeps run smallest → largest with
  `keep_alive=0` on each model's last call. (Same memory-hygiene
  pattern as the prose arm — see `RESEARCH-prose.md` for the OOM
  history that motivated it.)
- **Harness location:** `eval/code-prompts/`. Each prompt template
  variant gets a key in the harness's `PROMPTS` dict; result files
  are namespaced by variant key so different code-prompt shapes
  don't clobber each other.

## Prompt variants

(none yet — fill in as templates are tried)

## Experiments

(none yet — fill in as runs complete)

## Key cross-experiment lessons

(none yet)

## Open questions / next experiments

- [ ] **Pick the first code-prompt template to try.** Candidates on the
  table:
  - **Rule statement + JSON few-shot examples.** Closest to the prose
    arm's v0-prompt but with the rule's positive/negative examples
    rendered as JSON inputs/outputs (rather than narrative).
  - **JSON few-shot examples only (no rule statement).** Force the
    model to infer the rule from input/output pairs. Tests whether
    the rule prose itself was load-bearing or whether examples are
    enough.
  - **Partial JSON schema for completion.** Give the model a partially
    filled JSON object and have it fill in the `label` and
    `reasoning` fields. Hypothesis: structurally constrains the
    model's "thinking" path more than free-form prompting.
  - **Pseudo-Python rule function.** Render the rule as a function
    signature with examples in the docstring; ask the model to "call"
    it on the candidate. Highest-novelty / highest-risk shape.
- [ ] **Marker convention.** The prose arm found that target marker
  format materially shifts attention (`[[…]]` → `<target>…</target>`
  was a 5pp lift on qwen). Worth deciding early what marker the code
  arm uses — and whether code-shaped prompts call for a different
  marker (e.g., `# target: …` comments, or a dedicated JSON field).
- [ ] **Same set of models?** Default to the prose arm's quartet
  (gemma4:e2b, e4b, 26b, qwen3.5:9b) for direct comparability, unless
  there's a code-specific reason to add or drop one.
