# Memory: <Project Name>

> Durable project memory. Store important findings, reusable knowledge, CHANGELOG entries, run-log summaries, failed-attempt lessons, and historical execution summaries here.
> `program.md` remains the source of truth for current plan and latest node status only. Task packages keep active execution state only.

- Last updated: `YYYY-MM-DD`
- Program: `program.md`

## 1. Important Findings

Only keep findings that should affect future planning or implementation.

| ID | Status | Finding | Impact | Evidence | Source | Date |
|---|---|---|---|---|---|---|
| F-001 | `有效 / 已废弃 / 待验证` | <important fact, system behavior, constraint, hidden dependency, or failure cause> | <effect on future planning or implementation> | <test, log, commit, report, or task package> | <TASK-NNN / L-NNN / Checkpoint> | `YYYY-MM-DD` |

## 2. Knowledge Base

Reusable knowledge that future agents should apply.

| ID | Category | Knowledge | Applies when | Boundary / counterexample | Evidence |
|---|---|---|---|---|---|
| K-001 | `implementation / testing / architecture / product / ops / data / process` | <reusable knowledge> | <when to use it> | <when it does not apply> | <evidence link or task package> |

## 3. Changelog

Meaningful changes to plan, implementation, interfaces, dependencies, acceptance criteria, or decisions. Do not create a separate CHANGELOG file unless explicitly requested.

| ID | Time | Type | Scope | Summary | Trigger | Evidence | Impact |
|---|---|---|---|---|---|---|---|
| CHG-001 | `YYYY-MM-DD` | `plan / code / test / docs / decision / dependency / release` | <NODE-NNN, TASK-NNN, module, or interface> | <what changed> | <why it changed> | <commit, task package, test, review, or record> | <effect on later plans or users> |

## 4. Run Logs

Runtime logs are distilled records of execution, verification, rollout, rollback, manual acceptance, or Loop attempts. Link raw terminal output, CI logs, screenshots, or artifacts instead of pasting large logs.

| ID | Time | Scope | Type | Action | Result | Evidence | Next | Distillation |
|---|---|---|---|---|---|---|---|---|
| RUN-001 | `YYYY-MM-DD` | <TASK-NNN, NODE-NNN, L-NNN, or command> | `implementation / test / build / verify / rollout / rollback / manual acceptance / loop` | <what was done> | `passed / failed / partial / blocked` | <log, command output, CI, screenshot, report, or task package> | <next step or none> | `待提炼 / 不需要 / produced K-R-PL-F ID` |

## 5. History Summaries

Summarize task-package and checkpoint history. Do not duplicate raw logs; link to them.

| ID | Time | Scope | Result | Key evidence | Lesson / later impact |
|---|---|---|---|---|---|
| HIST-001 | `YYYY-MM-DD` | <TASK-NNN, NODE-NNN, or Checkpoint> | `完成 / 阻塞 / 已取消 / partial` | <RUN-NNN, CHG-NNN, test, or commit> | <summary future agents need> |

## 6. Failures And Rework

Preserve failures that reduce future search space.

| ID | Time | Failure / rework | Root cause | Ruled-out options | Future rule |
|---|---|---|---|---|---|
| R-001 | `YYYY-MM-DD` | <failure symptom or rework> | <verified or suspected root cause> | <approaches not to repeat> | <future execution rule> |

## 7. Open Knowledge Gaps

Track unknowns that are not current blockers but matter later.

| ID | Status | Question | Why it matters | Validation method | Related plan node |
|---|---|---|---|---|---|
| Q-001 | `待验证` | <unknown> | <impact> | <validation method> | `NODE-NNN / None` |

## 8. Preference Learning

Capture what execution taught about preferences, tradeoffs, locked constraints, or negotiable space.

| ID | Learned preference | Previous assumption | Evidence | Scope | Promote to default? |
|---|---|---|---|---|---|
| PL-001 | <what we now know matters> | <old assumption or blank> | <RUN-NNN、CHG-NNN、TASK-NNN 或 review> | `strategic / tactical` | `yes / no / later` |

## 9. Reflection And Curation

Treat this file as an evolving playbook, not a rewrite target. Execution writes traces (`RUN`); reflection distills lessons (`K/R/PL/F`); curation only changes specific ID-based entries.

Trigger a reflection pass when a task package completes, blocks, or is cancelled, or when `待提炼` run logs reach 5.

Process:

1. Reflect: Review `待提炼` RUN/R entries and extract lessons from success and failure.
2. Curate: Add or revise ID-based K/R/PL/F entries; do not rewrite unrelated sections.
3. Mark sources: Set each RUN entry's `Distillation` field to the produced ID or `不需要`.
4. Compact: Summarize distilled execution history as `HIST-NNN`; mark replaced entries `已废弃` with a pointer instead of deleting them.

Avoid:

- Brevity bias: Do not flatten concrete lessons into vague principles. Distilled entries need trigger conditions, scope, boundaries, and evidence.
- Context collapse: Do not "clean up" by rewriting the whole file. Change entries by ID; when merging duplicates, keep the surviving ID and mark merged entries `已废弃`.

## 10. Update Rules

- Important findings need evidence pointers; do not record impressions alone.
- Preference Learning records only preference discoveries that should change future planning or execution.
- Changelog entries record changes with later impact, not ordinary edit history.
- Run logs are summaries with evidence pointers; do not paste full terminal output or long CI logs.
- History summaries record conclusions and impact; do not duplicate run logs.
- Failure records must name ruled-out options so future agents do not repeat them.
- If a finding becomes stale, mark it `已废弃`; do not silently delete it.
- For every completed, blocked, or cancelled task package, decide whether CHG/RUN/F/K/HIST/R/PL writeback is needed. If not, explain `不需要` in the task completion writeback.
