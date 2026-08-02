# Skill Eval Grading And Blind Comparison

Use this reference after paired runs exist. Keep deterministic checks in code, semantic checks evidence-based, and human judgment visible.

## Grade Assertions

Give a grader the frozen eval entry, one unlabeled run directory, and only the source artifacts needed to verify it. Do not provide the candidate Skill, baseline identity, expected winner, prior diagnosis, or acceptance thresholds unless an assertion explicitly requires inspecting process behavior.

For each assertion:

1. Inspect the actual output and relevant transcript evidence.
2. Run a deterministic checker when the assertion can be decided mechanically.
3. Pass only when specific evidence demonstrates substantive completion.
4. Fail when evidence is missing, contradictory, unverifiable, or merely superficial.
5. Flag weak assertions separately instead of quietly raising their score.

Write `<run-dir>/grading.json` exactly as:

```json
{
  "assertions": [
    {
      "id": "correct-result",
      "passed": true,
      "evidence": "Checked outputs/result.json: total is 42 and matches the fixture."
    }
  ],
  "notes": [
    "The formatting assertion is verifiable only by human review."
  ]
}
```

Use every assertion ID from the frozen eval exactly once. Do not add summary fields; the aggregator derives totals and rejects missing or unknown IDs.

## Protect Grading Integrity

- Grade the outcome, not confidence or eloquence in the transcript.
- Treat claims in the output as hypotheses until artifacts verify them.
- Keep the burden of proof on a passing verdict.
- Do not let candidate code write `grading.json` or alter fixtures.
- Use the same grader instructions and tools for candidate and baseline.
- Route `human` assertions to the user; record their verdict and evidence without substituting model taste.
- Regrade both configurations if the rubric changes.

## Blind Comparison

Use blind comparison when assertions miss an important subjective difference or the user asks whether one version is actually better.

1. Randomly assign candidate and baseline outputs to labels A and B outside the comparator's context.
2. Give the comparator the original prompt, output A, output B, and a task-specific rubric fixed before comparison.
3. Hide Skill contents, transcripts, configuration names, benchmark scores, and prior feedback.
4. Require a winner of A, B, or tie with evidence tied to the artifacts.
5. Unblind only after the verdict is saved.
6. Analyze which instruction or resource plausibly caused the difference; do not infer causation from one win alone.

Use this result shape:

```json
{
  "winner": "A",
  "reasoning": "A is more accurate because ...",
  "criteria": [
    {
      "name": "factual-accuracy",
      "a": 5,
      "b": 3,
      "evidence": "A preserves all three source values; B changes the second."
    }
  ]
}
```

Repeat close or high-variance comparisons with swapped labels. Treat a single model preference as qualitative evidence, not a calibrated probability.

## Inspect The Evaluator

Before promotion, look for:

- assertions that pass in both configurations and do not discriminate;
- assertions that fail everywhere and may be impossible or malformed;
- large run-to-run variance;
- output-format compliance that hides incorrect content;
- candidate behavior that targets grader wording rather than the user outcome;
- latency or token costs that erase the quality gain;
- regressions visible in raw artifacts but absent from the assertions.

Repair evaluator defects as a separate harness change, then freeze and rerun both configurations.
