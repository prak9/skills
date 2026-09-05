# Status And Completion Contract

Read this file before setting `阻塞`, `待验收`, or `完成`, or when status and evidence disagree.

## Status Vocabulary

Use `待开始 / 进行中 / 阻塞 / 待验证 / 待验收 / 完成 / 已取消`. `探索中` is also valid for a program.

In Full plans, each task package owns its status. `program.md` links task packages and derives project state from them; it does not repeat task status.

## Status Transitions

- `阻塞`: name the missing information, permission, prerequisite, or external state and the exact unblock action.
- `待验证`: implementation exists but the declared verifier has not passed.
- `待验收`: verification evidence is complete and only an explicitly retained, still-pending human decision remains; name its owner and subject. Do not invent this decision from a template or a generic preference for human review.
- `完成`: acceptance conditions passed, evidence is recorded, no active node remains, and required durable writeback is done.
- `已取消`: record the reason and any consequence for dependent work.

Do not cross a required readiness gate while it is `Blocked`. Authorized investigation and independent work can continue. If the current program represents only gated work, keep that program blocked; if an authorized diagnostic is the next node, scope the readiness contract to that diagnostic and mark it `Ready` without treating the downstream mutation as authorized.

## Completion Bar

For every task:

- acceptance criteria are checked and tied to evidence;
- relevant runtime behavior or an explicit scoped alternative was verified;
- atomic nodes are terminal;
- every completed Full Linear node records either a triggered evidence-linked `R-*` or `None: <no trigger reason>`; every verified Loop attempt points to an `R-*`;
- the completion review states the observable result, evidence, unverified behavior or residual risk, remaining work, and completion date;
- consequential decisions or findings are written once to `memory.md`.

For risky changes, also review applicable migration, compatibility, security, observability, rollback, and human-approval requirements. Add a deeper red-team checklist only when the risk warrants it; do not force an empty universal questionnaire.

For a changed public or Agent-facing workflow whose documentation is part of acceptance, require evidence from the affected documented journey against the delivery version, as defined in `executable-spec-contract.md`. A required path that failed or has not run remains `待验证`, or `阻塞` when an external prerequisite prevents verification. Use `待验收` only after technical evidence is complete and an explicit owner decision remains; record that decision before `完成`. Passing unit tests or reviewer agreement cannot substitute for the missing journey evidence or owner decision.

For Loop or unattended repeated jobs, also require the declared independent checker and raw evidence path, confirm verification was finer than the change slice, and name any retained human judgment. An ordinary autonomous task does not require a separate reviewer. When safe ownership depends on understanding, include the necessary explanation; require teach-back only for an explicit requirement or concrete operational gap.

For a Lite plan, the Plan table, Reflection Log, and top-level status carry the same evidence and reflection contract without a task package.

When acceptance is satisfied and no retained decision remains, record `完成` and deliver the result. Do not stop at a plan, first implementation, passing subtask, or optional polish. Report required but blocked work precisely; do not relabel it complete or let an independent optional follow-up keep finished work open.
