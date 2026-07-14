# Status And Completion Contract

Read this file before setting a program or task to `阻塞`, `待验收`, or `完成`, and when auditing contradictory status or evidence.

## Status Vocabulary

Use one controlled vocabulary across `program.md` and task packages:

```text
待开始 / 进行中 / 阻塞 / 待验证 / 待验收 / 完成 / 已取消
```

`探索中` is additionally valid for the program-level overall status.

## Status Transitions

- Set `完成` only after acceptance criteria pass, evidence is recorded, and required writeback is done.
- Set a program to `待验收` only when every node is `待验收`, `完成`, or `已取消`; at least one node awaits acceptance; and latest evidence, next checkpoint, and next human decision are concrete.
- Set a task to `待验收` only when implementation, verification, checklists, red-team answers, evidence, and writeback are ready, but human acceptance remains.
- Set a program to `阻塞` only when at least one node is `阻塞` and Current Status names the blocker and unblock condition.
- Use `阻塞` only for missing information, permission, external state, or a failed prerequisite.
- Give every incomplete atomic node a concrete next verification action.
- Keep primary table IDs unique, and keep each `TASK-NNN-*.md` filename ID identical to its H1 ID.

## Completion Bar

Complete the Standing Checklist before moving a task to `待验收` or `完成`. Check every applicable item; record `N/A: <reason>` for each non-applicable item.

Per task:

- tie acceptance criteria to evidence
- verify runtime behavior, not only compilation or typechecking
- add a regression test that fails without the change, or record why it is not applicable
- run relevant tests, build/typecheck, lint, and formatting, or record scoped exclusions
- handle edge cases and error paths, or record them as known risks
- keep the diff scoped and remove unrelated refactors, duplicated logic, dead code, debug output, and commented-out blocks

For a feature or risky change:

- cover migrations, configuration, feature flags, public contracts, and backward compatibility
- document changed interfaces, user behavior, and durable architecture decisions
- review security implications for untrusted input, authorization, and data handling
- define observability and rollback for new critical paths
- require human review before merge, deployment, or acceptance when appropriate

Do not treat written code as completion. Require acceptance evidence, a completed Standing Checklist, answered Pre-completion Red Team questions, and writeback.
