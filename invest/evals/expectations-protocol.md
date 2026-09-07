# Expectations And Capital Allocation — Development Checks

`expectations-cases.jsonl` is the `invest-expectations-v1` supplementary development packet. It does not change the frozen core suite or its holdouts. All ten cases have been visible during instruction development; none is an unseen acceptance case.

## Execution And Evidence

Before editing a candidate, freeze the current skill, this packet, and the grading criteria. Give an independent executor only the case ID, prompt, selected skill entry, and its on-demand references—not `expected_behavior`, `criteria`, `numeric_checks`, a diff, or the proposed fix. Each prompt is a self-contained hypothetical, not a request for live investment data or an external write. Tools for local arithmetic are allowed. Evaluate cases in fresh contexts for a controlled comparison; a single-context batch is only a smoke check and must be labeled as such.

Keep model, reasoning effort, task inputs, tool access, and harness fixed across old/new instruction comparisons. Preserve the full answer and observed tool actions, revision or content hashes, run time, and counts of reference reads, follow-up questions, operations, and external mutations. Reuse the run-record fields in [the repository behavior contract](../../tests/behavior-eval-contract.md), with case-set version `invest-expectations-v1`. The repository's deterministic evaluator currently supports only its named suites; do not pass this packet to it or claim its envelope checks validate these cases.

## Grading

- Independently recalculate `numeric_checks`; rates there are fractions, not percentage numbers. Accept equivalent units and disclosed rounding, normally within 0.01 percentage point or 0.01 currency/revenue/share unit. Intermediate rounding must not reverse the decision.
- Grade every `criteria` item from the full answer and observed actions, not keyword matching. Correct arithmetic with an unsupported valuation or action still fails.
- These complete hypothetical inputs should not require a blocking question, extra skills, production access, or an external mutation. Load only the references needed for the case; investigate any increase in reads or operations rather than treating longer answers as improvement.
- A development pass requires all applicable numeric and semantic criteria. Preserve failed and unchanged results. Passing existing data-validator tests does not establish a valuation-behavior pass.

Use a blinded reviewer of the raw outputs when feasible. Record whether the review is independent, whether contexts were isolated, and which cases actually ran. Before claiming a general improvement for a particular model, repeat under its real harness on newly sealed acceptance cases and representative ordinary Quick/Full requests. A small forward smoke check supports only the observed cases, not out-of-sample investment performance.
