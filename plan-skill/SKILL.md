---
name: plan-skill
description: Use this skill to turn a raw idea, vague project, existing spec, or ongoing implementation into a controlled plan-and-execution loop. It refines ideas into program.md, creates or repairs AI-executable plans, decomposes work into tasks/TASK-*.md packages, keeps latest per-task output snapshots under gitignored tasks/output/TASK-*/ directories, tracks verification and checkpoints, and preserves durable findings in memory.md. Trigger when the user asks to refine an idea, ideate, stress-test a plan, create an implementation plan, break down tasks, run Loop-mode execution, manage project control, clarify preferences/tradeoffs, order dependencies, slice work vertically, define acceptance criteria, track evidence, write run logs/CHANGELOG/history, or hand off coding work across sessions.
---

# Plan Skill

Use this skill to move from idea to verified implementation without losing state. It has three authoritative artifacts:

```text
program.md                 # Current state: concept brief, plan, status, blockers, next step, links.
memory.md                  # Durable history: findings, lessons, changelog, run logs, summaries.
tasks/TASK-NNN-<slug>.md   # Executable task packages with atomic nodes, verification, and evidence.
tasks/output/TASK-NNN-<slug>/  # Latest final output snapshot for that task package; gitignored.
```

Do not create `codemap.md` by default. Keep implementation maps inside the relevant task package unless they become large enough to deserve a separate file.

If downstream tooling requires `tasks/plan.md` or `tasks/todo.md`, generate them only from `program.md` and `tasks/TASK-*.md`. They are exports, not sources of truth.

Task output artifacts live under `tasks/output/TASK-NNN-<slug>/`, matching the task package filename without `.md`. This directory records the latest final output state for that task only. If outputs change across attempts, overwrite or replace the previous files so the directory shows the current final state; do not append timestamped versions or chronological history there. Keep `tasks/output/` ignored by git by default.

## Operating Model

- `program.md` owns the refined concept, current plan, task-package status, blockers, checkpoints, and next action. It must stay current-state only.
- `tasks/TASK-*.md` owns task execution state: atomic nodes, latest attempt, verification, evidence, blockers, rollback, and completion writeback.
- `tasks/output/TASK-*/` owns the latest final task output artifacts, such as generated reports, screenshots, exports, review bundles, or acceptance files. It is not a run log and should not accumulate old versions.
- `memory.md` owns durable knowledge: findings, reusable lessons, changelog entries, run logs, failed attempts, and history summaries.
- Code, tests, logs, screenshots, CI, and runtime output are facts. Markdown records intent, status, decisions, and evidence pointers.
- Chat is not durable. Write decisions that matter into `program.md` or the active task package. Write reusable discoveries into `memory.md`.
- Never silently reconcile drift. Name the conflicting sources, pick the authority, and update it.

## Profiles

Declare `- Profile: Lite / Full` in `program.md`; `scripts/validate_plan.py` defaults to `Full`.

- `Full`: Use for multi-session, multi-package, Loop-mode, high-risk, or handoff-heavy work.
- `Lite`: Use for one or two focused sessions. `program.md` needs Concept Refinement, Problem Definition, Acceptance Criteria, Node Status, and Current Status. Each task package needs the Task contract, Atomic Implementation Plan, Standing Checklist, Pre-completion Red Team, and Completion Writeback. `memory.md` is optional until the first durable finding.
- Semantic rules apply in both profiles: `完成`/`待验收` requires evidence; statuses must agree across files; hypotheses close only with a verdict and evidence.
- Upgrade Lite to Full once the plan grows beyond about three task packages, spans multiple sessions, or needs Loop mode.

## Stage 0: Concept Refinement

Use this stage when the input is still a raw idea, multiple directions are plausible, target users are unclear, success criteria are missing, or the user asks to ideate, refine, or stress-test a plan.

Skip it when the user already provides a clear spec, accepted direction, or existing plan.

Goal: refine raw ideas into sharp, actionable concepts worth building through structured divergent and convergent thinking.

```text
Idea -> Concept brief -> Plan -> Task packages -> Execute -> Verify -> Memory
```

### Understand And Expand

- Restate the idea as a concise "How might we..." problem statement.
- Ask at most 3-5 sharpening questions. Target user and success criteria are required.
- If inside a codebase, read relevant specs, entry points, tests, and prior docs before generating options.
- Generate 5-8 considered variations using only useful lenses: inversion, simplification, audience shift, constraint removal, adjacent combination, 10x scale, or expert-domain obviousness.

### Evaluate And Converge

After the user reacts, cluster promising options into 2-3 distinct directions. Stress-test each on:

- user value: who benefits, how much, and whether the idea is a painkiller or a vitamin
- feasibility: technical/resource cost and hardest unknown
- differentiation: why it wins or why users would switch

For each direction, name what must be true, what could kill the idea, and what is intentionally ignored for now. Be direct when an idea is weak.

### Sharpen And Ship The Brief

Write the confirmed one-page brief into `program.md#0-concept-refinement`. Do not create a separate idea document by default.

Map the brief into the plan:

- Problem Statement -> `program.md#1-problem-definition`
- Target User / Success Criteria -> `program.md#4-goals-and-metrics`
- Recommended Direction -> `program.md#6-strategy`
- Key Assumptions -> `program.md#8-exploration-and-hypothesis-validation`
- MVP Scope -> initial `program.md#9-implementation-plan` nodes
- Not Doing -> `program.md#1-problem-definition` Non-goals
- Open Questions -> `program.md#9-implementation-plan` Open Questions

## Planning Rules

When creating or refreshing a plan, stay in read-only planning mode unless the user explicitly asks to execute:

- Read specs, docs, code entry points, tests, configuration, and recent changes.
- Identify existing patterns, ownership boundaries, dependencies, risks, unknowns, and decisions needed.
- Build or update `program.md` from `assets/program.template.md`.
- Ensure the project git ignore rules exclude `tasks/output/` before creating task output artifacts.
- Planning is complete only when implementation can continue from the artifacts without relying on chat memory.

`program.md` must include:

- Concept Refinement, or `None` when the work starts from a clear spec
- problem, goals, final acceptance criteria, constraints, non-goals, and escalation rules
- context/reference index with source, purpose, and freshness
- preferences/tradeoffs, locked constraints, and negotiable space
- decisions, strategy, dependency graph, node status, task list, checkpoints, risks, and open questions
- exploration/hypothesis plan when assumptions need validation
- Loop contract and Loop state when iterative convergence is expected
- current status, active task package, next action, latest evidence, and next checkpoint

Keep `program.md` latest-state only. Historical changes and run logs belong in `memory.md`.

## Preference Layer

Make important preferences explicit before decomposing work:

```text
Preference -> Goal -> Plan -> Task -> Verify -> Memory
```

Use these labels:

- `declarative preference`: desired outcome, implementation open
- `imperative preference`: required path, implementation constrained
- `locked constraint`: must not change without escalation
- `negotiable space`: agent may optimize or propose alternatives

If execution reveals a better tradeoff or a wrong assumption, update `program.md#3-preferences-and-tradeoffs` and record durable learning in `memory.md`.

## Decomposition Rules

### Map Dependencies

Build foundations before dependents. Typical order:

```text
schema/data -> models/types -> service/API contract -> endpoint/client -> UI/workflow -> e2e verification
```

Record dependencies in `program.md` as both a graph/list and a node-status table. If a task package depends on another package or shared contract, name it explicitly.

### Prefer Vertical Slices

Default to vertical slices that deliver one working, testable path. Avoid horizontal plans such as "all schema, then all APIs, then all UI" unless the architecture forces it.

Good: "User can create a task" with data shape, API, UI path, and verification for that flow.

Weak: "Implement backend and frontend" with no single observable result.

### Size Work

| Size | Files | Scope | Rule |
|---|---:|---|---|
| XS | 1 | Single function/config/doc change | Fine as an atomic node |
| S | 1-2 | One component, endpoint, or small behavior | Good task package if independently verifiable |
| M | 3-5 | One vertical feature slice | Ideal upper bound |
| L | 5-8 | Multi-component feature | Split unless tightly coupled |
| XL | 8+ | Too large | Must split |

Use `Small`, `Medium`, and `Large` in task-package contracts; `XS/S/M/L/XL` may be used internally.

Split further when the title contains "and", acceptance criteria exceed three bullets, work crosses independent subsystems, or implementation plus verification is unlikely to fit in one focused session.

### Place Checkpoints

- satisfy dependencies bottom-up
- keep every task package in a working state when completed
- validate high-risk assumptions early
- checkpoint every 2-3 task packages or at risk boundaries
- call out parallel work only after shared contracts are defined

## Task Packages

Start each task package from `assets/task.template.md`.

Each task package must define:

- Task contract: description, acceptance criteria, verification, dependencies, context/preference refs, locked constraints, negotiable space, likely files, and estimated scope
- Output Artifacts: the per-task directory `tasks/output/TASK-NNN-<slug>/`, its current contents, source command, status, and overwrite rule
- Atomic Implementation Plan with status, action, dependency, touched area, verification, evidence, and failure action
- Verification Matrix and Checkpoint
- Current Loop Attempt when needed
- Latest Execution Snapshot
- Escalation, Risks and Rollback
- Standing Checklist
- Pre-completion Red Team
- Completion Writeback to `program.md` and `memory.md`

Work from the task package, not from memory. Execute the smallest useful node, run its verifier, record evidence, then update status and write durable findings as needed.

When a task produces artifacts, write only the latest final version to `tasks/output/TASK-NNN-<slug>/`. Use `memory.md` for historical run summaries and the task package for evidence pointers; do not use `tasks/output/` as a chronological archive.

## Loop Mode

Use Loop mode when work must converge through attempts:

- implementation path is unclear but success criteria are clear
- a high-risk hypothesis needs proof
- verification may fail and should trigger reflection
- the task is repair, optimization, eval, research, migration, or integration work

Every loop needs a finite budget, verifier, reflect trigger, iterate rule, and stop/escalation condition.

```text
GOAL -> PLAN -> ACT -> VERIFY -> PASS
                   |
                   v
                REFLECT -> ITERATE -> PLAN
```

`program.md` owns the project-level Loop contract and latest Loop state. Task packages own the current attempt. Completed attempts are summarized in `memory.md`.

Do not use Loop mode to hide indecision. If the same failure repeats without new information, stop and mark blocked or escalate.

## Memory Discipline

Write to `memory.md` when:

- a task reveals an important implementation fact, invariant, dependency, or system behavior
- a meaningful plan, interface, behavior, dependency, or decision change occurs
- execution, verification, rollout, rollback, or manual acceptance creates a run log
- verification fails in a way future agents should learn from
- a Loop iteration changes the plan because of evidence
- a task package completes, blocks, or is cancelled

Do not write ordinary progress chatter. A memory entry should change future planning or execution.

Promotion rule:

```text
raw evidence/log -> tasks/output/TASK-* latest artifact when it is a deliverable -> memory.md run log or summary -> task/program evidence pointer -> program.md current status if plan-level
```

Treat `memory.md` as an evolving playbook:

- every run-log entry gets a distillation state: `待提炼` or `不需要`
- reflect when a task package closes or pending entries reach 5
- distill useful lessons into K/R/PL/F entries with trigger conditions, scope, counterexamples, and evidence
- revise by delta; do not rewrite the whole memory file
- mark superseded entries `已废弃` with a pointer instead of deleting them

## Status Vocabulary

Use one status vocabulary across `program.md` and task packages:

```text
待开始 / 进行中 / 阻塞 / 待验证 / 待验收 / 完成 / 已取消
```

`探索中` is additionally valid for the program-level overall status.

Rules:

- `完成` only when acceptance criteria pass, evidence is recorded, and required writeback is done.
- `待验收` when implementation and verification evidence are ready but human acceptance is required.
- `阻塞` only when the next action depends on missing information, permission, external state, or a failed prerequisite.
- Atomic nodes use the same statuses and must name the next verification action when incomplete.

## Standing Completion Bar

Before moving a task package to `待验收` or `完成`, complete its Standing Checklist. Every applicable item must be checked; every non-applicable item needs `N/A: <reason>`.

Per task:

- acceptance criteria are met and tied to evidence
- runtime behavior was verified, not only compiled or typechecked
- new behavior is covered by tests that would fail without the change, or a reason is recorded
- existing tests, build/typecheck, lint, and formatting pass or are explicitly scoped out
- relevant edge cases and error paths are handled or recorded as known risk
- changes stay scoped; no unrelated refactors, duplicated business logic, dead code, debug output, or commented-out blocks remain

Per feature or risky change:

- integration points are covered: migrations, config, feature flags, public contracts, and backward compatibility
- public interfaces, APIs, user-facing behavior, and durable architecture decisions are documented when changed
- security implications are reviewed for untrusted input, auth, and data handling
- observability and rollback are defined for new critical paths or risky changes
- human review happens before merge, deploy, or acceptance when required

Do not mark a task package complete because code was written. Completion requires acceptance evidence, completed Standing Checklist, answered Pre-completion Red Team, and writeback.

## Workflow

### Create Or Refresh A Plan

1. Classify input: raw idea, refined idea/spec, existing plan, or active execution.
2. If raw idea, refine it first and write the confirmed brief into `program.md#0-concept-refinement`.
3. Gather context in read-only planning mode.
4. Create/update `program.md`, preferences, dependency graph, risks, checkpoints, and open questions.
5. Decide `Lite` or `Full`, and `Linear` or `Loop`.
6. Create task packages only for nodes ready to execute or needing precise scoping now.
7. Ensure `.gitignore` excludes `/tasks/output/` or `tasks/output/`.
8. Run `scripts/validate_plan.py <project-root>` when possible.

### Continue A Plan

At session start, read in order:

1. `program.md`
2. `memory.md`
3. the active task package listed in `program.md`
4. evidence referenced by that task package
5. relevant code, tests, and recent commits

Then report current status, relevant memory, next node, stale evidence, blockers, decisions needed, and what will be updated if the next step succeeds.

### Execute A Task Package

1. Pick the next actionable atomic node.
2. Execute the smallest useful step.
3. Run the node's verifier.
4. Update status, evidence, and next action.
5. If the task has output artifacts, refresh `tasks/output/TASK-NNN-<slug>/` by overwriting stale files with the latest final state.
6. Write durable findings, changelog entries, run logs, and history deltas to `memory.md`.
7. If package status changes, update the latest status table in `program.md`.

### Audit Or Repair A Plan

Use `references/audit-checklist.md`. Repair by restoring the three-layer authority:

- `program.md`: current entrypoint and latest plan state
- `memory.md`: durable findings, changelog, run logs, and history
- `tasks/TASK-*.md`: active execution state

## Resources

- `assets/program.template.md`: create or restructure `program.md`
- `assets/task.template.md`: create task packages
- `assets/memory.template.md`: create or restructure `memory.md`
- `references/audit-checklist.md`: audit or repair a plan
- `scripts/validate_plan.py <project-root>`: check structure, links, statuses, memory, placeholders, and unresolved markers
- `examples/csv-export/`: minimal filled example that should pass validation
