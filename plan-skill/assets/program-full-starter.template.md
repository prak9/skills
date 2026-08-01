# Program: <Project Name>

> Durable current state. Task packages own task status and execution evidence.

- Overall status: `待开始`
- Profile: `Full`
- Plan mode: `Linear`
- Execution readiness: `Blocked`
- Loop state: `Not applicable`
- Loop iteration: `Not applicable`
- Memory: `memory.md`
- Active task package: `tasks/TASK-001-short-slug.md`
- Latest evidence: `None`
- Current blocker: `None`
- Next step: `TASK-001 / N-001`
- Next checkpoint: `CP-001`
- Owner / TL: `<owner>`
- Last updated: `YYYY-MM-DD`
- Clean state: `Not due`
- Last clean: `Not run`

## Outcome

- Problem: <observable problem>
- Success: <observable result>
- Non-goals: <scope intentionally excluded>

## Execution Readiness Gate

Keep `Blocked` only while a missing judgment or evidence gap could change scope, method, risk, or whether to proceed. Use `Not required` with a concrete reason for a directly verifiable specification.

| Field | Content |
|---|---|
| Decision this work informs | <decision changed by pass or fail> |
| Key uncertainty / hypothesis | <material uncertainty or falsifiable claim> |
| Pass / fail evidence | <evidence that permits or stops execution> |
| Cheapest informative check | <smallest belief-changing check> |

## Context

None yet. Add only references that change execution.

## Constraints And Decisions

- Locked constraints: <must not change without escalation, or None>
- Negotiable space: <implementation choices the agent may make>
- Decisions: None yet.

## Acceptance

| ID | Condition | Verification | Pass condition |
|---|---|---|---|
| A-001 | <observable condition> | <command or review> | <clear result> |

## Node Index

| Node | Task package | Dependencies | Acceptance |
|---|---|---|---|
| NODE-001 | `tasks/TASK-001-short-slug.md` | None | A-001 |

## Loop Contract

Not applicable (Linear). For Loop mode, replace this section using `references/loop-contract.md`.

## Loop State

Not applicable (Linear). For Loop mode, replace this section using `references/loop-contract.md`.

## Checkpoints

| Checkpoint | After | Requirement | Human review |
|---|---|---|---|
| CP-001 | NODE-001 | <acceptance evidence> | yes |

## Current Status

- Next human decision: None
- Pending memory write: None
