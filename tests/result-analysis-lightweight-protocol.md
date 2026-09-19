# Result-analysis proportionality development probes

The five prompts in `result-analysis-lightweight-cases.jsonl` were frozen before the simplification. They are visible development cases, not holdouts, and are not loaded by `evaluate_behavior_cases.py`.

Preserve the same model/settings, prompt and read-only permissions for before/after probes. Each executor receives one prompt, the skill when applicable, and no criteria or change rationale. Restrict it to supplied evidence and skill files; do not read real trading data or run experiments. Record the raw answer, instruction snapshot, actual reference reads and any side effects. A routing probe receives only discovery descriptions before deciding which skill to open.

Acceptance: the requested answer remains correct, project metric/causal and live-risk boundaries survive, and arithmetic or research-only requests do not create unrelated report work. Use file reads as a limited overhead proxy, not a claim about tokens, latency or trading quality. Mark any action count based only on executor self-report. Do not count unrun cases as passes or tune against frozen core holdouts.

Pre-edit structural baseline: 28 repository contract tests and 12 result-analysis regression tests passed. No runtime script, evaluator, trading policy or production state is being changed.

## Observed 2026-09-19

`result-analysis-lightweight-observed.json` records seven returned answers: two single-run before/after pairs and three candidate-only cases. Parent criterion review found the five candidate responses consistent with the frozen criteria. Arithmetic reference reads went from 1 to 0; research-only reads went from 2 to 1, removing the daily image/operations reference. Both baselines already gave appropriate user-facing answers; the observed difference is unnecessary instruction reading, not a demonstrated correctness gain.

The routing probe used candidate frontmatter locally, not the installed runtime selector. Independent-evidence and live-boundary cases shared a context, so their costs are not isolated. Reads/actions are executor self-reports, no tokens or latency were measured, and no statistical or holdout improvement is claimed. A separate static reviewer found no substantive loss of original operational thresholds, data semantics or authority boundaries. The 28 contract tests, 12 script tests and skill validator also passed after editing.
