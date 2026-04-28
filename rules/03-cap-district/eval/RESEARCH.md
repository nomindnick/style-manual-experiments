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
  EXP-05 introduces a parallel `v1b-xml` variant that swaps `[[…]]` for
  `<target>…</target>`; the marker in use is keyed by prompt name in
  `MARKERS` in `run.py` so the rest of the harness stays neutral.
- **JSON schema.** Output is `{reasoning, label, confidence}`. `reasoning`
  comes **first** in the schema's `required` array — under Ollama's
  grammar-constrained decoding this forces the model to emit reasoning before
  committing to a label (real CoT, not post-hoc rationalization).
- **Memory hygiene.** Multi-model sweeps run smallest → largest; the harness
  passes `keep_alive=0` on each model's last call so the server unloads it
  before the next loads. (Avoids the OOM that crashed the original 26b → 27b
  run on this 30 GB box.)
- **Reproducibility.** Default temperature is 0; results files are
  committed alongside each corpus. Re-running should produce identical
  outputs absent model changes on the Ollama side. The harness now
  exposes `--temperature` (EXP-06); non-zero values get a `.t{NN}`
  infix in the result filename (e.g. `results.v1b-xml.t07.qwen3.5__9b.json`)
  so they don't clobber the deterministic baselines.

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

### v1b-xml-prompt — v1b with XML target markers

- **Defined in:** `PROMPTS["v1b-xml"]` in `v0-sentences/run.py`
- **Diff from v1b:** identical content; only the target marker changes
  from `[[…]]` to `<target>…</target>` (and the corresponding marker
  references in the prompt body are reworded to "tagged" / "between the
  tags"). External hypothesis we were testing: that bracket tokens may be
  destabilizing Ollama's grammar-constrained JSON decoding on qwen-9b's
  deterministic `cap-03` failure. Schema-violation hypothesis was
  falsified by EXP-05, but the marker swap moved the dial elsewhere — see
  that experiment for details.

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

### EXP-05 — v1b-xml-prompt × v0-sentences × {gemma4:e2b, e4b, 26b, qwen3.5:9b}

- **Date:** 2026-04-28
- **Run:** `rules/03-cap-district/eval/v0-sentences/run.py --prompt v1b-xml`
- **Log:** appended to `v0-sentences/run.log`
- **Per-model results:** `results.v1b-xml.{model}.json`

**Setup.** An external review of EXP-04 suggested two hypotheses about
qwen3.5:9b's deterministic `cap-03` schema violation: (a) the `[[…]]`
markers themselves were destabilizing Ollama's grammar-constrained JSON
decoder, or (b) the embedded `(the "District")` was inducing unescaped
double-quotes inside the model's `reasoning` string. EXP-05 isolates
hypothesis (a) by changing only the marker — `[[…]]` → `<target>…</target>` —
while keeping the v1b prompt content character-identical otherwise.

| model        | v1b acc | v1b-xml acc | Δ        | v1b-xml low | v1b-xml cap |
|--------------|---------|-------------|----------|-------------|-------------|
| gemma4:e2b   |  60.0%  |  60.0%      |  0       |  30%        |  90%        |
| gemma4:e4b   |  85.0%  |  80.0%      | −5.0pp   |  60%        | 100%        |
| gemma4:26b   | 100.0%  | 100.0%      |  0       | 100%        | 100%        |
| qwen3.5:9b   |  94.7%  | **100.0%**  | +5.3pp   | 100%        |  90%*       |

*qwen `cap-03` still errors out with the same `JSONDecodeError: Expecting ',' delimiter: line 2 column 80` and is excluded from the per-class accuracy denominator (19 ok / 1 err). 19/19 of the responses qwen actually returned were correct.

**Findings**

- **Schema-violation hypothesis (a) is falsified.** qwen3.5:9b's `cap-03`
  produced byte-identical error output under v1b-xml: same exception
  type, same character offset (line 2 col 80). Bracket tokens in the
  user message are not what's destabilizing the JSON. The remaining
  hypothesis on the table is the embedded `(the "District")`
  parenthetical inducing unescaped quotes in `reasoning`. Tracking that
  as the live hypothesis going forward.
- **qwen3.5:9b cleared all four lowercase-class blind spots.** With
  v1b's content held constant and only the marker changed, qwen got
  every lowercase sentence right — including `low-09`, the
  comparative-with-two-triggers sentence that had broken qwen on every
  prior prompt. This was unexpected. The marker change was supposed to
  test a tokenization theory; instead it changed how the model attends
  to the target.
- **The reasoning shift on `low-09` is striking.** Verbatim:
  - **Under `[[…]]`:** "The phrase 'board of trustees' refers to a
    specific governing body distinct from the 'county board of
    supervisors' mentioned in the same sentence, indicating it is a
    specific entity rather than a generic class." → `capitalize` (wrong)
  - **Under `<target>…</target>`:** "The phrase 'board of trustees' is
    used generically to describe a class of governing bodies
    (specifically contrasting them with 'county board of supervisors' as
    a category) rather than referring to a specific, named entity like
    'The Springfield Board of Trustees'. Therefore, it should be
    lowercase." → `lowercase` (right, with correctly hypothesized
    counterexample)

  Same model, same temperature, same content, same sentence — only the
  marker around the target changed. The XML form appears to read to qwen
  as "this string has been tagged for analysis" while the bracket form
  reads as "this string has been emphasized/named." Speculative
  mechanism; what's empirical is that the effect is large on a hard
  case.
- **gemma4:e4b regressed slightly (85% → 80%).** Lost `low-09` (which
  it had under v1b) and kept the same three statutory-paraphrase misses
  (`low-03`, `low-05`, `low-06`). e4b's reasoning on `low-09` under
  v1b-xml: "Since 'county board of supervisors' is capitalized and
  refers to a specific type of governing body, 'board of trustees' is
  likely being used to refer to a specific, identifiable body in this
  context, making capitalization appropriate." That's the same
  prompt-parroting failure mode noted in EXP-04 — model integrating cues
  and applying them backward. e4b at this size class looks ceiling'd at
  80–85% on this corpus, prompt-format-independent.
- **gemma4:e2b: 60.0%, unchanged net.** Same "always capitalize" bias
  on lowercase. Different sentence-level shuffling vs v1b but identical
  totals. Not viable for this rule at any prompt complexity tested.
- **gemma4:26b: 100.0%, unchanged.** Saturated on this corpus
  regardless of marker format.
- **No latency change of note.** qwen 42.4s/call (v1b: 42s). Gemmas
  similar to prior runs.

**Implication for production candidates.** qwen3.5:9b + v1b-xml is now
co-leader on accuracy with gemma4:26b on this corpus, modulo the
sentence-specific schema violation. The marker format is a free lever —
no content cost, no latency cost — so v1b-xml is now the qwen baseline
moving forward.

### EXP-06 — v1b-xml-prompt × T=0.7 × v0-sentences × {gemma4:e2b, e4b, 26b, qwen3.5:9b}

- **Date:** 2026-04-28
- **Run:** `rules/03-cap-district/eval/v0-sentences/run.py --prompt v1b-xml --temperature 0.7`
- **Log:** appended to `v0-sentences/run.log`
- **Per-model results:** `results.v1b-xml.t07.{model}.json`

**Setup.** Mostly-curiosity test: v1b-xml at sampling temperature 0.7
instead of 0.0, single pass. Three open questions: (a) does qwen's
deterministic `cap-03` schema violation clear when sampling has
randomness, (b) is v1b-xml's marker-attention win on `low-09` robust to
temperature, and (c) does e2b's "always capitalize" bias break with
randomness.

| model        | T=0 acc    | T=0.7 acc | Δ        | notes                                     |
|--------------|------------|-----------|----------|-------------------------------------------|
| gemma4:e2b   |  60.0%     |  60.0%    |  0       | same totals, different sentences right    |
| gemma4:e4b   |  80.0%     |  85.0%    | +5.0pp   | unlocked `low-03` (statutory paraphrase)  |
| gemma4:26b   | 100.0%     | 100.0%    |  0       | saturated                                 |
| qwen3.5:9b   | 100.0%     | 100.0%    |  0       | `cap-03` still errors (see below)         |

**Findings**

- **`cap-03` schema violation is fully temperature-independent.** Same
  exception type, same byte offset (line 2 col 80, char 81) at T=0.7 as
  at T=0. Cross-checked across all five qwen runs to date:

  | run                   | error offset (line:col / char) |
  |-----------------------|--------------------------------|
  | v0 + T=0              | 2:80 / 81                      |
  | v1a + T=0             | 2:98 / 99                      |
  | v1b + T=0             | 2:98 / 99                      |
  | v1b-xml + T=0         | 2:80 / 81                      |
  | v1b-xml + T=0.7       | 2:80 / 81                      |

  Pattern: error offset depends on *prompt content* (v0 and v1b-xml
  share an offset because both have a shorter system prompt influencing
  the response start; v1a/v1b share the longer offset). It does **not**
  depend on temperature. Even at T=0.7, the model is reproducing
  byte-identical breakage on a single specific input.

  This is the cleanest evidence yet that the bug is a structural
  artifact of grammar-constrained JSON decoding interacting with the
  embedded `(the "District")` parenthetical — not a sampling-noise
  fragility. Under `format=` constraint, temperature only chooses among
  tokens *valid in the grammar*; if the model's logit for unescaped `"`
  dominates at the relevant decision point, T=0.7 won't escape it
  because both `\"` and `"` are mass-1 next-token candidates given the
  preceding text. Most likely fix is at the input layer: either escape
  the embedded quotes before sending, or run a separate pre-rule that
  short-circuits `(the "Foo")` defined-term constructions to
  `capitalize` without an LLM call.
- **qwen's v1b-xml accuracy is robust to temperature.** All 19/19
  ok responses are still correct at T=0.7, including `low-09`. So the
  marker-attention effect from EXP-05 isn't a T=0 artifact — qwen really
  is reading `<target>…</target>` as "tagged for analysis" in a way that
  generalizes. This matters for production: the win isn't a brittle
  pinpoint of the decoding distribution.
- **e4b: 80% → 85% at T=0.7.** Unlocked `low-03` ("Any board of
  education considering a layoff resolution should consult Education
  Code section 44955."). The reasoning is qualitatively better at T=0.7
  too, not just luckier:
  - **T=0:** "...implying a class of specific, identifiable agencies
    that are subject to this rule, thus requiring capitalization." →
    `capitalize` (wrong, with the prompt-parroting failure mode noted in
    EXP-04).
  - **T=0.7:** "The sentence implies a general requirement for any
    board of education that might consider a layoff resolution,
    suggesting it is referring to the class of governing body rather
    than a specific, named one." → `lowercase` (correct, with cleanly
    framed generic-class reasoning).

  Modest signal but real — temperature lets e4b sometimes step out of
  the prompt-parroting attractor. The other two statutory-paraphrase
  cases (`low-05`, `low-06`) and the comparative (`low-09`) still
  failed, so the ceiling effect isn't *entirely* gone. Worth a multi-seed
  follow-up before claiming e4b can hit 85% reliably at T>0 — single-pass
  +5pp could still be a coin-flip on a 20-sentence corpus.
- **e2b: 60.0% net, but a different 60%.** Lost `cap-05` (had it under
  v1b-xml T=0); gained nothing on the lowercase side. Same "always
  capitalize" bias. Randomness shuffled which sentence it got wrong but
  didn't move the underlying boundary.
- **gemma4:26b: 100% unchanged.** Saturated regardless of temperature.
- **Latency unchanged.** ~3.3s e2b / 10.4s e4b / 7.1s 26b / 42s qwen.
  Sampling temperature affects which token is picked, not how long
  picking takes.

### EXP-07a — `cap-03` unescaped-quote hypothesis probe

- **Date:** 2026-04-28
- **Run:** `rules/03-cap-district/eval/v0-sentences/cap03_quote_probe.py`
- **Setup:** Two qwen3.5:9b calls on the v1b-xml prompt at T=0. Call 1
  is the original cap-03 sentence (`(the "District")`); call 2 swaps
  the embedded `"District"` for `'District'`. Everything else identical.
  `raw_content` from `ClassifyResult` captured on both so we can read
  what the decoder actually emitted.

**Hypothesis confirmed.** The doctored sentence parses cleanly with the
correct label; the original errors at the same byte offset as in every
prior run. The captured raw output makes the failure mode unambiguous.

| sentence | ok | label | latency | notes |
|---|---|---|---|---|
| original (`(the "District")`) | ✗ | — | 49.4s | `JSONDecodeError: Expecting ',' delimiter: line 2 column 80 (char 81)` |
| doctored (`(the 'District')`) | ✓ | capitalize | 47.0s | clean parse, sensible reasoning |

**The smoking gun.** Raw decoder output around char 81 (the failure
point) on the original sentence:

> `...rict' is immediately followed by '(the "<<<HERE>>>District")', which indicates it is a spe...`

qwen wrote a literal `(the "District")` inside its `reasoning` string
with the inner `"` characters unescaped. JSON parser hit the first
unescaped `"`, thought the string had closed early, then choked on the
following `District` tokens. Doctored version uses `'District'` and the
model just mirrors that quoting style — no unescaped doubles in the
reasoning string, no parse error.

**Production fix.** Pre-process inputs by replacing embedded
`"…"` quoted-substring constructions with `'…'` before sending to the
LLM. This is a one-line text substitution in the rule's
sentence-extraction path, not a prompt change. The model's *reasoning*
stays valid (it just adopts the quoting style of the input it's given);
the JSON encoding stays valid too.

**Lessons compounding.** Combined with EXP-05 (marker swap) and EXP-06
(temperature), all three deterministic-failure hypotheses for `cap-03`
are now tested and only this one survives:

| hypothesis | tested in | verdict |
|---|---|---|
| bracket tokens destabilize JSON grammar | EXP-05 | falsified |
| T=0 brittleness; randomness would clear it | EXP-06 | falsified |
| embedded `"…"` induces unescaped quotes in `reasoning` | EXP-07a | confirmed |

### EXP-07b — gemma4:e4b × v1b-xml × T=0.7 × 5 seeds

- **Date:** 2026-04-28
- **Run:** `rules/03-cap-district/eval/v0-sentences/e4b_t07_multiseed.py`
- **Result file:** `results.v1b-xml.t07.multiseed5.gemma4__e4b.json`
- **Setup:** 5 independent passes (no explicit seed control; T=0.7
  sampling) of e4b on the full 20-sentence corpus. 100 calls total.
  Goal: tell whether EXP-06's single-pass +5pp lift is consistent or
  coin-flip.

**Aggregate: 84.0% (84/100).** Sits between T=0 (80.0%) and the
single-pass T=0.7 number (85.0%). EXP-06's +5pp was a lucky pass; the
actual expected lift from temperature is closer to +4pp.

**The interesting result is per-sentence stability**, not the
aggregate:

| bucket | sentences | what it means |
|---|---|---|
| **stable correct** (5/5) | all 10 cap + low-01, -02, -04, -07, -08, -10 | e4b is rock-solid here even at T=0.7 |
| **stable wrong** (0/5) | low-06, low-09 | high-confidence wrong logits — temperature can't escape |
| **unstable** (1/5–3/5) | low-03 (3/5), low-05 (1/5) | "boundary" cases where the model has real uncertainty and temperature sometimes lands on the right side |

low-03 and low-05 are both statutory paraphrases ("Education Code
section X authorizes a school district to…"). low-06 is also a
statutory paraphrase but e4b is *deterministically* wrong on it. low-09
is the comparative-with-two-triggers case. So e4b's failure modes split
into two qualitatively different classes:

1. **High-confidence misjudgments** (low-06, low-09) — the model has
   essentially zero entropy at the failure point. The prompt-parroting
   reasoning shape from EXP-04 is the same one that produces these.
2. **Low-confidence boundary cases** (low-03, low-05) — temperature
   exposes that the model is genuinely uncertain, and sometimes finds
   the right answer.

**Production implications.**

- Single-pass at T=0.7 is *not* a robust 85% — it's an 80–85% expected
  band depending on which uncertain sentences land which way.
- A simple ensemble — say "majority of 3 seeds" — would push e4b to
  ~85% reliably (would catch low-03 most of the time, miss low-05
  most of the time, never catch low-06/-09). At ~30s/call × 3 = 90s
  per sentence, you'd be 2× slower than qwen-9b at v1b-xml T=0
  (~42s) for *worse* accuracy. So ensemble e4b doesn't beat
  single-call qwen.
- An asymmetric vote ("if any of N seeds says lowercase, output
  lowercase") would catch all four lowercase misses on this corpus
  given enough seeds, but would also generate false-cap→false-low
  flips elsewhere. Not a free lever.
- **Net:** e4b's ceiling on this corpus is around 84% with reasonable
  ensembling; qwen-9b + v1b-xml + the EXP-07a quote-fix gets to a
  genuine 100% on this corpus at ~42s/call. e4b is not a viable
  cheaper alternative — it's just a worse model.

## Standings — model × prompt grid (final on v0-sentences)

| model        | v0 acc | v1a acc | v1b acc | v1b-xml acc | best     |
|--------------|--------|---------|---------|-------------|----------|
| gemma4:26b   | 100.0% | 100.0%  | 100.0%  | 100.0%      | any      |
| qwen3.5:9b   |  84.2% |  89.5%  |  94.7%  | **100.0%**  | v1b-xml  |
| gemma4:e4b   |  90.0% |  85.0%  |  85.0%  |  80.0%      | v0       |
| gemma4:e2b   |  50.0% |  55.0%  |  60.0%  |  60.0%      | v1b/xml  |

Two production-viable candidates emerge: **gemma4:26b at 100% (~7s/call)**
and **qwen3.5:9b + v1b-xml at 100% on the 19/20 it answers (42s/call,
modulo the deterministic `cap-03` schema-violation patch)**. The choice
between them is mostly a latency/RAM trade-off — qwen-9b is ~6× slower
but lighter on RAM (~5 GB vs ~17 GB for 26b).

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
5. **Marker format is not just cosmetic.** EXP-05 swapped only the target
   marker (`[[…]]` → `<target>…</target>`) with prompt content held
   constant and saw qwen-9b move from 94.7% to 100% on the 19 sentences
   it answers — the gain came from a hard sentence whose previous miss
   was a confabulation, not a near-miss. Hypothesis: XML tags read to
   the model as "this string is *tagged for analysis*" while brackets
   read as "this string is *named/emphasized*", which biases attention
   toward specific-entity reasoning. Effect is model-dependent — same
   change cost e4b 5pp on the same corpus.
6. **Temperature has limited reach under grammar-constrained decoding.**
   EXP-06 showed `cap-03`'s schema violation reproduces byte-for-byte at
   T=0.7 — same exception type, same character offset. Under Ollama's
   `format=` constraint, the JSON grammar restricts which tokens are
   valid; temperature only diversifies among grammar-valid candidates,
   so a deterministic structural failure survives sampling noise.
   Practical implication: a parse-error retry layer that just bumps
   temperature won't help for this class of bug — the fix has to be at
   the input layer.
7. **The `cap-03` bug is an unescaped-quote bug — confirmed by EXP-07a.**
   When the input sentence contains `"…"`, qwen mirrors that quoting
   style verbatim into its `reasoning` string without escaping the
   inner double-quotes, breaking JSON. Doctoring the embedded
   `"District"` to `'District'` clears the parse error with the same
   prompt, model, and temperature. Production fix is a one-line input
   substitution; no prompt change required. Generalizable warning:
   under grammar-constrained JSON, any `"` characters in the input
   that the model is likely to quote back are JSON-encoding hazards.
8. **Temperature is asymmetric across model failure modes.** EXP-07b
   ran e4b × v1b-xml × T=0.7 over 5 seeds and found per-sentence
   stability splits cleanly into three buckets: stable-correct (18/20
   sentences, 100% across seeds), stable-wrong (low-06, low-09; 0/5
   correct — high-confidence wrong logits temperature can't escape),
   and unstable boundary cases (low-03, low-05; 1–3 of 5 correct).
   Aggregate 84% sits between the T=0 number (80%) and the lucky
   single-pass T=0.7 number (85%). Lesson: temperature only helps on
   sentences where the model has real entropy at the relevant
   decision point. Sentences where it's confident-wrong don't move,
   no matter how much sampling noise you add.

## Open questions / next experiments

- [ ] **EXP-08: v1b-xml-prompt × the labeled fixture corpus, binary subset.**
  The highest-information test we have left. v1b-xml is now the qwen
  baseline (100% on 19/19 of v0-sentences). Two real questions: (a) does
  qwen's controlled-corpus saturation transfer to messy real-fixture
  cases, and (b) does e4b stay near 80% or fall further. This is the
  test that would graduate v1b-xml from "saturated on a controlled set"
  to "shippable prompt."

  **Wired up and ready** — `rules/03-cap-district/eval/run_eval_v1bxml.py`.
  Reuses v1b-xml prompt + markers from `v0-sentences/run.py` verbatim,
  filters the fixture corpus to its binary subset (109 cap + 36 low =
  145 of 247 candidates; 102 `do_not_flag` excluded by design — same
  framing as v0-sentences, since deterministic out-of-scope handling is
  prefilter territory not LLM territory), applies the EXP-07a quote-fix
  to all inputs (catches the ~25 candidates with embedded `"ShortForm"`
  defined-term short-forms that would otherwise trigger qwen's JSON
  parse error), and reuses `score()` / `print_summary_table()` from
  `run_eval.py` so the output table matches the heavyweight baseline
  exactly. Model labels (`capitalize`/`lowercase`) get mapped to the
  three-label gold space (`must_capitalize`/`must_lowercase`) for direct
  comparison; the `do_not_flag` column will read 0 by construction.

  Run command (full 4-model sweep, ~2.5 hours dominated by qwen):

      .venv/bin/python rules/03-cap-district/eval/run_eval_v1bxml.py

  Results land at `eval/results.v1b-xml.{model}.json` (different
  namespace from the heavyweight `results.{model}.json` baselines).
- [x] ~~**`cap-03` schema-violation root-cause.**~~ Resolved by
  EXP-07a. Embedded `"…"` in the input induces unescaped quotes in
  qwen's `reasoning` string. Fix: a one-line input pre-process that
  substitutes embedded `"…"` for `'…'`. Belongs in the LS-CAP-02
  rule's sentence-extraction path — track as a production-rule
  implementation note rather than an open research question.
- [x] ~~**e4b diagnostic / multi-seed at T=0.7.**~~ Resolved by EXP-07b.
  e4b at T=0.7 is 84.0% across 5 seeds (not 85%). The +5pp single-pass
  lift was a lucky roll; expected lift is ~+4pp. Per-sentence
  stability shows e4b's failures split into stable-wrong (low-06,
  low-09 — high-confidence wrong) and unstable-boundary (low-03,
  low-05 — model has real uncertainty). Conclusion: even with
  ensembling, e4b can't beat qwen-9b + v1b-xml on this corpus, and
  it's slower (3 × 30s = 90s/sentence with 3-seed majority vs qwen's
  ~42s single-call). e4b is **not** a viable cheaper alternative.
- [ ] **Retry-on-parse-error in `shared/ollama_client.py`.** Schema
  violations are deterministic, so naive retry won't help qwen's
  `cap-03`. But might help genuinely transient cases on bigger corpora.
  Lower priority than initially thought.
- [ ] **v1-sentences corpus.** v0-sentences now saturates both 26b AND
  qwen-9b+v1b-xml at 100% (modulo `cap-03`). Harder cases are needed to
  differentiate the candidates. Build after the real-fixture eval if
  26b/qwen-9b still need stress-testing.
- [ ] **Marker-attention follow-up.** EXP-05's qwen `low-09` swing is
  too clean to ignore. Worth one targeted test: re-run *just* `low-09`
  on qwen with a few marker formats (`[[…]]`, `<target>…</target>`,
  `**…**`, no marker + index pointer) at temperature 0 to see how
  consistent the attention shift is. Mostly research curiosity, but if
  the effect generalizes it's a free lever for the production rule.
