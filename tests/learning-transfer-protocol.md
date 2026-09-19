# Learning-loop transfer: sequential regression probes

## Frozen contract

- Baseline: `aeece47f72e6635e8aced652bb41100d6cdee790`.
- Packet: [learning-transfer-cases.json](learning-transfer-cases.json).
- Packet SHA256 before the runtime edit: `14ff352372bb68c34c21b602d4c6f71bf04289088a81685d05d03841ae5fa045`.
- Editable runtime surface: one paragraph in `decision/references/causal-analysis.md`. Other runtime instructions stay unchanged unless an observed failure warrants a separately recorded revision.
- Acceptance: the packet's behavioral criteria, not terminology, paragraph count or a self-reported success label. Preserve any failing run.

These supplement the existing frozen suites; they do not replace their cases or claim that previously unrun evaluations were run. All inputs are fictional. They are visible development probes, not a held-out benchmark.

## Execution

Use a fresh executor for each sequence and each decision arm. Give it only the skill snapshot, current user turn and scoped artifact destination. Send the next turn only after the previous answer has completed and been preserved. Do not expose future inputs or grading criteria to executors.

- Research: initial model → changed intercept → new path/boundary. Check old forecasts are settled rather than rewritten.
- Quant: unpaired aggregate → paired lifecycle → no new evidence. Check attribution becomes more specific without turning observational evidence into an execution intervention's causal benefit.
- Decision: one identical prompt per old/new paragraph. Update magnitude and action without forcing a structural rewrite.
- Plan: copy the [offline pagination fixture](fixtures/learning-transfer/pagination), resume and actually fix it, then issue a no-new-information followup. Do not alter the original source, acceptance or prior evidence.

Only the decision probe has a before/after comparison. The other sequences test existing behavior. One run per sequence/arm cannot establish reliability, comparative uplift, generalization or a particular model's capabilities.

## Verification and reporting

Preserve full prompts, responses, instruction versions, executor action reports and final plan artifacts. Independently replay the repaired exporter and run its new test against the original implementation; a green test alone does not show that the escaped defect is detected. Validate the final Lite plan separately from the runtime behavior.

Report actual behavioral results separately from deterministic fixture/unit tests. Action traces are executor self-reports unless independently captured. Missing exact model identifier, token counts, billing and timing remain unknown; file reads or response length are not token-cost measurements. Do not call a grader blind if paths or diffs expose arm identity.

No deployment, external write, live strategy action, commit or push is part of these probes.

Actual results and limitations: [learning-transfer-review.md](learning-transfer-review.md). Full run archive: [learning-transfer-observed.json](learning-transfer-observed.json). Replay the offline artifacts with `python3 -B -m unittest discover -s tests -p test_learning_transfer_fixtures.py -v`; this is not a rerun of model behavior.
