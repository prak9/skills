---
name: plan-skill
description: Use this skill to create, refine, audit, or continue an AI-executable project plan with program.md as the current-state source of truth, tasks/TASK-*.md as task packages, and memory.md as durable findings/history memory. Trigger when the user asks for a plan skill, planning-and-task-breakdown, implementation plan, Loop-mode plan, project control plan, preference/tradeoff clarification, declarative vs imperative preferences, locked constraints, negotiable space, task-package decomposition, dependency ordering, vertical slicing, scope estimation, parallelizable work, execution status tracking, acceptance criteria, measurable goals, constraints, hypothesis validation, checkpoints, iterative ACT/VERIFY/REFLECT cycles, important findings, knowledge-base capture, CHANGELOG, run logs, execution-history summaries, or cross-session AI coding handoff.
---

# Plan Skill

Use this skill to turn an ambiguous project or ongoing implementation into a verifiable execution plan. The plan has three layers:

```text
program.md                 # Main entrypoint and current state only: latest plan, node status, blockers, next step, links.
memory.md                  # Durable memory: findings, reusable knowledge, CHANGELOG, run logs, history summaries, lessons, evidence pointers.
tasks/TASK-NNN-<slug>.md   # Active task package: one plan node decomposed into atomic implementation nodes with status and verification.
```

Do not create `codemap.md` by default. If implementation mapping is needed, keep it inside the relevant task package unless it becomes large enough to justify a separate file.

If downstream tooling explicitly expects `tasks/plan.md` or `tasks/todo.md`, generate them only as derived exports from `program.md` and `tasks/TASK-*.md`. They are not authoritative.

## Authority Model

- `program.md` is the main entrypoint for the project plan and the source of truth for the current plan plus the latest status of every task package. It must link to relevant task packages and memory entries, but it must not accumulate CHANGELOG entries, run logs, historical status transitions, or old Loop attempts.
- `memory.md` is the source of truth for durable findings, reusable knowledge, CHANGELOG entries, run-log summaries, historical execution summaries, lessons learned, and evidence pointers that should survive task closure.
- Each `tasks/TASK-*.md` is the source of truth for its own active atomic implementation plan, current attempt state, latest evidence pointer, and verification state.
- Code, tests, logs, and runtime evidence are facts. Markdown records intent, plan, status, and evidence pointers.
- When chat decisions matter beyond the current reply, write them into `program.md` or the active task package before treating them as durable.
- When a discovery matters beyond the current task, write it into `memory.md` before treating it as durable knowledge.
- Never silently reconcile conflicts. Mark drift, name the conflicting sources, and choose the authority to update.

## Core Shape

`program.md` must define:

- the problem being solved and why it matters
- entrypoint links to the active task package, current memory file, latest evidence pointers, and next checkpoint
- the context and references the plan depends on, including specs, code entry points, external docs, evidence, and owners
- preferences and tradeoffs: what is locked, what is negotiable, and which tradeoffs define success
- goals, metrics, and final acceptance criteria
- constraints, non-goals, risk boundaries, and escalation rules
- overall strategy and important decisions
- exploration questions, hypothesis-validation plan, and concrete exploratory implementation plan when validation requires a spike, prototype, script, or experiment
- an implementation plan section with overview, architecture decisions, phased task list, checkpoints, risks, and open questions
- a plan dependency graph and node-status table where each node maps to one task package
- a Loop contract and Loop state table when execution should iterate through `ACT -> VERIFY -> REFLECT -> ITERATE`
- current plan status, active node, and next checkpoint
- only the latest state. Historical changes, run logs, previous Loop attempts, and old status transitions belong in `memory.md`

`memory.md` must define:

- important findings and knowledge items with evidence pointers
- reusable implementation, testing, product, or operational lessons
- preference learning: what execution revealed about preferences, tradeoffs, locked constraints, or negotiable space
- CHANGELOG entries for meaningful plan, implementation, interface, or decision changes
- run-log summaries for execution, verification, rollout, rollback, and manual acceptance events
- historical execution summaries by task package or milestone
- failed attempts worth preserving and why they failed
- open knowledge gaps that need future validation
- a reflection-and-curation pass that periodically distills run logs into reusable entries

Context and references are not memory. `program.md` stores the current context index and reference pointers needed to understand the plan; `memory.md` stores distilled findings and historical learning extracted from execution.

## Preference Layer

Before decomposing work, make preferences explicit:

```text
Preference -> Goal -> Plan -> Task -> Verify -> Memory
```

Use English labels because they are shorter and less ambiguous:

- `declarative preference`: desired outcome, implementation open.
- `imperative preference`: required path, implementation constrained.
- `locked constraint`: must not be changed without escalation.
- `negotiable space`: the agent may optimize or propose alternatives.

For important plans, ask what hidden assumptions would materially change implementation. Put the answers in `program.md#Preferences & Tradeoffs`. If execution reveals a better tradeoff or a wrong assumption, record the learning in `memory.md`.

Each task package must define:

- a `Task N` contract with description, acceptance criteria, verification, dependencies, likely files touched, and estimated scope
- atomic implementation nodes with clear status
- exact verification method for each node
- current Loop attempt state when attempts need verify-reflect-iterate cycles
- latest evidence pointers for completed or failed checks
- blockers, decisions, and rollback notes
- memory writeback requirements for findings, CHANGELOG entries, run logs, and execution summaries
- preference references, locked constraints, and negotiable space when tradeoffs matter
- required `program.md` status updates when the package moves state

## Planning Discipline

When the user asks for planning or task breakdown, enter read-only planning mode:

- Read specs, existing docs, code entry points, tests, configuration, and recent changes.
- Identify existing patterns, ownership boundaries, and dependency chains.
- Note risks, unknowns, and decisions needed.
- Do not write implementation code during planning. Only create or update planning artifacts unless the user explicitly asks to execute.

Planning is complete only when the plan can drive implementation without relying on chat memory.

## Context And References

Maintain a `program.md` section for context and refs before detailed goals:

- product/spec context: PRDs, tickets, user requests, screenshots, designs
- code context: entry points, modules, tests, configs, migrations, scripts
- external references: docs, APIs, standards, upstream issues, papers
- evidence refs: logs, benchmarks, prior reports, screenshots, CI runs
- ownership refs: decision owner, reviewer, domain expert, escalation contact

Every ref should include a location, why it matters, and freshness/status. Do not paste large source material into `program.md`; link or point to it. If a ref produces a reusable finding, promote the distilled finding to `memory.md`.

## Loop Mode

Use Loop mode when a plan is expected to converge through repeated attempts, not one pass:

- unclear implementation path but clear success criteria
- high-risk hypothesis needs proof before full buildout
- verification may fail and should produce structured reflection
- model/agent work must preserve failed attempts as learning
- task package is a repair, optimization, eval, research, migration, or integration effort

Loop mode is:

```text
GOAL -> PLAN -> ACT -> VERIFY -> PASS
                   |
                   v
                REFLECT -> ITERATE -> PLAN
```

`program.md` owns the project-level Loop contract:

- loop objective
- success criteria
- failure signals
- iteration budget
- reflect trigger
- stop/escalation condition
- current Loop state and next action
- what findings or failed attempts must be promoted to `memory.md`

Task packages own the current attempt state:

- what was tried
- what verification said
- why it failed or passed
- what changed in the next plan
- whether the package should continue, split, block, or escalate
- which lessons, CHANGELOG entries, run logs, or execution summaries were written to `memory.md`

Completed Loop attempts should be summarized in `memory.md`; keep only the latest active attempt in `program.md` and the task package.

Do not use Loop mode to hide indecision. Every loop must have a finite budget and a verifier. If the same failure repeats without new information, stop and mark blocked or escalate.

## Memory Discipline

Use `memory.md` to preserve knowledge that should outlive one task package. Keep it concise and evidence-backed.

Write to `memory.md` when:

- a task reveals an important implementation fact, invariant, hidden dependency, or system behavior
- a meaningful plan, interface, behavior, dependency, or decision change would otherwise become a CHANGELOG entry
- an execution, verification, rollout, rollback, or manual acceptance event would otherwise become a run log
- verification fails in a way that teaches a reusable lesson
- a loop iteration changes the plan because of evidence
- a task package completes, blocks, or is cancelled and future agents need the history
- a decision's evidence is longer-lived than the decision record in `program.md`

Do not write ordinary progress chatter. A memory entry should change future planning or execution.
Do not append CHANGELOG, run-log, or historical status sections to `program.md`; update its latest state in place and link to the relevant memory IDs when needed.

Use this promotion rule:

```text
raw evidence/log -> memory.md run log or summary -> task/program latest evidence pointer -> program.md current status if plan-level
```

`memory.md` is not a replacement for evidence. It stores the distilled claim plus the pointer to the evidence.

### Reflection & Curation

Treat `memory.md` as an evolving playbook (ACE-style), never a rewrite target:

- Execution writes traces: every run-log entry gets a `提炼` state — `待提炼` or `不需要`.
- Reflect when a task package closes or pending entries reach 5: extract lessons from successes and failures into K/R/PL/F entries, then mark the source RUN entries with the produced IDs.
- Curate by delta only: add or revise individual ID'd entries; never rewrite the whole file. Merge duplicates by keeping the surviving ID and marking the other `已废弃` with a pointer.
- Against brevity bias: a distilled entry must keep concrete trigger conditions, applicable scope, counterexamples, and an evidence pointer. A lesson with no applicable scenario does not enter the playbook.
- Against context collapse: compaction may only turn already-distilled RUN spans into one H summary; superseded entries are marked `已废弃`, not deleted.

## Breakdown Algorithm

### 1. Map Dependencies

Build foundations before dependents. Typical chains look like:

```text
schema/data -> models/types -> service/API contract -> endpoint/client -> UI/workflow -> e2e verification
```

Record dependency order in `program.md` as both:

- a graph/list that shows node dependencies
- a node-status table that tracks status, task-package link, phase, dependency, verification, and evidence

If a task package depends on another package or shared contract, name it explicitly.

### 2. Prefer Vertical Slices

Default to vertical slices that deliver one working, testable path. Avoid horizontal plans such as "build all schema, then all APIs, then all UI" unless the architecture forces it.

Good task package: "User can create a task" with data shape, API, UI path, and verification for that single flow.

Weak task package: "Implement backend and frontend" with no single user-visible result.

### 3. Size Tasks

Use this sizing guide:

| Size | Files | Scope | Rule |
|---|---:|---|---|
| XS | 1 | Single function/config/doc change | Fine as an atomic node |
| S | 1-2 | One component, endpoint, or small behavior | Good task package if independently verifiable |
| M | 3-5 | One vertical feature slice | Ideal upper bound |
| L | 5-8 | Multi-component feature | Split unless tightly coupled |
| XL | 8+ | Too large | Must split |

Use `Small`, `Medium`, and `Large` in task-package contracts; `XS/S/M/L/XL` may be used internally for finer sizing.

Split further when the title contains "and", acceptance criteria exceed three bullets, the work crosses independent subsystems, or one focused session is unlikely to finish implementation plus verification.

### 4. Order Checkpoints

Arrange task packages so:

- dependencies are satisfied bottom-up
- every task package leaves the system in a working state
- high-risk or assumption-validating work happens early
- checkpoints appear after every 2-3 task packages or at risk boundaries
- parallelizable work is called out only after shared contracts are defined

## Status Vocabulary

Use one vocabulary across `program.md` and task packages:

```text
待开始 / 进行中 / 阻塞 / 待验证 / 待验收 / 完成 / 已取消
```

Rules:

- A task package is `完成` only when its task package acceptance criteria pass and `program.md` has been updated.
- A task package is `待验收` when implementation and verification evidence are ready but human acceptance is required.
- A task package is `阻塞` only when the next action depends on missing information, permission, external state, or a failed prerequisite.
- Atomic nodes use the same statuses and must name the next verification action when not complete.

## Workflow

### 1. Create Or Refresh The Plan

1. Enter read-only planning mode and gather context.
2. Build or update the `program.md` context/ref index.
3. Define preferences and tradeoffs: locked constraints, negotiable space, declarative preferences, imperative preferences.
4. Restate the problem, desired outcome, constraints, and unknowns in one concise checkpoint before large edits if the goal is ambiguous.
5. Map dependency order and identify high-risk assumptions.
6. For high-risk assumptions, write a concrete exploratory implementation plan in the exploration section before committing to full task packages.
7. Split into vertical task packages where each plan node has a verifiable result.
8. Write the implementation plan in `program.md`: entrypoint links, overview, architecture decisions, dependency graph, node-status table, phased task list, checkpoints, risks, and open questions. Keep it to latest state only.
9. Decide whether the plan is `Linear` or `Loop`. If Loop, define budget, verifier, reflect trigger, and stop condition.
10. Create or update `program.md` from `assets/program.template.md`.
11. Create task files from `assets/task.template.md` only for task packages that are ready to execute or need precise scoping now.
12. Run `scripts/validate_plan.py <project-root>` when possible.

### 2. Continue A Plan

At session start, read in order:

1. `program.md`
2. `memory.md`
3. the active task package listed in `program.md`
4. evidence referenced by that task package
5. relevant code, tests, and recent commits

Then report from the `program.md` entrypoint:

- current plan status and active task package
- relevant memory findings and whether any appear stale
- next atomic node to execute
- stale or missing evidence
- blockers and decisions needed
- what will be updated if the next step succeeds

### 3. Execute A Task Package

Work from the task package, not from memory.

1. Pick the next atomic node with status `待开始`, `进行中`, or `阻塞` after unblocking.
2. Execute the smallest useful implementation step.
3. Run the node's verification method.
4. Update the node status, latest evidence pointer, and next action.
5. Write CHANGELOG entries, run-log summaries, durable findings, and execution-history deltas to `memory.md`.
6. If the task package status changes, update only the latest task-package status table in `program.md`.

Do not mark a task package complete because code was written. Mark it complete only when verification evidence satisfies its acceptance criteria and the task package's Pre-completion Red Team questions are answered.

### 4. Audit Or Repair A Plan

Check for these failures:

- `program.md` lacks measurable goals, final acceptance criteria, or task-package status.
- `program.md` lacks preferences/tradeoffs for a non-trivial plan, or fails to mark locked constraints and negotiable space.
- `program.md` contains CHANGELOG, run-log, historical status, or old Loop-attempt sections instead of only latest state.
- context and references are missing, stale, or lack source/freshness information.
- dependency graph, node-status table, checkpoints, or parallelization assumptions are missing.
- Loop mode is enabled but no finite loop budget, verifier, reflect trigger, or stop condition exists.
- `memory.md` is missing, stale, or lacks findings, CHANGELOG entries, run logs, or history summaries for completed or failed task packages.
- run logs pile up as `待提炼` with no reflection pass turning them into K/R/PL/F entries.
- implementation plan lacks overview, architecture decisions, phased task list, risks, or open questions.
- Implementation work exists but no task package records its verification method or evidence.
- Task packages contain broad backlog lists instead of atomic executable nodes.
- task packages are horizontal layers instead of verifiable vertical slices.
- task package size is L/XL without a reason.
- Status fields are stale or disagree between `program.md` and task files.
- Exploration questions have no validation method or stop condition.
- A hypothesis or exploration entry was closed by producing an artifact instead of a verdict (`支持 / 推翻 / 不确定`) with evidence.
- Exploration implementation exists without atomic steps, verification, evidence pointer, or promotion rule to task package / memory.
- Task packages make tradeoff-sensitive changes without preference refs or escalation rules for locked constraints.
- Decisions are hidden in chat, commit messages, or code comments instead of `program.md`.
- "完成" means code landed rather than acceptance evidence passed.
- A task package reached `待验收` or `完成` without answered Pre-completion Red Team questions.

Repair by restoring the three-layer authority: entrypoint and latest plan state in `program.md`; durable findings, CHANGELOG, run logs, and history in `memory.md`; active task execution state in `tasks/TASK-*.md`.

## Task Package Sizing

A task package should be:

- large enough to let the AI autonomously design, implement, test, and fix within a bounded area
- small enough that failure can be localized, retried, or rolled back
- tied to one observable plan node in `program.md`
- closed by evidence, not by effort

Split a package when two parts can be accepted independently, have different blockers, touch unrelated risk areas, or require different human decisions.

## Atomic Node Rules

Every atomic node inside a task package must include:

- status
- concrete implementation action
- dependency on earlier node, or `无`
- expected touched area
- verification method or command
- evidence location once run
- next action if verification fails

Avoid vague nodes such as "improve UI", "clean up backend", or "write tests". Rewrite them as observable actions with checks.

## Task Package Contract

Start each task package with this contract shape:

```markdown
## Task [N]: [Short descriptive title]

**Description:** One paragraph explaining what this task accomplishes.

**Acceptance criteria:**
- [ ] [Specific, testable condition]

**Verification:**
- [ ] Tests pass: `<command>`
- [ ] Build succeeds: `<command>`
- [ ] Manual check: <scenario>

**Dependencies:** [Task numbers or NODE IDs, or "None"]

**Context/Refs:** [CTX/REF/OWN IDs from `program.md`, or "None"]

**Preference refs:** [PREF IDs from `program.md`, or "None"]

**Locked constraints:** [what must not change without escalation, or "None"]

**Negotiable space:** [what the agent may optimize or propose alternatives for, or "None"]

**Files likely touched:**
- `<path>`

**Estimated scope:** [Small: 1-2 files | Medium: 3-5 files | Large: 5+ files]
```

Then add the atomic implementation plan, verification matrix, checkpoint, current Loop attempt, latest execution snapshot, escalation, rollback, pre-completion red team, and completion writeback sections.

For Loop mode, update only the current Loop attempt in the task package. Move completed attempt summaries to `memory.md#运行日志`.

## Updating Rules

- Update `program.md` whenever a task package is created, blocked, ready for acceptance, completed, or cancelled; overwrite latest state instead of appending history.
- Update `memory.md` whenever a durable finding appears, a CHANGELOG-worthy change happens, a run-log event occurs, a loop teaches a reusable lesson, or a task package completes/blocks/cancels.
- Update the task package whenever an atomic node starts, finishes, fails verification, or changes scope; keep only latest execution state and point to memory IDs for history.
- Record evidence as concise pointers to tests, logs, screenshots, commits, reports, or manual acceptance notes.
- Use ISO dates: `YYYY-MM-DD`.
- Mark uncertainty explicitly with `[待确认]`, `[待验证]`, or `[待决策]`; include the next validation or decision step. Markers are legitimate on active work, but a node or row marked `完成` must not carry them.

## Resources

- Use `assets/program.template.md` when creating or restructuring `program.md`.
- Use `assets/memory.template.md` when creating or restructuring `memory.md`.
- Use `assets/task.template.md` when creating a task package.
- Use `scripts/validate_plan.py <project-root>` to check required sections, task links, status consistency, memory structure, placeholders, and unresolved markers.

## Source

Absorbs the planning-and-task-breakdown method: read-only planning first, dependency graph, vertical slicing, task sizing, checkpoints, parallelization notes, and per-task acceptance plus verification.
