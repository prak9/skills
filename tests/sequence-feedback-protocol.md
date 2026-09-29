# Sequence Feedback Development Packet

`sequence-feedback-cases.jsonl` contains six visible development cases, frozen before the associated instruction edit: policy-dependent coverage, delayed verification benefit, action credit, unsupported execution-policy changes, reward versus completion, and permitted abstention as a clean control.

Apply the isolated prompt-only forward execution and independent grading rules in `behavior-eval-contract.md`. Executors receive prompts and the applicable skill version, never criteria or sibling outputs. Keep both versions, full responses, actual read records and criterion-level grades. The fixed criteria judge decisions under the supplied hypothetical facts; they do not establish that a proposed experiment was actually run.

For the first comparison, explicitly load iterate, research-craft and its harness/quant references in both arms. This tests application, not automatic routing. One batch per arm shares context across six cases; exact model/seed/cost metadata unavailable from the harness remain unknown. Do not treat six within-batch outcomes as independent repeated trials. Freeze both arms during grading and preserve disagreements. Report ties as regression evidence, not improvement; add fresh unseen cases before claiming transfer. No permission for live orders or external writes follows from these tests.

This packet is not loaded by `evaluate_behavior_cases.py`. JSON parsing and static repository tests are not behavior passes. Initial comparison artifacts: `.research/sequence-feedback-20260929/`; their local presence is separate from this versioned case packet.
