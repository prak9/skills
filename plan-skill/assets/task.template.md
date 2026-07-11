# TASK-NNN: <Short descriptive title>

> A task package for one plan node. The top section defines the task contract; the atomic plan below breaks it into executable nodes with current status, verification, and latest evidence pointers. Historical run logs and changelog entries belong in `../memory.md`.

- Status: `待开始 / 进行中 / 阻塞 / 待验证 / 待验收 / 完成 / 已取消`
- Plan mode: `Linear / Loop`
- Loop budget: `<max attempts or not applicable>`
- Program: `../program.md`
- Plan node: `NODE-NNN`
- Context refs: `CTX-NNN / REF-NNN / REF-EXT-NNN / OWN-NNN`
- Preference refs: `PREF-NNN / None`
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

**Context/Refs:** <CTX/REF IDs from `../program.md#2-context-and-references`, or `None`>

**Preference refs:** <PREF IDs from `../program.md#3-preferences-and-tradeoffs`, or `None`>

**Locked constraints:** <constraints this task must not change without escalation, or `None`>

**Negotiable space:** <implementation details the agent may optimize or propose alternatives for, or `None`>

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

## Current Loop Attempt

Use this section when `Plan mode` is `Loop`. Keep only the current/latest attempt here. Move completed attempt summaries to `../memory.md#4-run-logs`.

| Iteration | Loop step | Node | Attempt | Verification result | Reflection | Plan delta | Next |
|---|---|---|---|---|---|---|---|
| L-001 | `Plan / Act / Verify / Reflect / Iterate / Pass` | `N-001` | <what was tried> | <test/build/manual result> | <why it passed/failed and what was learned> | <what changes next round> | <continue, split, block, escalate, or complete> |

## Latest Execution Snapshot

Keep this section to the latest execution state only. Write chronological run logs to `../memory.md#4-run-logs` and reference their IDs here.

| Field | Value |
|---|---|
| Snapshot ID | `E-001` |
| Time | `YYYY-MM-DD` |
| Node | `N-001` |
| Type | `implementation / test / research / decision / blocker / rollback / manual acceptance` |
| Latest action | <what changed or was checked> |
| Latest result | `passed / failed / partial / blocked` |
| Evidence | <test output, log, screenshot, commit, report, or manual note> |
| Memory refs | `RUN-NNN / CHG-NNN / HIST-NNN / None` |
| Next | <next node, fix, split, or escalation> |

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

## Standing Checklist

Complete applicable items before moving this package to `待验收` or `完成`. Mark non-applicable items as `N/A: <reason>`.

### Per Task

- [ ] Acceptance criteria are met and tied to evidence.
- [ ] Runtime behavior was verified, not only compiled or typechecked.
- [ ] New behavior is covered by tests that fail without the change and pass with it, or `N/A: <reason>`.
- [ ] Existing tests still pass; no regression signal is ignored.
- [ ] Relevant edge cases and error paths are handled or recorded as known risk.
- [ ] Changes are scoped to this task; no unrelated refactors are included.
- [ ] No duplicated business logic, dead code, debug output, or commented-out blocks were left behind.
- [ ] Linting and formatting pass, or `N/A: <reason>`.

### Per Feature / Risky Change

- [ ] Integration points are accounted for: migrations, config, feature flags, public contracts, and backward compatibility.
- [ ] Public interfaces, APIs, user-facing behavior, and durable architecture decisions are documented when changed, or `N/A: <reason>`.
- [ ] Security implications are reviewed for untrusted input, auth, and data handling, or `N/A: <reason>`.
- [ ] Observability is in place for new critical paths, or `N/A: <reason>`.
- [ ] Rollback or containment path is defined for risky changes, or `N/A: <reason>`.
- [ ] Human review is complete before merge, deploy, or acceptance when required, or `N/A: <reason>`.

## Pre-completion Red Team

Answer all four questions before moving this package to `待验收` or `完成`.

| # | Question | Answer |
|---|---|---|
| RT-1 | If the deliverable were actually broken, would the evidence above still pass? If yes, the evidence proves nothing — replace it with a check that can fail. | <answer> |
| RT-2 | What was NOT verified? (inputs, error paths, concurrency, scale, platforms) | <explicit list, or why nothing material is missing> |
| RT-3 | Re-read the original problem in `../program.md#1-problem-definition` — the original text, not this task's restatement. Does the result solve it? | <yes with reason / gap found> |
| RT-4 | What is the single most likely post-delivery failure path? Rule it out now, or record it as a known risk in `../memory.md`. | <what was done> |

## Completion Writeback

When this task package is done, update `../program.md`:

- update `Plan Dependency Graph` if node state changed
- update `Node Status` for `NODE-NNN`
- update `Loop State` if this task ran in Loop mode
- update `Task List` checkbox for this node
- update `Memory Sync` when changelog entries, run logs, durable findings, or execution summaries were written
- fill evidence location
- update current status and next step
- update decisions or hypothesis results if this task changed them
- update `program.md#2-context-and-references` if new context, entry points, refs, or owners were discovered
- update `program.md#3-preferences-and-tradeoffs` if execution reveals a better tradeoff, wrong assumption, or changed preference
- do not append changelog, run-log, or historical status sections to `program.md`

Also update `../memory.md`:

- add important findings to `memory.md#1-important-findings`
- add reusable knowledge to `memory.md#2-knowledge-base`
- add changelog entries to `memory.md#3-changelog`
- add run-log entries to `memory.md#4-run-logs`
- add task outcome summary to `memory.md#5-history-summaries`
- add failed-attempt lessons to `memory.md#6-failures-and-rework`
- add preference learning to `memory.md#8-preference-learning`
- run the reflection pass (`memory.md#9-reflection-and-curation`): distill this task's `待提炼` run logs into K/R/PL/F entries, or mark them `不需要`
- if no memory writeback is needed, record that decision in this task's completion summary

Completion summary:

- Final result: <observable result>
- Key evidence: <V-NNN or E-NNN>
- Memory writeback: `CHG-NNN / RUN-NNN / F-NNN / K-NNN / HIST-NNN / R-NNN / 不需要：<原因>`
- Remaining work: <new task package or None>
- Completed: `YYYY-MM-DD`
