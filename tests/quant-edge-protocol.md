# Quant Edge Development Cases

`quant-edge-cases.jsonl` contains nine visible development cases for the incremental-information, observation-boundary, realization, decay, research-budget and discriminating-hypothesis instruction changes. The original six prompts are unchanged; three additions cover inconclusive versus contradicted claims, post-decision selection, and domain-specific failure learning. They are not untouched holdouts. Existing frozen suites remain unchanged.

Baseline checks before editing: 42 repository tests and 12 result-analysis tests passed. These establish structural/script health, not model behavior. The cases were authored with the instruction change, so no independent behavioral improvement may be inferred from their existence or manual inspection.

For a forward comparison, provide an isolated executor only the prompt, relevant skill and necessary evidence. Keep model, tools, reasoning budget and permissions fixed; retain instruction revisions, raw answers, actual actions, reference reads, questions, operations and cost when available. Grade every criterion, including the clean negative; keyword matches do not suffice. All cases are hypothetical and authorize no trading, production changes or external writes.

The existing `evaluate_behavior_cases.py` does not load this packet. JSON/schema checks and review are not automated behavior passes. Forward model runs and cost comparisons remain unrun until actual outputs/actions are collected and graded. No new runtime approval gate is introduced.
