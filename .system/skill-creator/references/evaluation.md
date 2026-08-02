# Skill Evaluation Protocol

Use this protocol when a new or revised skill makes a behavioral claim worth testing. Keep a simple subjective skill lightweight; require paired evaluation before claiming that a complex skill improved.

## Contents

1. Freeze the contract
2. Write useful cases and assertions
3. Choose the baseline
4. Use the workspace layout
5. Execute paired runs
6. Grade and aggregate
7. Review and decide
8. Iterate without contaminating evidence

## Freeze The Contract

Create `evals/evals.json` in the skill under development, validate it, then copy the entire `evals/` directory into the sibling evaluation workspace before running candidates. Copying the directory preserves fixture paths relative to `evals.json`. Treat that snapshot as the frozen evaluator for the iteration. Do not let candidate executors edit it.

Use this schema:

```json
{
  "schema_version": 1,
  "skill_name": "example-skill",
  "acceptance": {
    "min_candidate_pass_rate": 0.8,
    "max_required_failures": 0,
    "min_pass_rate_delta": 0.0
  },
  "evals": [
    {
      "id": "realistic-case",
      "prompt": "A realistic user request",
      "expected_output": "The observable outcome that should exist",
      "files": ["fixtures/input.txt"],
      "assertions": [
        {
          "id": "correct-result",
          "text": "The output contains the correct result derived from input.txt.",
          "kind": "deterministic",
          "required": true
        }
      ]
    }
  ]
}
```

Run:

```bash
python scripts/validate_evals.py <skill-path>/evals/evals.json
```

Keep the schema strict so stale or misspelled fields fail before execution. Store fixture paths relative to `evals/evals.json`; the validator rejects missing files and paths that escape the eval directory.

## Write Useful Cases And Assertions

Start with at least three realistic cases that cover the main workflow, a hard boundary, and a likely failure mode. Expand the set before making a broad generalization claim. Prefer raw user-like prompts and representative files over prompts that reveal the intended implementation.

Write assertions that distinguish correct completion from plausible-looking output:

- Use `deterministic` for checks a script can decide exactly.
- Use `model` for semantic judgments with an explicit evidence burden.
- Use `human` for taste, visual quality, or consequential judgment that should not be delegated.
- Mark an assertion `required` when one failure must veto promotion.

Do not reward internal implementation details unless the task requires them. A file existing is weak evidence when its contents can be empty or wrong. Freeze assertions before editing the candidate; if the evaluator must change, label that as harness work and restart the comparison.

## Choose The Baseline

- For a new skill, run the same task without the skill.
- For an existing skill, snapshot the original skill before editing and use that snapshot.
- Use the same model, tools, permissions, prompt, fixture files, and run count for candidate and baseline.
- Pair runs close together. With limited parallel slots, run one candidate/baseline pair per wave rather than running every candidate first.

Treat an unpaired smoke test as diagnostic evidence only. Do not call it an improvement benchmark.

## Use The Workspace Layout

Keep execution artifacts outside the candidate skill:

```text
<skill-name>-eval-workspace/
├── contract/
│   ├── evals/
│   │   ├── evals.json
│   │   └── fixtures/                # Only when cases need input files
│   └── baseline-skill/              # Existing-skill comparisons only
└── iteration-1/
    ├── eval-realistic-case/
    │   ├── candidate/
    │   │   └── run-1/
    │   │       ├── outputs/
    │   │       ├── transcript.md
    │   │       ├── timing.json
    │   │       └── grading.json
    │   └── baseline/
    │       └── run-1/
    │           ├── outputs/
    │           ├── transcript.md
    │           ├── timing.json
    │           └── grading.json
    ├── benchmark.json
    ├── benchmark.md
    └── decision.md
```

Use the names `candidate/run-1` and `baseline/run-1` exactly. Add `run-2`, `run-3`, and so on only when repeated runs are justified. Keep run numbers paired for every eval.

## Execute Paired Runs

Give each executor only the task-local inputs it needs:

```text
Execute this task as a user request.
Skill: <candidate path, baseline snapshot path, or none>
Prompt: <frozen eval prompt>
Input files: <frozen fixture paths or none>
Write task outputs only to: <run-dir>/outputs/
Record a concise execution trace in: <run-dir>/transcript.md
Do not read the other configuration, grading files, acceptance thresholds, or prior conclusions.
```

Use independent subagents when available. Do not tell them the expected answer, suspected defect, or which configuration should win. If runs must be executed inline, disclose that independence is weaker.

Write `timing.json` only when the runtime reports real measurements:

```json
{
  "duration_seconds": 12.4,
  "total_tokens": 8421
}
```

Omit unavailable fields. Never estimate tokens from output characters or invent timing.

## Grade And Aggregate

Read `references/grading.md` before grading. Check deterministic assertions with scripts where practical. Grade candidate and baseline against the same frozen assertions, and save exact assertion IDs with boolean verdicts and specific evidence.

Run:

```bash
python scripts/aggregate_evals.py \
  <workspace>/iteration-1 \
  --evals <workspace>/contract/evals/evals.json
```

The aggregator rejects missing grades, unknown assertion IDs, unpaired runs, malformed timing, and stale eval directories. It produces `benchmark.json` plus a human-readable `benchmark.md`. It computes token and timing statistics only from reported samples.

## Review And Decide

Inspect representative outputs, transcripts, failed assertions, and tails before accepting the aggregate. Ask the user to review every `human` assertion and any consequential tradeoff. For close subjective comparisons, randomize labels A/B and use the blind-comparison protocol in `references/grading.md` before unblinding.

Accept only when all declared checks pass:

- candidate pass rate meets `min_candidate_pass_rate`;
- required failures do not exceed `max_required_failures`;
- candidate-minus-baseline pass rate meets `min_pass_rate_delta`;
- raw-output review reveals no material regression or evaluator gaming;
- the user accepts non-reducible taste or risk decisions.

Record the decision and evidence in `decision.md`. A better aggregate does not override a required failure, contaminated evaluator, or material human-review concern.

## Iterate Without Contaminating Evidence

Use failures to form one mechanism-level revision at a time. Preserve the frozen contract within an iteration. Put revised candidate runs in `iteration-2/`, compare against the declared baseline, and retain rejected results. Add new cases for newly discovered failure classes, but do not rewrite old failures into easy passes. Reserve untouched cases before making strong generalization claims.

Trigger accuracy is a separate evaluation surface. Do not claim automatic trigger precision or recall until the current Codex runtime exposes a reproducible way to observe skill selection; manual explicit invocation only tests skill behavior after selection.
