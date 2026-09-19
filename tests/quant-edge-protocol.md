# Quant Edge Development Cases

`quant-edge-cases.jsonl` contains thirteen visible development cases for the incremental-information, observation-boundary, realization, decay, research-budget and discriminating-hypothesis instruction changes. The original nine prompts are unchanged; four additions cover external-observation transfer and information clocks, own-order feedback, shared validation blind spots, and cycle narratives versus risk limits. The additions were recorded before the associated instruction edits. These are development cases, not untouched holdouts. Existing frozen suites remain unchanged.

Baseline checks before editing: 42 repository tests and 12 result-analysis tests passed. These establish structural/script health, not model behavior. The cases were authored with the instruction change, so no independent behavioral improvement may be inferred from their existence or manual inspection.

For a forward comparison, provide an isolated executor only the prompt, relevant skill and necessary evidence. Keep model, tools, reasoning budget and permissions fixed; retain instruction revisions, raw answers, actual actions, reference reads, questions, operations and cost when available. Grade every criterion, including the clean negative; keyword matches do not suffice. All cases are hypothetical and authorize no trading, production changes or external writes.

The existing `evaluate_behavior_cases.py` does not load this packet. JSON/schema checks and review are not automated behavior passes. A full-suite forward comparison and cost comparison remain unrun. Targeted isolated smoke runs may check particular responses, but without a matched pre-change run they do not establish improvement or a full-suite pass. No new runtime approval gate is introduced.

## 2026-09-19 targeted smoke

`quant-edge-smoke-observed.json` retains five returned answers, instruction hashes, parent criterion review and limitations. Two executors received prompts without criteria and loaded current skills; cases within each executor shared a context. Four new cases and the existing clean negative were checked, not the full packet. Own-impact cost accounting was not explicitly exercised in the returned answer; the clean negative's read cost cannot be isolated from earlier questions. No measured before/after improvement, independent blind grading or instrumented external-action claim is made.

For this update, the 28 repository contract tests and 12 result-analysis regression tests passed; these remain structural/script checks, separate from the response-level smoke observations.
