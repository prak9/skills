# Judgment Training for Code Review

Use deliberate review practice to build the quality function that automation cannot supply. Optimize for calibrated judgment, not the number of comments produced.

## Run the practice loop

1. **Choose a real artifact.** Use a meaningful PR, defect, subsystem, incident, or design change rather than a toy style exercise.
2. **Predict first.** Before reading test results or reviewer comments, record likely failure modes, decisive invariants, expected evidence, and confidence.
3. **Review independently.** Reconstruct the system and produce findings without using the known answer as a map.
4. **Reveal evidence.** Run tests, inspect logs, read final reviewer decisions, or compare with the incident outcome.
5. **Score the process.** Separate a lucky verdict from sound reasoning and an unlucky miss from a disciplined process.
6. **Record surprise.** Add the smallest durable lesson to the error ledger.
7. **Reapply soon.** Find another change where the same heuristic could succeed or fail.

Do not leak expected findings into the independent review phase. A test of memory is not a test of judgment.

## Keep an error ledger

Record one entry whenever the reviewer or Agent misses, invents, mis-severities, or correctly anticipates a surprising issue:

```text
date / artifact:
review decision:
prediction and confidence:
what actually happened:
miss | false positive | severity error | comprehension error | good catch:
why the original model failed:
new boundary or heuristic:
next artifact that can test it:
```

Review the ledger after 20–30 artifacts. Group repeated misses by underlying boundary—ownership, state, concurrency, compatibility, security, observability—not by superficial syntax. Retire heuristics that create more false positives than useful findings.

## Protect deliberate practice

Regularly perform work that keeps the mental model grounded:

- read a change and explain it without proposing edits;
- trace one request from entry to persistence and back;
- hand-simulate a parser, state machine, retry loop, or transaction through failure;
- write the specification and invariants before looking at the implementation;
- take one subsystem to its breaking point and document the first violated assumption;
- review the same code before and after seeing tests, then compare what the tests changed in the model;
- implement a small but meaningful component manually when the goal is learning rather than delivery.

Use automation after the prediction to accelerate searches, tests, and comparisons. Keep specification, validation criteria, and final acceptance separate from generation.

## Evaluate a reviewer or Agent

Use a frozen rubric and a representative set of real changes. Start with 20 artifacts for diagnosis; use roughly 50 or more before making a strong comparative claim.

Score at least:

- **valid-defect recall:** proportion of known, in-scope defects found;
- **precision:** proportion of reported findings that survive expert review;
- **severity calibration:** whether impact and likelihood match the assigned priority;
- **comprehension accuracy:** whether the behavior, invariants, and failure path are explained correctly;
- **evidence quality:** whether findings have reproducible or code-level support;
- **test selection:** whether chosen checks are informative rather than merely broad;
- **decision calibration:** whether confidence and approve/reject recommendations match outcomes;
- **review cost:** time, tool calls, and reviewer burden per useful finding.

Keep the artifact set, rubric, known findings, scoring rules, and reviewer context fixed during a comparison. Include clean changes so a reviewer cannot score well by always objecting. Preserve hidden or held-out artifacts to detect adaptation to the evaluator.

Inspect disagreements rather than trusting the aggregate score. An alleged false positive may expose a missing specification; a known finding may itself be wrong or irrelevant.

## Calibrate autonomy by consequence

Choose the least supervision that preserves judgment and safety:

| Task | Reversibility and evidence | Default autonomy |
|---|---|---|
| Search, call-graph mapping, candidate edge cases | Cheap, inspectable | High |
| Boilerplate or mechanical refactor with strong tests | Reversible, well-scored | High with sampled review |
| Ordinary product change | Moderate impact, partial evaluator | Agent executes; human reviews evidence |
| Public API, migration, concurrency, billing | Expensive or cross-system | Human owns spec and independent review |
| Auth, privacy, destructive operation, architecture | Hard to reverse; judgment-heavy | Low; explicit human approval required |

Increase autonomy only after repeated evidence shows both high defect recall and low false confidence in that task class. Reduce it after surprises, evaluator gaps, or changes in system context.

## Measure the last mile

Track whether the reviewer catches work left after the generated draft appears complete:

- boundary behavior and error semantics;
- compatibility and migration sequencing;
- observability and diagnosability;
- cleanup, rollback, and recovery;
- operational ownership and rollout safety;
- whether the implementation solves the difficult version rather than only the demo.

When draft production becomes cheap, these qualitative decisions become the product of review. Keep them visible in the scorecard.
