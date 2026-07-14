# TASK-NNN: <Short descriptive title>

> Lite task package for one focused, independently verifiable plan node. Use exactly one concrete value for every choice field.

- Status: `<待开始 / 进行中 / 阻塞 / 待验证 / 待验收 / 完成 / 已取消 — choose one>`
- Plan mode: `Linear`
- Program: `../program.md`
- Plan node: `NODE-NNN`
- Output artifacts: `tasks/output/TASK-NNN-<slug>/`
- Owner: `<person, role, or AI>`
- Updated: `YYYY-MM-DD`

## Task N: <Short descriptive title>

**Description:** <Observable result this task delivers.>

**Acceptance criteria:**

- [ ] <specific testable condition>
- [ ] <specific testable condition>

**Verification:**

- [ ] Tests/runtime check: `<command or N/A: concrete reason>`
- [ ] Manual check: <scenario or N/A: concrete reason>

**Dependencies:** <NODE/TASK IDs or None>

**Locked constraints:** <must not change without escalation, or None>

**Negotiable space:** <implementation details the agent may optimize, or None>

**Files likely touched:**

- `<path>`

**Estimated scope:** `Small / Medium — choose one`

## Output Artifacts

Use `tasks/output/TASK-NNN-<slug>/` for the latest final output snapshot. Keep `tasks/output/` gitignored and overwrite stale outputs rather than accumulating history.

| Artifact | Path | Source step | Status | Notes |
|---|---|---|---|---|
| <name> | `tasks/output/TASK-NNN-<slug>/<file>` | <command or step> | `current / not produced / N/A` | <what it proves or why absent> |

## Atomic Implementation Plan

| Node | Status | Depends on | Action | Verification | Evidence |
|---|---|---|---|---|---|
| N-001 | `待开始` | `None` | <small implementation action> | <command or scenario> | <fill after running> |

- Failure action: <retry, split, block, or escalate>

## Standing Checklist

- [ ] Acceptance criteria are met and tied to evidence.
- [ ] Runtime behavior was verified, or `N/A: <reason>`.
- [ ] New behavior has a regression test, or `N/A: <reason>`.
- [ ] Existing relevant tests pass.
- [ ] Edge cases and error paths are handled or recorded as risk.
- [ ] Changes are scoped; no unrelated refactor or debug residue remains.
- [ ] Integration, security, documentation, and rollback were reviewed, or each has `N/A: <reason>`.
- [ ] `tasks/output/` is gitignored and the latest output snapshot is current, or `N/A: <reason>`.

## Pre-completion Red Team

| # | Question | Answer |
|---|---|---|
| RT-1 | Would this evidence still pass if the deliverable were broken? | <answer> |
| RT-2 | What material behavior was not verified? | <answer> |
| RT-3 | Does the result solve the original problem? | <answer> |
| RT-4 | What is the likeliest post-delivery failure path? | <answer> |

## Completion Writeback

- Final result: <observable result>
- Output artifacts: `tasks/output/TASK-NNN-<slug>/` current, or `N/A: <reason>`
- Memory writeback: `<memory IDs, or N/A: concrete reason>`
- Remaining work: <next task or None>
- Completed: `YYYY-MM-DD`
