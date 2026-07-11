# TASK-NNN: <Short descriptive title>

> A task package for one plan node. The top section defines the task contract; the atomic plan below breaks it into executable nodes with status, verification, and evidence.

- Status: `待开始 / 进行中 / 阻塞 / 待验证 / 待验收 / 完成 / 已取消`
- Plan mode: `Linear / Loop`
- Loop budget: `<max attempts or not applicable>`
- Program: `../program.md`
- Plan node: `NODE-NNN`
- Owner: `<person, role, or AI>`
- Created: `YYYY-MM-DD`
- Updated: `YYYY-MM-DD`

## Task N: <Short descriptive title>

**Description:** <One paragraph explaining what this task accomplishes and what observable state changes when it is done.>

**Acceptance criteria:**

- [ ] <Specific, testable condition>
- [ ] <Specific, testable condition>
- [ ] <Specific, testable condition>

**Verification:**

- [ ] Tests pass: `<test command or not applicable with reason>`
- [ ] Build succeeds: `<build/typecheck command or not applicable with reason>`
- [ ] Manual check: <what to verify manually, or not applicable with reason>

**Dependencies:** <Task numbers or NODE IDs this depends on, or `None`>

**Files likely touched:**

- `<src/path/to/file.ts>`
- `<tests/path/to/test.ts>`

**Estimated scope:** `Small: 1-2 files / Medium: 3-5 files / Large: 5+ files`

## Atomic Implementation Plan

| Node | Status | Depends on | Action | Likely touched | Verification | Evidence | If verification fails |
|---|---|---|---|---|---|---|---|
| N-001 | `待开始` | `None` | <specific implementation action> | `<path or module>` | `<command, check, or manual scenario>` | <fill after running> | <retry, split, block, or escalate> |

Node rules:

- Each node should fit in one focused implementation and verification session.
- Split nodes that touch more than 5 files.
- Split nodes whose action contains "and", "plus", "以及", or "并且".

## Verification Matrix

| Check | Covers | Method/command | Pass condition | Status | Evidence |
|---|---|---|---|---|---|
| V-001 | `N-001` | `<command or scenario>` | <clear condition> | `待验证` | <fill after running> |

## Checkpoint

| Checkpoint | Covers | Requirements | Human review |
|---|---|---|---|
| CP-001 | `N-001` | <tests, build, end-to-end flow, or manual acceptance> | `Yes / No` |

## Loop Iteration Log

Use this section when `Plan mode` is `Loop`. For linear tasks, keep one row with `Not applicable`.

| Iteration | Loop step | Node | Attempt | Verification result | Reflection | Plan delta | Next |
|---|---|---|---|---|---|---|---|
| L-001 | `Plan / Act / Verify / Reflect / Iterate / Pass` | `N-001` | <what was tried> | <test/build/manual result> | <why it passed/failed and what was learned> | <what changes next round> | <continue, split, block, escalate, or complete> |

## Execution Log

### E-001: <record title>

- Time: `YYYY-MM-DD`
- Node: `N-001`
- Type: `implementation / test / research / decision / blocker / rollback / manual acceptance`
- Action: <what changed or was checked>
- Result: `passed / failed / partial / blocked`
- Evidence: <test output, log, screenshot, commit, report, or manual note>
- Next: <next node, fix, split, or escalation>

## Escalation

Show a checkpoint before continuing when:

- an atomic node finishes but verification fails
- scope, acceptance criteria, hard constraints, or external contracts need to change
- the task package is ready to move to `待验收`

Stop and ask first when:

- <task-specific red-line condition>

## Risks and Rollback

| Risk | Impact | Prevention/detection | Rollback or containment |
|---|---|---|---|
| <risk> | <impact> | <measure> | <measure> |

## Completion Writeback

When this task package is done, update `../program.md`:

- update `Plan Dependency Graph` if node state changed
- update `Node Status` for `NODE-NNN`
- update `Loop State` if this task ran in Loop mode
- update `Task List` checkbox for this node
- fill evidence location
- update current status and next step
- update decisions or hypothesis results if this task changed them

Completion summary:

- Final result: <observable result>
- Key evidence: <V-NNN or E-NNN>
- Remaining work: <new task package or None>
- Completed: `YYYY-MM-DD`
