# TASK-001: <Short descriptive title>

> Compact Full task package. Add detail only when it changes execution or verification.

- Status: `待开始`
- Plan mode: `Linear`
- Loop budget: `not applicable`
- Program: `../program.md`
- Plan node: `NODE-001`
- Context refs: `None`
- Preference refs: `None`
- Abstraction impact: `<none / reuse / new / modify / remove — choose one>`
- Output artifacts: `tasks/output/TASK-001-short-slug/`
- Owner: `<owner>`
- Created: `YYYY-MM-DD`
- Updated: `YYYY-MM-DD`

## Task 1: <Short descriptive title>

**Description:** <Observable result this task delivers.>

**Acceptance criteria:**

- [ ] <specific testable condition>

**Verification:**

- [ ] Tests/runtime check: `<command or N/A: reason>`
- [ ] Manual check: N/A unless runtime behavior needs a separate scenario.

**Dependencies:** None

**Context/Refs:** None

**Preference refs:** None

**Locked constraints:** None identified beyond accepted scope.

**Negotiable space:** Implementation details within acceptance criteria.

**Files likely touched:**

- None identified; inspect before editing.

**Estimated scope:** `Small`

## Abstraction Gate

For `none` or `reuse`, replace the table with `N/A: <concrete reason>`. For `new`, `modify`, or `remove`, complete every field.

| Field | Content |
|---|---|
| Concrete pressure / current consumers | pending |
| Existing pattern / direct alternative | pending |
| Boundary / owned invariant | pending |
| Explicit non-responsibilities | pending |
| Expected variation | pending |
| Concept count / indirection | pending |
| Coupling / interface impact | pending |
| Contract verification | pending |
| Rollback / deletion trigger | pending |

## Output Artifacts

Use `tasks/output/TASK-001-short-slug/` for the latest final snapshot. Keep it gitignored and overwrite stale outputs.

No deliverable artifact is planned yet.

## Atomic Implementation Plan

| Node | Status | Depends on | Action | Verification | Evidence |
|---|---|---|---|---|---|
| N-001 | `待开始` | `None` | <small implementation action> | <command or scenario> | None |

- Failure action: <retry, split, block, or escalate>

## Verification Matrix

Add `V-001` rows before `待验收` or `完成`; keep planned checks in the atomic plan until then.

## Checkpoint

- ID: `CP-001`
- Covers: `N-001`
- Requirement: <acceptance evidence>
- Human review: yes

## Current Loop Attempt

Not applicable (Linear).

## Latest Execution Snapshot

- Latest action: Not started
- Latest result: None
- Evidence: None
- Next: `N-001`

## Escalation

- Stop when a locked constraint or acceptance criterion must change.
- Show a checkpoint when risk or scope materially increases.

## Risks and Rollback

None identified. Add detection and rollback when a concrete risk appears.

## Standing Checklist

- [ ] Acceptance criteria are met and tied to evidence.
- [ ] Runtime behavior and relevant regressions were verified.
- [ ] Edge cases and error paths are handled or recorded as risk.
- [ ] Changes are scoped; no unrelated refactor or debug residue remains.
- [ ] Integration, security, documentation, and rollback were reviewed or marked N/A with a concrete reason.
- [ ] `tasks/output/` is gitignored and the latest snapshot is current or marked N/A with a concrete reason.

## Pre-completion Red Team

| # | Question | Answer |
|---|---|---|
| RT-1 | Would this evidence pass if the deliverable were broken? | <answer> |
| RT-2 | What material behavior was not verified? | <answer> |
| RT-3 | Does the result solve the original problem? | <answer> |
| RT-4 | What is the likeliest post-delivery failure path? | <answer> |

## Completion Writeback

- Final result: <observable result>
- Output artifacts: `tasks/output/TASK-001-short-slug/` current, or `N/A: <reason>`
- Memory writeback: <memory IDs, or `N/A: reason`>
- Remaining work: <next task or None>
- Completed: YYYY-MM-DD
