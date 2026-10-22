---
name: plan-skill
description: 为复杂工程、跨会话协作或高风险执行建立可恢复的持久计划状态，维护目标、约束、节点、证据、阻塞与有限复盘；不用于只需做选择的决策分析，也不为单次简单任务强制创建计划文件。
---

# Plan Skill

Create the lightest durable control surface that lets work resume without chat history and finish with evidence.

## Choose The Surface

| Surface | Use when | State |
|---|---|---|
| Inline | Direct, single-session work with no durable-plan request | Conversation/tool plan only; create no files |
| Lite | Directly verifiable work that benefits from a short durable plan | One `program.md`; it owns outcome, constraints, acceptance, nodes, status, and evidence |
| Full | Multiple sessions, handoff, risky work, or independently owned task packages | `program.md` indexes work; each `tasks/TASK-*.md` owns its task status and execution evidence |
| Loop | A Full plan must converge through experiments or repeated verification | Full state plus a finite Loop contract and consequential runs in `memory.md` |

Prefer the lighter surface when uncertain. Upgrade Lite in place when its state no longer fits one file.

## Authority

- In Lite, `program.md` is the only plan artifact and owns its `Reflection Log`.
- In Full, `program.md` owns project outcome, constraints, acceptance, task index, checkpoints, blockers, and next action. A task package is the only source of its task status and atomic execution state.
- `memory.md` is optional in Lite and required in Full. It stores only durable decisions, findings, consequential runs, and material reflections.
- Code, tests, CI, logs, and runtime output are facts. Markdown points to evidence; it does not replace it.
- Generated deliverables may use `tasks/output/TASK-NNN-<slug>/` only when a task produces such artifacts. Never create a second hand-maintained view derivable from authoritative state.

For an authorized repeated research loop, link existing case/run/grade/finding/change IDs and raw evidence instead of copying scores into the plan. Use [research-craft's flywheel contract](../research-craft/references/research-flywheel.md) only for that case.

## Create Or Refresh

A durable plan is ready when another agent can recover the observable outcome, current state, inherited constraints, acceptance evidence, material assumptions or unknowns, and next useful action without chat history. Choose the lightest surface that can hold that information. Inline work continues directly without plan files and should skip `init_plan.py`.

For Lite, Full, or Loop, use the bundled initializer when it is the shortest reliable way to create conforming state:

```bash
python3 <plan-skill>/scripts/init_plan.py <project-root> --title "<work title>"
# Use --profile full only when Full/Loop is already justified.
```

The template is an implementation aid, not an additional planning objective. Fill applicable fields from evidence and omit or mark genuinely inapplicable material rather than inventing it. New or upgraded durable state should pass `scripts/validate_plan.py --strict <project-root>` before it becomes the authority for continued execution or handoff.

For implementation work, turn problem decomposition, rapid implementation, and strict verification into one feedback discipline:

- Decompose by observable behavior, material uncertainty, and independently verifiable outcomes—not by file lists or architecture layers. Prefer the smallest end-to-end slice that proves a useful path; split further when dependencies or the verifier cannot localize failure.
- Optimize implementation speed for time to trustworthy evidence. Reuse established patterns and build the minimum runnable path, but never buy speed by weakening the accepted contract, hiding failure modes, or postponing the only meaningful check.
- Give each node a decisive verifier before execution. Cover the success path and the boundary or failure path most capable of disproving the claim, in proportion to risk. Let the result determine whether to expand, revise, or stop.

For research, operations, or non-code work, use the same logic with the cheapest decisive probe, rehearsal, comparison, or reviewable artifact instead of forcing a runnable-code slice.

Load only a branch that changes the plan:

- several plausible directions: `references/concept-refinement.md`;
- unfamiliar territory or hidden constraints: `references/unknowns-contract.md`;
- material solution preferences or method/objective conflict: `references/preference-contract.md`;
- unresolved readiness judgment: `references/pre-execution-grill.md`;
- Loop, unattended repetition, or explicit verification/recovery controls: `references/foundation-contract.md` and `references/loop-contract.md`;
- parallel work, ports, migrations, reference preservation or public workflow changes: `references/executable-spec-contract.md`.

Opt into `references/evidence-validity.md` only when old evidence validity must survive interruption or handoff; its snapshot is never created by default.

For a Lite plan that grows into Full:

```bash
python3 <plan-skill>/scripts/upgrade_plan.py <project-root> --dry-run
python3 <plan-skill>/scripts/upgrade_plan.py <project-root>
```

## Execute And Resume

- Resume from `program.md`, the active task and only its referenced memory/evidence. Reconcile changes to load-bearing premises before following the saved next action; reassess affected conclusions while preserving unrelated verified work.
- If the territory reveals a material unknown or deviation, read `references/unknowns-contract.md`, resolve discoverable facts from evidence, and update or stop the plan before crossing a bound.
- Execute according to dependencies and risk, and link completed nodes to their acceptance evidence. Read `references/reflection-contract.md` only when a material event triggers reflection or the plan uses Loop; routine success needs no invented lesson.
- Create later task packages just in time, after their dependencies and acceptance conditions are known.
- A failed verifier changes the plan, retires an assumption, or triggers escalation; repeating output without new information is not progress.
- If a checker passes but reality fails, treat it as a foundation defect: reopen acceptance, identify the escaped failure class, and add the cheapest decisive sensor.
- Apply `references/clean-contract.md` when accumulated state impairs recovery or a handoff/terminal transition requires reconciliation; concise aligned state needs only the contract's no-op marker.
- Before `阻塞`, `待验收`, or `完成`, read `references/status-and-completion.md`.
- For a shared abstraction change, read `references/abstraction-quality.md`.
- To audit or repair existing plan state, read `references/audit-checklist.md`.
- When designing or changing cross-session recovery, use the interruption probe in `references/audit-checklist.md`; structural validation alone does not prove correct resumption. Ordinary resumes do not require a new recovery experiment.

## Invariants

- A plan-only request does not authorize implementation. A build/fix request includes the planning needed to execute it and does not require another start confirmation.
- Every completed node has evidence. Lite and Full Linear record reflection only for material learning; Loop records one evidence-linked reflection per verified attempt. Record decision summaries, not hidden chain-of-thought.
- Route discovered unknowns into existing plan state; research discoverable facts and choose reversible details inside accepted bounds rather than opening a parallel diary or approval gate.
- Prefer declarative objectives with explicit bounds; reserve imperative constraints for fragile, high-stakes, or deliberately standardized paths and surface a materially better option without overriding the lock.
- For behavior-preserving work, treat reference code, translated tests, and differential evidence as specification sources; document intentional differences instead of hiding them behind a broad "equivalent" claim.
- `完成` and `待验收` require acceptance evidence. Use `待验收` only for an explicitly retained owner decision, not a template checkpoint or optional review.
- When evidence-validity checking is explicitly enabled, a recorded source, test, config, data, or acceptance change makes only the affected evidence stale. Unrelated unrecorded files do not force a full rerun. Fingerprints cannot substitute for coverage or behavioral verification.
- Verification must be finer than the change slice and link acceptance to raw evidence; executor self-report is not terminal evidence.
- A blocked item names the missing input, owner or external condition, and unblock action.
- Loop mode has a finite budget, bounded execution scope, independent checker, sensor stack, granularity alignment, calibration rule, reflect trigger, and stop/escalation condition.
- Preserve locked bounds and project conventions; store history only when it changes future execution. Clean may compress prose but preserves stable IDs, evidence links and raw facts.
- `plan-skill` owns durable execution state, not upstream decisions, domain research or final prose. Boundary and handoff: do not rerun upstream work unless missing or contradictory, and do not invoke all four by default.

## Resources

Use templates through `scripts/init_plan.py`; migrate with `scripts/upgrade_plan.py`; validate with `scripts/validate_plan.py`. `references/status-and-completion.md`, `references/abstraction-quality.md` and `references/audit-checklist.md` cover terminal state, shared abstractions and repair. `scripts/check_evidence_snapshot.py` checks the optional `references/evidence-validity.md` contract. Examples and tests are regression fixtures, not ordinary planning context.
