# Program: <Project Name>

> Current-state source of truth for the work. Keep only the concept brief, context, goals, constraints, strategy, decisions, hypotheses, implementation plan, task-package status, blockers, and next action here.
> Task execution state lives in `tasks/TASK-*.md`.
> Latest final task outputs live in `tasks/output/TASK-*/` and are ignored by git by default.
> Durable findings, changelog entries, run logs, lessons, and history summaries live in `memory.md`.

- Overall status: `待开始 / 探索中 / 进行中 / 阻塞 / 待验收 / 完成 / 已取消`
- Profile: `Full / Lite`
- Plan mode: `Linear / Loop`
- Loop state: `Goal / Plan / Act / Verify / Reflect / Iterate / Pass / Blocked / Not applicable`
- Loop iteration: `0/<max iterations or Not applicable>`
- Memory: `memory.md`
- Active task package: `tasks/TASK-NNN-<slug>.md / None`
- Task output root: `tasks/output/` (gitignored)
- Active plan node: `NODE-NNN / None`
- Next plan node: `NODE-NNN / Decision point / None`
- Latest evidence: `<V-NNN, RUN-NNN, CHG-NNN, commit, CI run, or report>`
- Next checkpoint: `CP-NNN / None`
- Owner / TL: `<name or role>`
- Last updated: `YYYY-MM-DD`

## 0. Concept Refinement

Refine raw ideas into sharp, actionable concepts worth building through structured divergent and convergent thinking.

### How It Works

- Understand & Expand (Divergent): Restate the idea, ask sharpening questions, and generate variations.
- Evaluate & Converge: Cluster ideas, stress-test them, and surface hidden assumptions.
- Sharpen & Ship: Produce a concrete markdown one-pager moving work forward.

### One-Page Brief

If the work starts from an already-clear spec, write `None` in fields that do not apply and explain the source. Do not keep brainstorming history here; keep only the current confirmed direction.

| Field | Content |
|---|---|
| Raw idea / Source | <user request, issue, spec, screenshot, codebase context, or None> |
| Problem statement | <one-sentence "How might we..." framing> |
| Target user | <specific user, role, team, operator, buyer, or system actor> |
| Success criteria | <observable success conditions> |
| Recommended direction | <chosen direction and why it wins> |
| Key assumptions to validate | <assumption + fast validation method> |
| MVP scope | <smallest version that tests the core assumption> |
| Not doing | <clear exclusions and why> |
| Open questions | <questions that must be answered before or during planning> |

## 1. Problem Definition

### Background

<Current situation, trigger, users, or affected systems.>

### Problem To Solve

<Define the problem, not just the solution.>

### Why Now

<Risk, opportunity, cost, dependency, or timing.>

### Non-goals

- <Explicitly out of scope for this round>

## 2. Context And References

Keep only summaries and pointers needed to understand or execute the current plan. Durable findings, historical changes, and run logs belong in `memory.md`.

### Key Context

| ID | Type | Summary | Location / Ref | Why it matters | Freshness |
|---|---|---|---|---|---|
| CTX-001 | `spec / code / test / design / data / ops / external / evidence` | <summary> | <path, URL, issue, commit, log, or person> | <affected goal or task package> | `current / needs validation / possibly stale` |

### Code And Runtime Entrypoints

| ID | Entrypoint | Path / Command | Related node | Notes |
|---|---|---|---|---|
| REF-001 | <module, test, script, config, or service> | `<path or command>` | `NODE-NNN` | <how to use it or what to watch> |

### External References And Evidence

| ID | Source | Ref | Use | Checked date |
|---|---|---|---|---|
| REF-EXT-001 | <docs, API, standard, report, screenshot, CI, log> | <URL, path, or record> | <which judgment or acceptance criterion it supports> | `YYYY-MM-DD` |

### People And Decisions

| ID | Role / Person | Scope | When to involve | Contact or record |
|---|---|---|---|---|
| OWN-001 | <Owner, Reviewer, Domain Expert> | <scope> | <decision point or risk> | <record location> |

## 3. Preferences And Tradeoffs

Use this layer to define what matters before decomposing work.

```text
Preference -> Goal -> Plan -> Task -> Verify -> Memory
```

### Preferences

| ID | Preference | Type | Strength | Scope | Rationale |
|---|---|---|---|---|---|
| PREF-001 | <what matters> | `declarative / imperative` | `locked / strong / negotiable` | `strategic / tactical` | <why this matters> |

### Tradeoffs

| Decision | Option A | Option B | Tradeoff | Choice | Negotiable? |
|---|---|---|---|---|---|
| <decision point> | <A> | <B> | <cost / benefit> | <current choice> | `yes / no` |

### Locked Constraints And Negotiable Space

| Area | Locked constraints | Negotiable space | Escalation rule |
|---|---|---|---|
| <critical area> | <must not change without approval> | <agent may optimize or propose alternatives> | <when to ask before changing> |

## 4. Goals And Metrics

### Goals

| ID | Goal | Success metric | Baseline | Target | Data source / observation |
|---|---|---|---:|---:|---|
| G-001 | <goal> | <metric> | <value> | <value> | <source> |

### Acceptance Criteria

| ID | Acceptance criterion | Verification method | Pass condition | Owner |
|---|---|---|---|---|
| A-001 | <end-to-end observable result> | <test, demo, log, manual acceptance> | <clear condition> | <role> |

## 5. Constraints

### Hard Constraints

| ID | Constraint | Scope | Verification / monitoring |
|---|---|---|---|
| C-001 | <security, data, compatibility, latency, compliance> | <scope> | <method> |

### Risk Boundaries And Escalation

| Situation | Rule |
|---|---|
| Reversible, local, does not change external contracts | AI may proceed and record evidence |
| Cross-module, unvalidated key assumption, or long-term commitment | Show at task-package checkpoint |
| Could violate a hard constraint, cause irreversible loss, or change goals/acceptance criteria | Stop and ask first |

## 6. Strategy

### Strategy Summary

<Briefly explain the solution, ordering, and main tradeoffs.>

### Dependency And Slicing Strategy

```text
<foundation> -> <intermediate capability> -> <user/system-observable result>
```

- Slice type: `vertical / horizontal / mixed`
- Why this slice: <reason>
- Early high-risk item: <risk or assumption to validate first>

### Execution Principles

- <principle, such as validate the riskiest assumption first>
- <principle, such as every task package needs independent acceptance evidence>
- <principle, such as checkpoint every 2-3 task packages>

## 7. Decisions

Record only decisions that affect later task packages. Put ordinary implementation details in the relevant task package.

| ID | Status | Decision | Reason / Evidence | Impact | Date |
|---|---|---|---|---|---|
| D-001 | `proposed / approved / replaced / deprecated` | <decision> | <evidence or tradeoff> | <impact> | `YYYY-MM-DD` |

## 8. Exploration And Hypothesis Validation

Use this section for spikes, prototypes, scripts, data checks, or technical feasibility validation. Exploration must be minimal and serve only to validate a hypothesis. If the result becomes delivery scope, promote it into Section 9 and a task package.

| ID | Status | Hypothesis / Unknown | Validation method | Deadline task | Pass / fail action |
|---|---|---|---|---|---|
| H-001 | `[待验证]` | <hypothesis or unknown> | <experiment, code read, prototype, user confirmation> | `TASK-NNN` | <action> |

### Exploration Plan

| ID | Hypothesis | Status | Action | Touched area | Verification | Evidence | Pass action | Fail action |
|---|---|---|---|---|---|---|---|---|
| EXP-001 | `H-001` | `待开始 / 进行中 / 待验证 / 完成 / 阻塞` | <minimal spike/prototype/script/experiment> | <files, modules, data, command, or external system> | <command, metric, manual check, or observation> | <RUN-NNN, report, log, screenshot, or commit> | <promote to NODE/TASK, update decision, or close hypothesis> | <retry, drop, split, escalate, or revise hypothesis> |

Rules:

- Keep exploration minimal. It does not carry formal delivery scope.
- Write exploration run logs, failures, changes, and summaries to `memory.md`.
- When an exploration conclusion changes implementation, update Decisions, Implementation Plan, and the related task package.
- Close hypotheses only with a verdict: `supported / disproven / uncertain` plus evidence. Producing an artifact is not the same as closing a hypothesis.

## 9. Implementation Plan

Every plan node must map to one task package. Each task package then breaks into atomic implementation nodes. This section tracks the dependency graph, node status, phased task list, checkpoints, risks, and open questions.

### Overview

<Describe what this round builds, why it is staged this way, and how final acceptance works.>

### Architecture Decisions

- <key decision and reason>
- <key decision and reason>

### Plan Dependency Graph

```text
NODE-001 Foundation (<status>)
  -> NODE-002 Core slice (<status>)
      -> NODE-003 Polish / hardening (<status>)
```

### Node Status

| Node | Phase | Status | Size | Task package | Output snapshot | Goal | Dependencies | Acceptance / Verification | Evidence | Updated |
|---|---|---|---|---|---|---|---|---|---|---|
| NODE-001 | Phase 1: Foundation | `待开始` | `Small / Medium` | `tasks/TASK-001-short-slug.md` | `tasks/output/TASK-001-short-slug/` | <observable result> | `None` | <A-NNN, V-NNN, or command> | <evidence location> | `YYYY-MM-DD` |

### Loop Contract

Use this for plans that need iterative convergence. For linear plans, keep this section and write `Not applicable`. Keep only the latest loop state here; historical attempts go to `memory.md#4-run-logs`.

```text
GOAL -> PLAN -> ACT -> VERIFY -> PASS
                   |
                   v
                REFLECT -> ITERATE -> PLAN
```

| Field | Content |
|---|---|
| Loop goal | <what this loop must converge to, or Not applicable> |
| Success criteria | <verifiable PASS condition> |
| Failure signal | <what result triggers Reflect> |
| Verifier | <test, build, manual scenario, metric, or review> |
| Max iterations | `<number, or Not applicable>` |
| Reflect trigger | <verification failure, risk increase, scope drift, insufficient evidence> |
| Iterate rule | <what may change each round and what may not> |
| Stop / escalation condition | <budget exhausted, repeated failure, hard constraint touched> |
| Memory write rule | <which changes, runs, findings, failures, and summaries must be written to memory.md> |

### Loop State

| Iteration | Node | Step | Current hypothesis / plan delta | Verification | Latest result | Decision | Next |
|---|---|---|---|---|---|---|---|
| L-001 | `NODE-001` | `Plan / Act / Verify / Reflect / Iterate / Pass` | <delta> | <command or acceptance check> | `待验证 / passed / failed / blocked` | <continue, revise, split, escalate> | <next step> |

### Memory Sync

| Type | Status | Source | memory.md location | Updated |
|---|---|---|---|---|
| Finding | `pending / written / not applicable` | <TASK-NNN, evidence, or loop iteration> | `memory.md#1-important-findings` | `YYYY-MM-DD` |
| Changelog | `pending / written / not applicable` | <TASK-NNN, commit, or decision> | `memory.md#3-changelog` | `YYYY-MM-DD` |
| Run log | `pending / written / not applicable` | <TASK-NNN, command, verification, or loop iteration> | `memory.md#4-run-logs` | `YYYY-MM-DD` |
| History summary | `pending / written / not applicable` | <TASK-NNN or Checkpoint> | `memory.md#5-history-summaries` | `YYYY-MM-DD` |

### Task List

#### Phase 1: Foundation

- [ ] NODE-001 / `tasks/TASK-001-short-slug.md`: <foundation or highest-risk hypothesis validation>
- [ ] NODE-002 / `tasks/TASK-002-short-slug.md`: <next foundation node>

#### Checkpoint: Foundation

- [ ] Tests pass and build is clean.
- [ ] Foundation assumptions are validated or explicitly escalated.

#### Phase 2: Core Features

- [ ] NODE-003 / `tasks/TASK-003-short-slug.md`: <core vertical slice>
- [ ] NODE-004 / `tasks/TASK-004-short-slug.md`: <core vertical slice>

#### Checkpoint: Core Features

- [ ] End-to-end core flow works.
- [ ] Node status table and task-package evidence are current.

#### Phase 3: Polish

- [ ] NODE-005 / `tasks/TASK-005-short-slug.md`: <hardening, documentation, or release work>

#### Checkpoint: Complete

- [ ] All acceptance criteria are met.
- [ ] All completed nodes have evidence.
- [ ] Ready for human review or release.

### Checkpoints

| Checkpoint | Position | Verification requirements | Human review |
|---|---|---|---|
| CP-001 | <after NODE-001 or NODE-001~003> | <tests, build, end-to-end flow, or manual acceptance> | `yes / no` |

### Parallelization Opportunities

| Work | Parallelizable? | Prerequisite | Coordination |
|---|---|---|---|
| <node, task package, test, or doc work> | `yes / no / needs confirmation` | <shared contract or dependency> | <file, interface, owner, or checkpoint> |

### Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| <risk> | `High / Medium / Low` | <mitigation> |

### Open Questions

- `[待决策]` <question, options, and recommended default>

## 10. Current Status

Keep only the latest state here. Status changes, changelog entries, and run logs belong in `memory.md`.

- Current blocker: <None, or blocker, owner, and unblock condition>
- Current risk: <None, or risk and control>
- Next step: <next plan node, task package, or atomic node>
- Next human decision: <None, or decision point>
- Pending memory write: <None, or source for changelog/run log/finding/history summary>

## 11. Update Protocol

- When an idea is refined or materially changed, update Section 0 and the context/ref index.
- When a plan node or task package is created, blocked, ready for acceptance, completed, or cancelled, update Plan Dependency Graph, Node Status, and Task List.
- When a task produces final artifacts, update its Output snapshot pointer and keep only the latest final state in `tasks/output/TASK-NNN-<slug>/`.
- In Loop mode, update the current Loop State after every ACT/VERIFY/REFLECT/ITERATE. After PASS, update Node Status. Historical loop attempts go to `memory.md#4-run-logs`.
- When new context, code entrypoints, evidence, or external references are found, update Section 2.
- When preferences, tradeoffs, locked constraints, or negotiable space change, update Section 3. Preference learning from execution goes to `memory.md#8-preference-learning`.
- When a changelog-worthy change, run log, important finding, failed lesson, reusable knowledge, or task-package history summary appears, update `memory.md` and Memory Sync.
- When goals, metrics, acceptance criteria, hard constraints, or strategy change, update Sections 4-7.
- When hypothesis validation or exploration completes, update Section 8 and reflect the impact in Decisions, Implementation Plan, and related task packages.
- Atomic node state lives only in `tasks/TASK-*.md`; this file records plan-node and task-package status.
- Do not add CHANGELOG, run logs, historical status transitions, or completed Loop attempts to this file.
- A `完成` row must have an evidence location; never mark work done because it was merely implemented.
- Keep `tasks/output/` gitignored by default. Do not rely on committed generated artifacts unless the user explicitly asks for that.
- If downstream tooling requires `tasks/plan.md` or `tasks/todo.md`, generate them only from this file and task packages. They are not authoritative.
