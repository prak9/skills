# Core Skill Behavior Evaluation

The fixed suite contains 24 cases: six each for `decision`, `writing`, `invest`, and `plan-skill`. Four cases per skill are development cases; two are acceptance cases. Acceptance cases should not be used to tune the next prompt or rule before the recorded run is graded.

Each harness run writes one JSONL record:

```json
{
  "id": "decision-sufficient-direct-holdout",
  "output": "the complete user-visible response",
  "tool_calls": ["tool names in observed order"],
  "metrics": {
    "reference_reads": 1,
    "followup_questions": 0,
    "external_mutations": 0,
    "operations": 1
  },
  "behavior_pass": true,
  "behavior_evidence": "short criterion-by-criterion justification from an independent evaluator"
}
```

`operations` counts tool calls and other harness actions beyond producing the answer; keep its counting rule fixed across compared runs. `reference_reads` counts on-demand files beyond the selected skill entry. A required external write counts as both an operation and an external mutation.

Run the deterministic envelope checks with:

```bash
python3 tests/evaluate_behavior_cases.py results.jsonl --split development
python3 tests/evaluate_behavior_cases.py results.jsonl --split acceptance
```

A split passes only when every selected case passes. The evaluator checks required and forbidden output evidence, actual tool prefixes, all four cost budgets, and the independent behavior verdict. Do not accept a keyword-only pass: `behavior_evidence` must assess the named behavior, including stop-versus-answer, semantic preservation, authorization, or selective revalidation as applicable.

When a new rule raises reads, questions, or operations, compare it with the frozen baseline on the same cases. Keep the extra cost only if the changed cases show a material correctness, fidelity, authorization, or recoverability gain; record that comparison outside the holdout outputs so the holdouts remain usable.
