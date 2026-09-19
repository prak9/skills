# Learning-loop transfer review — 2026-09-19

## Decision

Accept one runtime clarification in [decision's causal reference](../decision/references/causal-analysis.md): compare new evidence with the original prediction, change only supported parameters, relationships or boundaries, and allow no revision when evidence is insufficient. A smaller effect need not invalidate the mechanism; narrowing a new model's domain cannot retroactively rescue the old broad prediction. No new mandatory labels, forms or approval steps.

Keep `research-craft`, `result-analysis` and `plan-skill` runtime instructions unchanged. Their existing rules handled the tested learning and recovery behaviors. Add executable regression evidence instead of duplicating the investment framework across every skill. No changes to `invest`, `writing`, `code-review-craft` or `AGENTS.md`.

## Actual behavioral checks

The [protocol](learning-transfer-protocol.md) and [case packet](learning-transfer-cases.json) were frozen before the decision edit. Five fresh executor contexts produced ten user-turn responses. Research, quant and plan received successive evidence only after each preceding answer finished; decision used one isolated baseline and one isolated candidate context.

| Sequence | Observed result | Frozen criteria |
|---|---|---|
| Research, 3 turns | Recorded 10ms, then 11ms predictions; settled the 19ms observation as a miss; introduced a path-conditioned model with new 8/17ms predictions without rewriting old scope | R1–R4 pass |
| Quant, 3 turns | Began unresolved; paired data localized +0.40bp incremental opportunity before arrival, without treating it as proven net PnL or a causal acceleration benefit; repeated data did not cause a new diagnosis | Q1–Q4 pass |
| Decision, baseline/candidate | Both retained the original 4pp forecast, revised to 2pp, computed A=0 (−200..200) versus B=600 per month and chose B without extra confirmation | D1–D3 pass in both arms |
| Plan, 2 turns | Resumed from files, preserved 120-row acceptance, added a failing completeness test, repaired pagination, completed Lite state; unchanged followup reused evidence with no new reflection | P1–P4 pass |

These are 18 criterion judgments across five runs, not 18 independent tasks. Parent inspection and two independent grading contexts agreed. Graders saw version/path information: this was **not blind grading**. Both decision arms passed, so no measured improvement is claimed; the edit removes an overly narrow instruction, not an empirically demonstrated failure.

## Evidence beyond self-report

[learning-transfer-observed.json](learning-transfer-observed.json) preserves all ten user inputs and complete responses, executor-reported actions, instruction hashes, the exact candidate diff, both independent grades, final plan artifacts and parent verification results. Temporary absolute paths in original responses identify their original run locations; the archived `plan_artifacts` can reconstruct the project without those directories.

The parent independently confirmed:

- The initial fixture's old HTTP-status test passes while the output has only 100 rows.
- The recovered export contains exactly 120 unique IDs, covering 1..120, with HTTP 200; both executor-written tests pass.
- Replacing the repaired exporter with the original implementation makes the new completeness test fail with `120 != 100` while the status-only test still passes.
- Original source and previous evidence are byte-identical; the acceptance section is unchanged; the final Lite plan passes strict validation.
- All project-file hashes remain identical across the no-new-information followup. No fresh reflection or implementation was added.

Deterministic checks: 28 existing repository contract tests and 5 new fixture/archive regression tests passed. The latter reconstruct and replay the archived repair, including the deliberately broken implementation control. These checks establish artifact behavior, not model performance. Scoped `git diff --check` passed. An unrelated pre-existing whitespace error in `.system/plugin-creator/references/installing-and-updating.md` prevents a clean whole-worktree check; it was left untouched.

## Cost and limits

- Per-turn file reads, commands, writes and counts are recorded in executor traces. They are self-reported, not independent tool telemetry; assertions about unrecorded network or external actions cannot be independently established from them.
- Both decision arms report reading the same three instruction files. The candidate also read its two output files back. A single pair does not attribute this overhead to the wording change or demonstrate efficiency gains.
- The plan followup reports zero test reruns, zero project writes and zero new reflections. The unchanged project hashes corroborate the write claim, not the complete absence of unrecorded commands.
- Exact runtime model ID, token use, billing and comparable execution latency were unavailable. Inherited model/reasoning settings were not overridden. No GPT-6 Astra-specific reliability or cost claim follows from this probe.
- These are fictional, visible development cases, one run per context. There is no held-out generalization result, live trading validation or full production recovery test. Quant's future experiment still needs predeclared operational timing, sample and economic thresholds; no outcome was fabricated.

The new cases supplement rather than replace earlier frozen suites; their previously unrun cases remain unrun. No deployment, commit or push was performed.

After checking all ten archived responses and eight project artifacts against their original bytes, the two task-created temporary test directories were removed. Necessary evidence remains in the archive and the fixture replay test. During this work, another task advanced HEAD to `65d01ec` with Xiaohongshu-only changes; the frozen snapshots still correspond to `aeece47`, and this task's changes remain uncommitted.
