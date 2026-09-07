# Versioned Skill Behavior Evaluation

The frozen core suite contains 24 cases: six each for `decision`, `writing`, `invest`, and `plan-skill`. Four cases per skill are development cases; two are acceptance cases. The separate instruction-migration suite contains eight cases for skill routing, question behavior, and proportional verification. Acceptance cases should not be used to tune the next prompt or rule before the recorded run is graded.

Each harness configuration writes one schema-v2 JSONL record per case:

```json
{
  "schema_version": 2,
  "id": "decision-sufficient-direct-holdout",
  "run_context": {
    "model": "gpt-6-astra",
    "reasoning_effort": "medium",
    "harness": "codex-cli 1.2.3",
    "instruction_revision": "git:abc123",
    "skill_revision": "git:def456",
    "case_set_version": "core-v1",
    "run_at": "2026-09-05T12:00:00Z",
    "evaluator": "independent-reviewer-v1"
  },
  "output": "the complete user-visible response",
  "skills_loaded": ["decision"],
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

`operations` counts tool calls and other harness actions beyond producing the answer; keep its counting rule fixed across compared runs. `reference_reads` counts on-demand instruction or skill-reference files beyond the selected skill entry, not the project source and evidence that the task necessarily inspects; count those reads as operations or in an additional harness-specific metric. A required external write counts as both an operation and an external mutation. `skills_loaded` records actual activation, not the skills the evaluator expected to see.

Every non-obvious run-context field is required so results from different models, reasoning profiles, harnesses, instructions, or case revisions cannot be compared as if only one variable changed. All selected records in one results file must share that run identity; `run_at` may differ by case. The evaluator requires `core-v1`, `instruction-migration-v1`, or `all-v1` to match the selected suite. Use `not-applicable` rather than an empty value when a field genuinely does not apply.

Run the deterministic envelope checks with:

```bash
python3 tests/evaluate_behavior_cases.py results.jsonl --split development
python3 tests/evaluate_behavior_cases.py results.jsonl --split acceptance
python3 tests/evaluate_behavior_cases.py migration-results.jsonl --suite instruction-migration
```

A split passes only when every selected case passes. The evaluator checks required and forbidden output evidence, actual skill activation, tool prefixes, all four cost budgets, complete run metadata, and the independent behavior verdict. Do not accept a keyword-only pass: `behavior_evidence` must assess the named behavior, including stop-versus-answer, semantic preservation, authorization, routing, proportional verification, or selective revalidation as applicable.

When a new rule raises reads, questions, or operations, compare it with the frozen baseline on the same cases. Keep the extra cost only if the changed cases show a material correctness, fidelity, authorization, or recoverability gain; record that comparison outside the holdout outputs so the holdouts remain usable.

The deterministic evaluator and its unit-test fixtures validate the result envelope; they are not model runs. A model or instruction migration is not verified until real harness records with raw outputs and observed actions have been graded.

## Principle-Transfer Development Packet

`principle-transfer-cases.jsonl` is a supplementary `principle-transfer-v1` packet for timing decisions, abstraction fidelity, resource tradeoffs, completion boundaries, and audience-aware writing. All cases are visible development cases, not new holdouts. Keep the core and instruction-migration suites unchanged.

Freeze this packet before editing candidate instructions. A forward executor receives only each `prompt`, the selected skill, and necessary source artifacts, not the expected behavior or criteria. Grade actual responses and actions against every criterion, including clean negatives; matching a phrase is insufficient. Use isolated contexts and fixed model/harness settings for comparisons, and preserve raw outputs, tool actions, revisions, and the cost metrics defined above. Record unavailable metadata as unknown and narrow comparative claims accordingly.

The deterministic evaluator does not load this packet or accept its case-set version. Review its run records separately rather than reporting an unsupported automated pass. Parsing fixtures or inspecting instructions checks their structure, not model behavior; without actual recorded executions these cases remain unrun. Do not extend the evaluator or require a model benchmark for ordinary unrelated edits merely because the packet exists.
