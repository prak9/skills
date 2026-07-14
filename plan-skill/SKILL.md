---
name: plan-skill
description: Use this skill to turn a raw idea, vague project, existing spec, or ongoing implementation into a controlled plan-and-execution loop. It refines ideas into program.md, creates or repairs AI-executable plans, decomposes work into tasks/TASK-*.md packages, keeps latest per-task output snapshots under gitignored tasks/output/TASK-*/ directories, tracks verification and checkpoints, and preserves durable findings in memory.md. Trigger when the user asks to refine an idea, ideate, stress-test a plan, create an implementation plan, break down tasks, run Loop-mode execution, manage project control, clarify preferences/tradeoffs, order dependencies, slice work vertically, define acceptance criteria, track evidence, write run logs/CHANGELOG/history, or hand off coding work across sessions.
---

# Plan Skill

Use this skill to move from idea to verified implementation without losing state. It has three authoritative state documents plus one non-authoritative output area:

```text
program.md                 # Current state: concept brief, plan, status, blockers, next step, links.
memory.md                  # Durable history: findings, lessons, changelog, run logs, summaries.
tasks/TASK-NNN-<slug>.md   # Executable task packages with atomic nodes, verification, and evidence.
tasks/output/TASK-NNN-<slug>/  # Non-authoritative latest output snapshot; gitignored.
```

Do not create `codemap.md` by default. Keep implementation maps inside the relevant task package unless they become large enough to deserve a separate file.

If downstream tooling requires `tasks/plan.md` or `tasks/todo.md`, generate them only from `program.md` and `tasks/TASK-*.md`. They are exports, not sources of truth.

Task output artifacts live under `tasks/output/TASK-NNN-<slug>/`, matching the task package filename without `.md`. This directory records the latest final output state for that task only. If outputs change across attempts, overwrite or replace the previous files so the directory shows the current final state; do not append timestamped versions or chronological history there. Keep `tasks/output/` ignored by git by default.

## Fast Path

Use the lightest control surface that preserves useful state:

1. Skip plan artifacts for a truly one-step, single-session change unless the user asks for a durable plan.
2. Otherwise start with Lite. Choose Full immediately only for Loop mode, more than three task packages, multiple sessions, risky/irreversible work, or handoff-heavy execution.
3. Initialize the linked files instead of copying and repairing placeholders by hand:

   ```bash
   python3 <plan-skill>/scripts/init_plan.py <project-root> --title "<work title>"
   # Add --profile full only when a Full trigger applies.
   ```

4. If a Lite plan later crosses a Full trigger, preview and apply the in-place upgrade instead of rebuilding the files:

   ```bash
   python3 <plan-skill>/scripts/upgrade_plan.py <project-root> --dry-run
   python3 <plan-skill>/scripts/upgrade_plan.py <project-root>
   ```

5. Fill the current task package only. Create later task packages just in time when their dependencies and acceptance criteria are clear.
6. During drafting, run `scripts/validate_plan.py <project-root>` to separate structural errors from expected placeholder warnings. Before execution, handoff, or completion, remove the remaining placeholders and run `--strict`.

## Operating Model

- `program.md` owns the refined concept, current plan, task-package status, blockers, checkpoints, and next action. It must stay current-state only.
- `tasks/TASK-*.md` owns task execution state: atomic nodes, latest attempt, verification, evidence, blockers, rollback, and completion writeback.
- `tasks/output/TASK-*/` owns the latest final task output artifacts, such as generated reports, screenshots, exports, review bundles, or acceptance files. It is not a run log and should not accumulate old versions.
- `memory.md` owns durable knowledge: findings, reusable lessons, changelog entries, run logs, failed attempts, and history summaries.
- Code, tests, logs, screenshots, CI, and runtime output are facts. Markdown records intent, status, decisions, and evidence pointers.
- Chat is not durable. Write decisions that matter into `program.md` or the active task package. Write reusable discoveries into `memory.md`.
- Never silently reconcile drift. Name the conflicting sources, pick the authority, and update it.

## Profiles

Declare exactly one value in `program.md`: `- Profile: Lite` or `- Profile: Full`. Prefer Lite when uncertain; the validator keeps the legacy `Full` default only when the field is absent.

- `Lite`: Default for one or two focused sessions and up to three task packages. `memory.md` is optional until the first durable finding.
- `Full`: Use when any Fast Path Full trigger applies. It adds durable context, preferences, decisions, Loop state, checkpoints, and memory synchronization.
- Semantic rules apply in both profiles: `完成`/`待验收` requires evidence; statuses must agree across files; hypotheses close only with a verdict and evidence.
- Upgrade Lite to Full when a Full trigger appears; do not populate Full-only sections speculatively.

## Stage 0: Concept Refinement

Use this stage only when the input is a raw idea, multiple directions are plausible, target users or success criteria are unclear, or the user asks to ideate or stress-test the concept. Read `references/concept-refinement.md` before running it.

Skip divergent refinement when the user already provides a clear spec, accepted direction, or existing plan. Record `None: <source/reason>` in the brief instead of manufacturing alternatives.

Stage 0 must end with a confirmed one-page brief in `program.md#concept-refinement`, mapped into the problem, goals, strategy, hypotheses, MVP nodes, non-goals, and open questions. Do not create a separate idea document by default.

## Planning Rules

When creating or refreshing a plan, stay in read-only planning mode unless the user explicitly asks to execute:

- Read specs, docs, code entry points, tests, configuration, and recent changes.
- Identify existing patterns, ownership boundaries, dependencies, risks, unknowns, and decisions needed.
- Initialize new artifacts with `scripts/init_plan.py`; use `scripts/upgrade_plan.py` when Lite crosses a Full trigger; use the matching detailed templates directly only when repairing or restructuring an existing plan.
- Ensure the project git ignore rules exclude `tasks/output/` before creating task output artifacts.
- Planning is complete only when implementation can continue from the artifacts without relying on chat memory.

Full `program.md` must include the following. Lite keeps only the matching Lite-template fields until a Full trigger appears:

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

If execution reveals a better tradeoff or a wrong assumption, update `program.md#preferences-and-tradeoffs` and record durable learning in `memory.md`.

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

Create new task packages through `scripts/init_plan.py` or by copying the matching compact starter. Use `assets/task.template.md` only to repair or expand a detailed Full package.

Each Full task package must define the following. Lite uses its smaller contract and adds Full-only sections only after upgrading:

- Task contract: description, acceptance criteria, verification, dependencies, context/preference refs, locked constraints, negotiable space, likely files, and estimated scope
- Output Artifacts: the per-task directory `tasks/output/TASK-NNN-<slug>/`, its current contents, source command, status, and overwrite rule
- Atomic Implementation Plan with status, action, dependency, touched area, verification, evidence, and failure action
- Verification Matrix and Checkpoint; keep planned checks in the atomic plan and add `V-*` rows before `待验收` or `完成`
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

Treat `memory.md` as an evolving playbook. In a compact starter, materialize a named category only when its first evidence-backed entry appears:

- every run-log entry gets a distillation state: `待提炼` or `不需要`
- reflect when a task package closes or pending entries reach 5
- distill useful lessons into K/R/PL/F entries with trigger conditions, scope, counterexamples, and evidence
- revise by delta; do not rewrite the whole memory file
- mark superseded entries `已废弃` with a pointer instead of deleting them

## Status And Completion

Use `待开始 / 进行中 / 阻塞 / 待验证 / 待验收 / 完成 / 已取消` consistently; `探索中` is additionally valid at program level. Never equate written code with completion.

Read `references/status-and-completion.md` before setting `阻塞`, `待验收`, or `完成`, or when auditing status/evidence drift. It defines transition rules, the Standing Checklist contract, red-team requirements, and completion evidence.

## Workflow

### Create Or Refresh A Plan

1. Classify input: raw idea, refined idea/spec, existing plan, or active execution.
2. If raw idea, refine it first and write the confirmed brief into `program.md#concept-refinement`.
3. Gather context in read-only planning mode.
4. Decide `Lite` or `Full`, and `Linear` or `Loop`.
5. For new work, run `scripts/init_plan.py`; for existing work, update the matching artifacts in place.
6. Create task packages only for nodes ready to execute or needing precise scoping now.
7. Ensure `.gitignore` excludes `/tasks/output/` or `tasks/output/`.
8. Run `scripts/validate_plan.py --strict <project-root>` before execution, handoff, or completion.

### Continue A Plan

At session start, read in order:

1. `program.md`
2. `memory.md` when the program points to one
3. the active task package when one is listed
4. evidence referenced by the active task package
5. relevant code, tests, and recent commits

Then report current status, relevant memory, next node, stale evidence, blockers, decisions needed, and what will be updated if the next step succeeds.

### Execute A Task Package

1. Pick the next actionable atomic node.
2. Execute the smallest useful step.
3. Run the node's verifier.
4. Update status, evidence, and next action.
5. If the task has output artifacts, refresh `tasks/output/TASK-NNN-<slug>/` by overwriting stale files with the latest final state.
6. Write durable findings, changelog entries, run logs, and history deltas to `memory.md` when present or when a Lite durable finding requires creating it.
7. If package status changes, update the latest status table in `program.md`.

### Audit Or Repair A Plan

Use `references/audit-checklist.md`. Repair by restoring the three-layer authority:

- `program.md`: current entrypoint and latest plan state
- `memory.md`: durable findings, changelog, run logs, and history
- `tasks/TASK-*.md`: active execution state

## Resources

- `assets/program.template.md`: repair or restructure a detailed Full `program.md`
- `assets/task.template.md`: repair or restructure a detailed Full task package
- `assets/program-full-starter.template.md`, `assets/task-full-starter.template.md`, `assets/memory-starter.template.md`: compact Full initializer assets
- `assets/program-lite.template.md`: create a focused Lite `program.md`
- `assets/task-lite.template.md`: create a focused Lite task package
- `assets/memory.template.md`: create or restructure `memory.md`
- `references/concept-refinement.md`: read only for raw-idea ideation, convergence, and one-page brief mapping
- `references/status-and-completion.md`: read before blocked, acceptance, or completion transitions and related audits
- `references/audit-checklist.md`: audit or repair a plan
- `scripts/init_plan.py <project-root> --title <title> [--profile full]`: safely create a Lite-by-default `program.md`, linked `TASK-001`, git ignore rule, and Full `memory.md` when requested; never overwrite existing plan files
- `scripts/upgrade_plan.py <project-root> [--dry-run]`: validate and safely upgrade Lite to Full while preserving current program, task, and memory content
- `scripts/validate_plan.py --strict <project-root>`: check structure, links, IDs, statuses, state transitions, completion semantics, Loop contracts, Git output rules, memory, Markdown table shape, encoding, placeholders, and unresolved markers; add `--json` for stable status/count/error fields
- `tests/`: standard-library regression tests for valid plans, known false-PASS cases, and Markdown parsing boundaries
- `examples/csv-export/`: filled Full/Linear example and integration fixture
- `examples/lite-change/`: filled Lite/Linear example; both examples must pass strict validation
