# Status And Completion Contract

Read this file before setting `阻塞`, `待验收`, or `完成`, or when status and evidence disagree.

## Status Vocabulary

Use `待开始 / 进行中 / 阻塞 / 待验证 / 待验收 / 完成 / 已取消`. `探索中` is also valid for a program.

In Full plans, each task package owns its status. `program.md` links task packages and derives project state from them; it does not repeat task status.

## Status Transitions

- `阻塞`: name the missing information, permission, prerequisite, or external state and the exact unblock action.
- `待验证`: implementation exists but the declared verifier has not passed.
- `待验收`: verification evidence is complete and only an explicit human decision remains.
- `完成`: acceptance conditions passed, evidence is recorded, no active node remains, and required durable writeback is done.
- `已取消`: record the reason and any consequence for dependent work.

Do not move execution forward while a required readiness gate is `Blocked`.

## Completion Bar

For every task:

- acceptance criteria are checked and tied to evidence;
- relevant runtime behavior or an explicit scoped alternative was verified;
- atomic nodes are terminal;
- every completed atomic node points to an evidence-linked `R-*` reflection;
- the completion review states the observable result, evidence, unverified behavior or residual risk, remaining work, and completion date;
- consequential decisions or findings are written once to `memory.md`.

For risky changes, also review applicable migration, compatibility, security, observability, rollback, and human-approval requirements. Add a deeper red-team checklist only when the risk warrants it; do not force an empty universal questionnaire.

For Loop or unsupervised execution, also require the declared independent checker and raw evidence path, confirm verification was finer than the change slice, and name any retained human judgment. When safe ownership depends on understanding, include an explainer or teach-back that traces intent, change, sensor, evidence, and residual risk.

For a Lite plan, the Plan table, Reflection Log, and top-level status carry the same evidence and reflection contract without a task package.
