# TASK-001: Validate CLI timeout

- Status: `进行中`
- Plan mode: `Linear`
- Program: `../program.md`
- Plan node: `NODE-001`
- Abstraction impact: `none`
- Output artifacts: `tasks/output/TASK-001-validate-timeout/`
- Owner: AI
- Updated: 2026-07-13

## Task 1: Validate CLI timeout

**Description:** Validate timeout values at the CLI boundary so invalid input fails immediately with the documented exit code and message.

**Acceptance criteria:**

- [ ] Zero and negative values exit 2 with `timeout must be positive`.
- [ ] A positive timeout still reaches the request path.

**Verification:**

- [ ] Tests/runtime check: `pytest tests/test_cli.py -k timeout`
- [ ] Manual check: `demo --timeout 0` prints the validation message.

**Dependencies:** None

**Locked constraints:** Do not change retry or request semantics.

**Negotiable space:** Validation helper placement.

**Files likely touched:**

- `src/cli.py`
- `tests/test_cli.py`

**Estimated scope:** `Small`

## Abstraction Gate

N/A: The change adds boundary validation in the existing CLI path without changing a shared abstraction.

## Output Artifacts

Use `tasks/output/TASK-001-validate-timeout/` for the latest final output snapshot. Keep `tasks/output/` gitignored and overwrite stale outputs.

| Artifact | Path | Source step | Status | Notes |
|---|---|---|---|---|
| CLI transcript | `tasks/output/TASK-001-validate-timeout/manual-check.txt` | manual check | not produced | Produce after N-001 passes |

## Atomic Implementation Plan

| Node | Status | Depends on | Action | Verification | Evidence | If verification fails |
|---|---|---|---|---|---|---|
| N-001 | `进行中` | `None` | Add validation and regression cases | `pytest tests/test_cli.py -k timeout` | pending | inspect parser boundary and revise |

## Standing Checklist

- [ ] Acceptance criteria are met and tied to evidence.
- [ ] Runtime behavior was verified.
- [ ] Regression tests fail without the change and pass with it.
- [ ] Existing relevant tests pass.
- [ ] Edge cases and error paths are covered.
- [ ] Changes remain scoped and clean.
- [ ] Integration, security, documentation, and rollback are reviewed.
- [x] `tasks/output/` is gitignored.

## Pre-completion Red Team

| # | Question | Answer |
|---|---|---|
| RT-1 | Would this evidence still pass if the deliverable were broken? | Pending until the verifier runs |
| RT-2 | What material behavior was not verified? | Pending until completion review |
| RT-3 | Does the result solve the original problem? | Pending until completion review |
| RT-4 | What is the likeliest post-delivery failure path? | Pending until completion review |

## Completion Writeback

- Final result: pending
- Output artifacts: `tasks/output/TASK-001-validate-timeout/` pending
- Memory writeback: pending; decide at completion
- Remaining work: N-001
- Completed: pending
