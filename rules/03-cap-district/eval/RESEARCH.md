# LS-CAP-02 prompt-engineering research — index

LS-CAP-02 is a Tier 4 rule: it requires LLM judgment on whether each
candidate trigger word ("district", "board", "city", etc.) refers to a
specific identifiable entity (capitalize) or a generic class
(lowercase). Multiple prompt-design approaches are being investigated
in parallel against the same corpora; this file is the cross-arm index
and final-comparison report. Detailed lab notebooks for each approach
live in their own files — keep this file slim, link to them for depth.

## Shared corpora

Both arms test against the same two corpora so per-sentence and
per-candidate behavior is directly comparable across approaches:

- **`v0-sentences/sentences.json`** — 20 hand-crafted single sentences
  (10 cap / 10 low), each gold-labelable from the sentence alone. The
  controlled-corpus harness for fast prompt iteration.
- **`candidates.{clean,kitchen-sink,realistic-mixed}.json`** — 247
  candidates extracted from three demurrer fixtures. The binary subset
  (109 cap + 36 low = 145; the 102 `do_not_flag` cases are excluded by
  design — out-of-scope handling is the deterministic prefilter's job,
  not the LLM's). The fixture eval is each approach's graduation test.

## Approaches under investigation

### Prose-prompts arm — `RESEARCH-prose.md`

**Status: complete (EXP-01–08).**

Iterates natural-language prompt content (rule statement, legal
context, significance cues), target-marker formats (`[[…]]`,
`<target>…</target>`), and sampling temperature. Best result is
qwen3.5:9b + v1b-xml-prompt: 93.1% accuracy on the fixture binary
subset, zero schema errors, 77.8% recall on the harder lowercase
class. Required one input pre-process (substituting embedded
`"ShortForm"` with `'ShortForm'`) to clear a deterministic JSON-decode
bug on qwen.

### Code-prompts arm — `RESEARCH-code.md`

**Status: planned, no experiments yet.**

Hypothesis: small recent open models (gemma4, qwen3.5) treat
code-shaped prompts as a familiar register and may judge more
reliably from compact code-style templates (rule-as-JSON-examples,
partial-schema-completion, etc.) than from prose statements.
Iterates against the same shared corpora as the prose arm.

## Best-of-arm results — fixture binary subset (n=145)

| approach        | best model + prompt           | acc        | cap-R   | low-R   | lat (s) |
|-----------------|-------------------------------|------------|---------|---------|---------|
| prose-prompts   | qwen3.5:9b + v1b-xml          | **93.1%**  |  98.2%  |  77.8%  |  54.6   |
| code-prompts    | (pending)                     |  —         |  —      |  —      |  —      |

## Cross-approach comparison

Pending the code-prompts arm. Once a stable best variant emerges this
section will be rewritten as a head-to-head: same fixture corpus, same
metric, with attention to whether the approaches fail on the same
candidates (suggesting a hard underlying bottleneck) or different
candidates (suggesting an ensemble would beat either alone). The
final shipping decision goes here too.
