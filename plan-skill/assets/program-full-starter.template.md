# Program: <Project Name>

> Compact Full starter. Expand a section only when the work produces relevant state.

- Overall status: `待开始`
- Profile: `Full`
- Plan mode: `Linear`
- Loop state: `Not applicable`
- Loop iteration: `Not applicable`
- Memory: `memory.md`
- Active task package: `tasks/TASK-001-short-slug.md`
- Task output root: `tasks/output/` (gitignored)
- Active plan node: `NODE-001`
- Next plan node: `None`
- Latest evidence: `None`
- Next checkpoint: `CP-001`
- Owner / TL: `<owner>`
- Last updated: `YYYY-MM-DD`

## Concept Refinement

| Field | Content |
|---|---|
| Source | <request, issue, spec, or code context> |
| Problem statement | <one-sentence problem> |
| Target user | <specific user or system actor> |
| Success criteria | <observable outcome> |
| Direction | <chosen approach and why> |
| Non-goals | <what this round excludes> |

## Problem Definition

<Current problem, why it matters, constraints, and non-goals.>

## Context And References

None yet. Add `CTX-*`, `REF-*`, or `OWN-*` entries only when they change execution.

## Preferences And Tradeoffs

- Preferences: None yet; add `PREF-*` only when a tradeoff matters.
- Tradeoffs: None yet.
- Locked constraints: None identified beyond accepted scope.
- Negotiable space: implementation details within acceptance criteria.
- Escalation rule: ask before changing scope or acceptance criteria.

## Goals And Metrics

### Acceptance Criteria

| ID | Acceptance criterion | Verification method | Pass condition | Owner |
|---|---|---|---|---|
| A-001 | <observable result> | <test, command, or review> | <clear condition> | AI |

## Constraints

- None identified beyond accepted scope and non-goals.

## Strategy

<Smallest vertical path to the acceptance criterion.>

### Dependency And Slicing Strategy

```text
NODE-001 -> acceptance
```

## Decisions

None yet. Add a stable ID only when a decision constrains future work.

## Exploration And Hypothesis Validation

None identified. Add a hypothesis only with a validation method and pass/fail action.

## Implementation Plan

### Overview

<What the current vertical slice delivers.>

### Architecture Decisions

- None yet.

### Plan Dependency Graph

```text
NODE-001 First vertical slice (待开始)
```

### Node Status

| Node | Status | Task package | Evidence |
|---|---|---|---|
| NODE-001 | `待开始` | `tasks/TASK-001-short-slug.md` | None |

### Node Details

| Node | Size | Dependencies | Acceptance | Updated |
|---|---|---|---|---|
| NODE-001 | `Small` | `None` | `A-001` | `YYYY-MM-DD` |

### Loop Contract

Not applicable (Linear).

### Loop State

Not applicable.

### Memory Sync

| Type | Status | Source | memory.md location | Updated |
|---|---|---|---|---|
| Finding / run / change | pending | TASK-001 | memory.md | YYYY-MM-DD |

### Task List

- [ ] NODE-001 / `tasks/TASK-001-short-slug.md`: first vertical slice

### Checkpoints

| Checkpoint | Position | Verification requirements | Human review |
|---|---|---|---|
| CP-001 | After NODE-001 | <tests and acceptance evidence> | yes |

## Optional State

- Parallelization: None until shared contracts are clear.
- Risks: None identified.
- Open questions: None.

## Current Status

- Current blocker: None
- Current risk: None
- Next step: TASK-001 / N-001
- Next human decision: None
- Pending memory write: None

## Update Protocol

- Keep current state here; write history and durable findings to `memory.md`.
- Keep atomic execution state in the task package.
- Run strict validation before execution, handoff, or completion.
