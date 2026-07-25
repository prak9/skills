# Program: CLI timeout validation

- Overall status: `进行中`
- Profile: `Lite`
- Active plan node: `NODE-001`
- Latest evidence: `None`
- Current blocker: `None`
- Next step: `NODE-001`
- Next checkpoint: `None`
- Next human decision: `None`
- Owner: `AI`
- Last updated: `2026-07-13`

## Outcome

- Problem: The CLI accepts non-positive timeout values and fails later with an unclear error.
- Success: Invalid values exit 2 with a clear message; positive values still reach the request path.
- Non-goals: Changing request retry behavior.

## Constraints

- Locked: Do not change retry or request semantics.
- Negotiable: Validation helper placement.

## Acceptance

| ID | Condition | Verification | Pass condition |
|---|---|---|---|
| A-001 | Reject zero and negative timeout values | `pytest tests/test_cli.py -k timeout` | Invalid cases exit 2; positive case passes |

## Plan

| Node | Status | Action | Verification | Evidence |
|---|---|---|---|---|
| NODE-001 | `进行中` | Add boundary validation and regression cases | `pytest tests/test_cli.py -k timeout` | None |
