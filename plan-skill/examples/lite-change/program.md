# Program: CLI timeout validation

- Overall status: `进行中`
- Profile: `Lite`
- Plan mode: `Linear`
- Execution readiness: `Not required`
- Memory: `None`
- Active task package: `tasks/TASK-001-validate-timeout.md`
- Task output root: `tasks/output/` (gitignored)
- Active plan node: `NODE-001`
- Latest evidence: `None`
- Owner: AI
- Last updated: 2026-07-13

## Concept Refinement

None: the accepted request already specifies the input, behavior, and error message.

| Field | Content |
|---|---|
| Source | Accepted CLI validation issue |
| Problem statement | Reject non-positive timeout values before starting a request |
| Target user | CLI operators |
| Success criteria | Invalid values exit 2 with a clear message; positive values still work |
| Direction | Validate at the argument boundary |
| Non-goals | Changing request retry behavior |

## Execution Readiness Gate

N/A: The accepted issue defines the exact invalid inputs, exit code, message, positive control, and focused regression command.

## Problem Definition

The CLI currently accepts zero or negative timeout values and fails later with an unclear runtime error. This change validates only that boundary and does not alter request behavior.

## Goals And Metrics

### Acceptance Criteria

| ID | Acceptance criterion | Verification method | Pass condition |
|---|---|---|---|
| A-001 | Reject zero and negative timeout values | `pytest tests/test_cli.py -k timeout` | Invalid cases exit 2; positive case passes |

## Implementation Plan

### Node Status

| Node | Status | Task package | Evidence |
|---|---|---|---|
| NODE-001 | `进行中` | `tasks/TASK-001-validate-timeout.md` | None |

### Node Details

| Node | Size | Dependencies | Acceptance | Updated |
|---|---|---|---|---|
| NODE-001 | `Small` | `None` | `A-001` | 2026-07-13 |

## Current Status

- Current blocker: None
- Next step: TASK-001 N-001
- Next human decision: None
- Pending memory write: None; no durable finding yet
