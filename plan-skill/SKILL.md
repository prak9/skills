---
name: plan-skill
description: 为复杂工程、跨会话协作或高风险执行建立可恢复的持久计划状态，维护目标、约束、节点、证据、阻塞与有限复盘；不用于只需做选择的决策分析，也不为单次简单任务强制创建计划文件。
---

# Plan Skill

Keep the lightest state that lets work resume without chat history and finish with evidence. This skill owns durable execution state, not domain research, upstream decisions or final prose.

## Goal And Acceptance First

Before decomposition or execution, state the observable outcome, scope/bounds and evidence that will decide completion. Resolve ambiguity that would materially change the result or pass/fail judgment; activity and executor self-report are not acceptance evidence.

For plan-only requests or an explicitly retained gate, show the contract and wait before recording `Confirmed`. For an already authorized, unambiguous build/fix request, restate and record it, then proceed without redundant approval. Durable state stays `Contract status: Draft` until resolved; no executable nodes or execution under a Draft contract. Planning alone never authorizes implementation or external effects.

## Choose The Surface

| Surface | Use when | Authority |
|---|---|---|
| Inline | Ordinary single-session execution without a durable-plan need | Conversation/tool plan; create no files and skip `init_plan.py` |
| Lite | A short recoverable plan is useful | One `program.md` owns outcome, constraints, acceptance, nodes, evidence and material reflection |
| Full | Multiple owners, handoff, risk or accumulated state no longer fits one file | `program.md` owns the project contract/index; task packages alone own task status and atomic evidence; `memory.md` holds durable decisions/findings/runs |
| Loop | Full state must converge through repeated experiments/verification | Full plus a finite Loop contract and consequential run records |

Prefer Inline/Lite. Step count or the word “complex” does not justify a larger artifact set. Create tasks just in time and generated outputs only when needed; never hand-maintain a second derivable status view. Code, tests, receipts and runtime outputs are facts; Markdown points to them.

For Lite/Full/Loop, `scripts/init_plan.py <project-root> --title "<title>"` creates a scaffold; add `--profile full` only when justified. Fill applicable fields, not imaginary work. New/upgraded state must pass `scripts/validate_plan.py --strict <project-root>` before it becomes execution authority. Upgrade Lite in place with `scripts/upgrade_plan.py <project-root>`, first using `--dry-run` when inspecting the migration.

## Execution And Recovery

Decompose around observable behavior and uncertainty, not file lists. Prefer the smallest end-to-end slice that yields trustworthy evidence; give it a decisive verifier and a relevant failure/boundary case before execution. For non-code work use a discriminating probe or reviewable artifact rather than forcing runnable code.

Resume from `program.md`, the active task and their referenced evidence. Reconcile changed load-bearing premises and actual effects before using the saved next action; preserve unrelated verified work. A failed attempt must not overwrite the best verified result. A failed verifier changes an assumption, plan or implementation; if the checker passes but reality fails, repair the acceptance sensor rather than trusting the green mark.

Recover why the current route was chosen, its still-supported premises, unresolved questions and next acceptance check—not only node status. Read the smallest linked evidence set that can settle the next action; unchanged source bytes do not validate a finding contradicted by new evidence. Keep domain facts in their existing records and link their decision consequence here rather than copying a second research ledger into the plan.

Update existing records when evidence changes the route. Research discoverable unknowns and choose reversible details within accepted bounds; stop dependent work only when changing a locked outcome, acceptance, authority or real risk requires the user's decision. Do not add a parallel diary or approval process.

Handoff and completion need consistent state, not an automatic cleanup pass or `N/A` marker. Use Clean only when accumulated or conflicting state impairs recovery; preserve existing opted-in metadata. Evidence that still covers unchanged code, inputs and conditions can be reused.

## Conditional References

Read only the branch that changes the current plan:

| Condition | Reference |
|---|---|
| Several plausible goals/routes | `references/concept-refinement.md` |
| Material unknown or deviation | `references/unknowns-contract.md` |
| Solution preferences or method/objective conflict | `references/preference-contract.md` |
| Unresolved readiness decision | `references/pre-execution-grill.md` |
| Loop or unattended repeated execution | `references/foundation-contract.md`, `references/loop-contract.md` |
| Parallel ownership, ports, migration or public workflow change | `references/executable-spec-contract.md` |
| A material event changes reusable learning | `references/reflection-contract.md` |
| Recovery difficulty, duplicate or conflicting state | `references/clean-contract.md` |
| Setting `阻塞`, `待验收` or `完成` | `references/status-and-completion.md` |
| Shared abstraction change | `references/abstraction-quality.md` |
| Auditing/repairing state or changing recovery behavior | `references/audit-checklist.md` |

Opt into `references/evidence-validity.md` only when source-validity snapshots are needed across interruptions; a snapshot is never created by default. Fingerprints detect changes, not behavioral coverage. Recovery changes require the audit reference's isolated interruption probe; ordinary resumes do not.

For an authorized repeated research loop, link existing run/grade/finding/change IDs and raw evidence; use [the flywheel contract](../research-craft/references/research-flywheel.md) only for that case.

## Completion

Before advancing work that depends on a consequential result, write the result and its evidence to the existing authoritative record; a chat report alone is not durable writeback. Lite uses `program.md`; Full/Loop uses `memory.md` for decisions/findings and task packages for node evidence. Read `references/reflection-contract.md` when its material-learning trigger fires. Reuse domain records through links rather than duplicating their contents.

A completed node has acceptance evidence, not merely a report that it ran. Lite/Full Linear record reflection only for material learning; Loop records an evidence-linked reflection per verified attempt. Preserve locked bounds, stable IDs, raw evidence and consequential history; summaries are decision records, not hidden chain-of-thought.

Loop requires a finite budget, bounded scope, independent checker, sensor/granularity alignment, calibration and stop conditions. Keep goal completion, search convergence, budget exhaustion and blockage distinct; don't invent a budget or claim global optimality.

Use `待验收` only for an explicitly retained owner decision after technical evidence passes. A blocker names the missing condition, owner and recovery action. Do not keep completed work open for optional polish or mark an authorized unfinished delivery complete.

Reuse upstream goals, facts, constraints, conclusions and evidence. Boundary and handoff: do not rerun upstream work unless missing or contradictory, and do not invoke all four by default.
