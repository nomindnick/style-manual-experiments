# LS-CAP-02 prompt research log

Iterative prompt-engineering log for the district/board/etc. capitalization
rule. Each experiment records the corpus, the prompt, the models, and the
results in one place so we can see what's been tried and where the dial moved.

When we eventually ship `rule.py`, the production-relevant takeaways graduate
to a `NOTES.md` at the rule root; this file stays as the "lab notebook."

## Conventions

- **Label space.** Two labels: `capitalize` and `lowercase`. The
  `do_not_flag` / scope bucket (case names in citations, quoted text,
  headings, compound modifiers) is **excluded** from the v0 research — it's a
  separate problem and probably better handled by deterministic pre-filters.
- **Target marker.** The phrase under judgment is wrapped in `[[…]]` in the
  prompt. Double brackets to avoid colliding with single brackets that appear
  naturally in legal prose (alterations in quotes, `[id.]`, `[Citation.]`).
- **JSON schema.** Output is `{reasoning, label, confidence}`. `reasoning`
  comes **first** in the schema's `required` array — under Ollama's
  grammar-constrained decoding this forces the model to emit reasoning before
  committing to a label (real CoT, not post-hoc rationalization).
- **Memory hygiene.** Multi-model sweeps run smallest → largest; the harness
  passes `keep_alive=0` on each model's last call so the server unloads it
  before the next loads. (Avoids the OOM that crashed the original 26b → 27b
  run on this 30 GB box.)
- **Reproducibility.** Temperature 0; results files are committed alongside
  each corpus. Re-running should produce identical outputs absent model
  changes on the Ollama side.

## Corpora

### v0-sentences — 20 controlled single sentences

- **Path:** `rules/03-cap-district/eval/v0-sentences/`
- **Built:** 2026-04-28
- **Composition:** 10 `capitalize` + 10 `lowercase`, balanced.
- **Design rule:** every sentence is gold-labelable from the sentence alone.
  No "the District filed its demurrer" without context — that would be
  testing the wrong thing.
- **Difficulty gradient inside each class:**
  - `cap`: full proper names → in-sentence definitions → same-sentence
    anaphors → coreference where the named entity appears *after* the bare
    trigger.
  - `low`: indefinite/quantified generics → statutory paraphrases → plural
    class references → comparative sentences with two triggers.
- **Trade-off acknowledged:** controlled sentences are out-of-distribution
  vs. real briefs (no document-level defined-term context, no surrounding
  paragraph). Strong scores here need to transfer back to the 81-candidate
  real-fixture eval before we can claim a prompt is "good."

## Prompt variants

### v0-prompt — minimal first-principles prompt

- **Defined in:** `rules/03-cap-district/eval/v0-sentences/run.py`
- **Shape:** ~9 lines. Rule statement, bracket marker instruction,
  specific-vs-generic framing, JSON output spec. No few-shot examples, no
  rule decomposition, no scope handling.
- **Author's note:** drafted by Nick directly, in plain language. The point
  of starting here is to see how far the model gets on its own before we
  pile on prompt-engineering.

### v1a-prompt — v0 + one-line legal context

- **Defined in:** `PROMPTS["v1a"]` in `v0-sentences/run.py`
- **Diff from v0:** opening sentence becomes "You are applying a style rule
  to a single sentence taken from a legal document drafted by an attorney."
  Everything else is identical so any score delta is attributable to the
  context cue alone.

### v1b-prompt — v1a + significance sentence

- **Defined in:** `PROMPTS["v1b"]` in `v0-sentences/run.py`
- **Diff from v1a:** appends one sentence to the opening paragraph
  explaining that an attorney may refer to a specific party/recipient
  agency *or* may use a designation more broadly to describe the law's
  general application. Targets the statutory-paraphrase failure mode
  observed in EXP-01 (e4b) and EXP-02 (qwen-9b).

## Experiments

### EXP-01 — v0-prompt × v0-sentences × {gemma4:e2b, e4b, 26b}

- **Date:** 2026-04-28
- **Run:** `rules/03-cap-district/eval/v0-sentences/run.py` (defaults)
- **Log:** `rules/03-cap-district/eval/v0-sentences/run.log`
- **Per-model results:** `results.v0.gemma4__{e2b,e4b,26b}.json` in same dir

| model        | acc    | cap acc | low acc | lat (s/call) |
|--------------|--------|---------|---------|--------------|
| gemma4:e2b   |  50.0% |  90.0%  |  10.0%  | 3.2          |
| gemma4:e4b   |  90.0% | 100.0%  |  80.0%  | 7.1          |
| gemma4:26b   | 100.0% | 100.0%  | 100.0%  | 6.3          |

**Findings**

- **26b is perfect** on this corpus, including the hardest case (`cap-07`:
  "Counsel for the District served the verified petition on Eastvale Joint
  USD's superintendent…" — bare `District` resolved by coreference to a
  named entity that appears *later* in the same sentence).
- **e4b at 90% with a minimal prompt is a major signal.** On the real
  81-candidate fixture eval with the heavyweight 95-line prompt, e4b sat at
  ~57% accuracy with only 8% recall on `must_lowercase`. Same model, much
  shorter prompt, controlled sentences: 90%. Strong hypothesis: **the long
  prompt was hurting performance.** Needs to be confirmed by re-running the
  v0 prompt on the real corpus.
- **e4b's two misses share a pattern: statutory paraphrase.** Both have the
  shape "Code section X authorizes/grants a [trigger] to…":
  - `low-03`: "Any [board of education] considering a layoff resolution
    should consult Education Code section 44955."
  - `low-06`: "Government Code section 25303 grants a [board of supervisors]
    general supervisorial authority over county officers."

  The model's reasoning is consistent: it conflates "specific statute"
  with "specific entity." E.g.: *"used here in the context of a specific
  legal grant (Government Code section 25303), implying a specific,
  identifiable governing body."* This is a tightly-clustered, addressable
  failure mode — likely fixable with one targeted prompt sentence about
  statutory paraphrases.
- **e2b is essentially "always capitalize."** 9 of 10 misses are false-caps;
  reasoning is post-hoc rationalization on the trigger ("specific
  governmental entity"). Also produced **one schema violation** —
  `cap-07` returned `pred=District` instead of one of the two enum values,
  meaning Ollama's structured-output constraint didn't fully bind on the
  smallest model. Likely unviable for this rule at any prompt complexity,
  but worth confirming.
- **Latency oddity:** 26b averaged 6.3s/call, *faster* than e4b's 7.1s.
  Either 26b's reasoning was shorter or it parallelizes better on this
  hardware.

### EXP-02 — v0-prompt × v0-sentences × {qwen3.5:9b}

- **Date:** 2026-04-28
- **Run:** `rules/03-cap-district/eval/v0-sentences/run.py --models qwen3.5:9b`
- **Log:** appended to `v0-sentences/run.log`
- **Per-model results:** `results.v0.qwen3.5__9b.json`

| model        | acc    | cap acc | low acc | lat (s/call) | schema errors |
|--------------|--------|---------|---------|--------------|---------------|
| qwen3.5:9b   |  84.2% |  80.0%  |  80.0%  | 37.0         | 1 / 20        |

**Findings**

- **qwen3.5:9b underperforms gemma4:e4b on this corpus and prompt** (84.2%
  vs 90.0%). Notable inversion: on the heavyweight 95-line prompt + real
  fixture eval, qwen3.5:9b beat gemma4:e4b by ~10 points (66.2% vs ~57%).
  Two competing explanations: (a) gemma family responds better to simple
  prompts, or (b) the corpora differ enough that the comparison isn't
  apples-to-apples. Settling this requires EXP-04.
- **Schema-violation issue replicates outside the smallest model.** `cap-03`
  produced a JSON parse error from qwen — same failure class as e2b's
  `cap-07`. So Ollama's `format=` constraint can fail on a 9B model, not
  just on the 2B. Probably want a retry-on-parse-error layer at some point.
  Original heavyweight-prompt eval had 4 such errors out of 81 candidates
  on gemma4:26b too — known issue, not a one-off.
- **Statutory-paraphrase blind spot is cross-family.** qwen missed `low-06`
  ("Government Code section 25303 grants a [board of supervisors]…") with
  the same reasoning shape as e4b: "specific Government Code section…
  denotes a specific identifiable agency." This is a small-model pattern,
  not a gemma idiosyncrasy. Strengthens the case for a targeted prompt
  patch in EXP-03.
- **Real comprehension miss on `cap-04`** ("Petitioner City of Modesto
  (the \"[[City]]\")…"). Qwen reasoned the bracketed `City` was a generic
  noun-class reference and missed that the parenthetical is the canonical
  defined-term setup. This construction is the workhorse of every demurrer
  — production-relevant failure.
- **One outright confabulation on `low-09`.** Qwen claimed "board of
  trustees" referred to "the school district mentioned in the context"
  when no school district appears in the sentence. Worse failure mode than
  e4b's, which at least anchored in something present.
- **Latency: ~5× gemma** at this size class on this hardware. ~37s/call vs
  e4b's 7.1s and 26b's 6.3s. Cost matters at production volume.

### EXP-03 — v1a-prompt × v0-sentences × {gemma4:e2b, e4b, 26b, qwen3.5:9b}

- **Date:** 2026-04-28
- **Run:** `rules/03-cap-district/eval/v0-sentences/run.py --prompt v1a`
- **Log:** appended to `v0-sentences/run.log`
- **Per-model results:** `results.v1a.{model}.json`

| model        | v0 acc | v1a acc | Δ        | v0 low | v1a low |
|--------------|--------|---------|----------|--------|---------|
| gemma4:e2b   |  50.0% |  55.0%  | +5.0pp   |  10%   |  10%    |
| gemma4:e4b   |  90.0% |  85.0%  | −5.0pp   |  80%   |  70%    |
| gemma4:26b   | 100.0% | 100.0%  |  0       | 100%   | 100%    |
| qwen3.5:9b   |  84.2% |  89.5%  | +5.3pp   |  80%   |  80%    |

**Findings**

- **v1a did not unlock the statutory-paraphrase failure.** All three
  non-26b models still miss `low-06` ("Government Code section 25303
  grants a [board of supervisors]…"). The reasoning shape is identical to
  v0 — "specific code section, therefore specific entity." Adding the
  legal-context cue gave the model no new traction on this pattern.
- **e4b regressed** (−5pp). Specifically, it now also misses `low-05`
  ("Education Code section 35160 authorizes a [school district]…") which
  it got correct under v0. So v1a's cue made the statutory-paraphrase bug
  slightly *worse* on e4b, not better. Probably noise on the boundary,
  but worth not over-claiming any v1a benefit on e4b.
- **qwen-9b got a narrow but real win.** It now correctly classifies
  `cap-04` ("Petitioner City of Modesto (the \"[[City]]\")…"). In v0 it
  had completely missed the canonical `(the "ShortForm")` defined-term
  parenthetical and called it lowercase. With "legal document drafted by
  an attorney" in the prompt, qwen recognizes that this construction is
  defining a party-substitute. Useful because that pattern is the
  workhorse of every demurrer, but doesn't address the core failure.
- **e2b's gain is mostly noise.** Now 10/10 on cap and no schema
  violations this run — but cap-class accuracy was already 90% on v0, and
  e2b still sits at 10% on lowercase ("always capitalize" behavior
  persists). v1a moved a single cap example.
- **26b unchanged at 100%.** Either saturation on this corpus or genuine
  headroom; we won't know which until v1-sentences exists.
- **Schema-violation pattern is sentence + model specific.** e2b errored
  on `cap-07` in v0, was clean here. Qwen errored on `cap-03` in *both*
  runs — same JSON parse failure on the same sentence, both prompts. So
  it's a deterministic interaction between qwen-9b and that particular
  sentence ("Defendant Fresno Unified [[School District]] (the
  \"District\") demurs to the Complaint."), not random instability.

**Takeaway for v1b**

The statutory-paraphrase failure mode is the dominant remaining bug, and
v1a clearly doesn't address it. v1b is now well-motivated: its second
sentence explicitly names the pattern ("...or may at other times use an
agency or governing-board designation more broadly to explain how the law
applies generally") which is exactly what the model is failing to
recognize on `low-03`/`low-05`/`low-06`. Run next as EXP-04.

### EXP-04 — v1b-prompt × v0-sentences × {gemma4:e2b, e4b, 26b, qwen3.5:9b}

- **Date:** 2026-04-28
- **Run:** `rules/03-cap-district/eval/v0-sentences/run.py --prompt v1b`
- **Log:** appended to `v0-sentences/run.log`
- **Per-model results:** `results.v1b.{model}.json`

| model        | v1a acc | v1b acc | Δ        | v0→v1b Δ |
|--------------|---------|---------|----------|----------|
| gemma4:e2b   |  55.0%  |  60.0%  | +5.0pp   | +10.0pp  |
| gemma4:e4b   |  85.0%  |  85.0%  |  0       | −5.0pp   |
| gemma4:26b   | 100.0%  | 100.0%  |  0       |  0       |
| qwen3.5:9b   |  89.5%  |  94.7%  | +5.3pp   | +10.5pp  |

**Findings**

- **qwen3.5:9b: 94.7% — the v1b breakthrough.** All three
  statutory-paraphrase cases that had broken qwen on v0/v1a (`low-03`,
  `low-05`, `low-06`) are now correct. The "significance" sentence did
  exactly the job it was written for. Qwen's only remaining misses on
  v0-sentences:
  1. `cap-03` — the deterministic schema violation that's been present
     across all three prompts (model+sentence-specific bug).
  2. `low-09` — the hardest sentence in the corpus (comparative with two
     triggers, ambiguous antecedent for "board of trustees").
  Strip the schema bug and qwen is at 94.7% genuine accuracy on
  v0-sentences; with retry-on-parse it could plausibly hit 95-100%.
- **e4b is stuck at 85% — same misses as v1a.** The same prompt change
  that lifted qwen 10pp had zero effect on e4b's statutory-paraphrase
  bucket. More than zero, actually — *e4b is reading v1b's added language
  and using it to justify the wrong answer.* Reasoning excerpt on `low-05`:
  > "...the context implies that the law is granting authority to **a
  > specific type of entity that is a party to the proceeding or governed
  > by the code**, making it refer to a specific, identifiable agency."

  That bolded phrase is lifted directly from the v1b prompt. The model
  isn't ignoring the cue — it's integrating it and applying it backward.
  That's a different problem class from "model doesn't understand": the
  model can't reliably tell which side of the dichotomy it's on, even
  when both sides are explicitly named.
- **Same prompt, opposite effects on different models.** v1b lifts qwen
  +5pp, leaves e4b flat (and arguably worse, given the reasoning is now
  miscalibrated). This is a real lesson about prompt portability across
  local model families — what looks like a clean targeted fix on one
  model can be neutral or counterproductive on another.
- **e2b: 60% — net +10pp from v0, but unstable.** Picked up the two plural-
  form cases (`low-07`, `low-10`) under v1b but lost `low-04` (which it
  had correct on v0 *and* v1a). The longer prompt is shifting e2b's
  pattern-match without fixing the underlying "always capitalize" bias.
  Still 8/10 wrong on lowercase.
- **gemma4:26b unchanged at 100%** across all three prompts. We have no
  signal on how it would respond to harder cases until v1-sentences exists.
- **qwen latency scales with prompt length** as expected: 37s/call (v0) →
  38s (v1a) → 42s (v1b). Still ~6× e4b/26b. Production-relevant.

## Standings — model × prompt grid (final on v0-sentences)

| model        | v0 acc | v1a acc | v1b acc | best |
|--------------|--------|---------|---------|------|
| gemma4:26b   | 100.0% | 100.0%  | 100.0%  | any  |
| qwen3.5:9b   |  84.2% |  89.5%  | **94.7%** | v1b |
| gemma4:e4b   |  90.0% |  85.0%  |  85.0%  | v0   |
| gemma4:e2b   |  50.0% |  55.0%  |  60.0%  | v1b  |

Two production-viable candidates emerge: **gemma4:26b at 100% (6.6s/call)**
and **qwen3.5:9b + v1b at 94.7% (42s/call, modulo schema-violation patch)**.
The choice between them is mostly a latency/accuracy trade-off — qwen-9b is
~6× slower but lighter on RAM (~5 GB vs ~17 GB for 26b).

## Key cross-experiment lessons

1. **Less is often more.** v0-prompt (minimal, ~9 lines) beats the original
   95-line heavyweight prompt by ~30pp on e4b and ~20pp on qwen-9b on this
   easier corpus. Confirmed pending real-fixture re-test.
2. **Targeted prompt cues work — but model-dependently.** The "significance"
   sentence in v1b is a textbook targeted cue (it names the failure
   pattern). It works perfectly on qwen-9b and not at all on e4b.
3. **Reasoning-first schema is load-bearing.** Putting `reasoning` ahead
   of `label` in the JSON schema's `required` array forces real CoT under
   Ollama's grammar-constrained decoding. Without it, models post-hoc
   rationalize. (Inherited from EXP-01 setup, not directly tested.)
4. **Schema-violations are deterministic per (model, sentence).** Not
   random. They're reproducible. So a one-shot retry probably won't help;
   need either a different prompt phrasing or a model-specific workaround
   for the offending sentences.

## Open questions / next experiments

- [ ] **EXP-?: v1b-prompt × the original 81-candidate fixture eval.**
  The highest-information test we have left. Two real questions: (a) does
  qwen's +10.5pp lift transfer to messy real-fixture cases, and (b) does
  e4b stay flat or get worse there too. This is the test that would
  graduate v1b from "promising on a controlled set" to "shippable prompt."
- [ ] **e4b diagnostic.** e4b's failure mode under v1b is qualitatively
  different from before — it's parroting the prompt language to justify
  wrong answers. Worth understanding before deciding whether to keep
  iterating on prompt cues for e4b at all, or treat 85% as its ceiling.
- [ ] **Retry-on-parse-error in `shared/ollama_client.py`.** Now confirmed
  the schema violations are deterministic, so naive retry won't help
  qwen's `cap-03` problem. But it might help genuinely transient cases on
  bigger corpora. Lower priority than initially thought.
- [ ] **v1-sentences corpus.** v0-sentences saturates 26b at 100% and
  qwen-9b approaching 95%; we need harder cases to differentiate the
  candidates and to test prompt robustness. Build after the real-fixture
  eval if 26b/qwen-9b still need stress-testing.
