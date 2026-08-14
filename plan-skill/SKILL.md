---
name: plan-skill
description: "Use this skill when work needs durable planning state: a requested implementation plan, cross-session or multi-agent handoff, uncertainty-driven Loop execution, verification-foundation design for repeated agentic work, or audit, cleanup, simplification, and repair of existing plan artifacts or memory. It can expose preferences, tradeoffs, and unknowns; align change, verification, and memory granularity; capture evidence-linked reflection; create Lite or Full plans; control complexity; and validate status and evidence. Do not trigger it merely because an ordinary single-session task has several steps."
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
- `memory.md` is optional in Lite and required in Full. It owns durable decisions, findings, consequential runs, and reflections triggered by material learning.
- Code, tests, CI, logs, and runtime output are facts. Markdown points to evidence; it does not replace it.
- Generated deliverables may use `tasks/output/TASK-NNN-<slug>/` as a latest snapshot. Create and gitignore it only when a task actually produces such artifacts.

Never create a second hand-maintained view of state that can be derived from an authoritative field.

## Create Or Refresh

1. Read the request, relevant repository instructions, specs, entry points, tests, configuration, and recent changes.
2. Frame the plan as an objective plus bounds: state the observable outcome, inherited strategic defaults, tactical objective, imperative bounds, negotiable space, material assumptions, acceptance evidence, and next useful action.
3. Choose Inline, Lite, Full, or Loop.
4. For a raw idea with several plausible directions, read `references/concept-refinement.md`.
5. Read `references/unknowns-contract.md` when the territory is unfamiliar, important preferences are tacit, or implementation is likely to reveal constraints the prompt cannot contain.
6. Read `references/preference-contract.md` when valid solutions differ materially, a preference must be inferred, or a requested method may conflict with its objective.
7. Read `references/pre-execution-grill.md` only when unresolved judgment or evidence could change scope, method, risk, or whether to proceed.
8. Read `references/foundation-contract.md` when an agent may act repeatedly or without line-by-line supervision, a change slice is broader than its verifier, or the work includes irreversible effects. Loop mode always reads it.
9. Read `references/executable-spec-contract.md` for parallel agent work, ports, rewrites, migrations, or any task whose correctness depends on preserving reference behavior.
10. For Loop, read `references/loop-contract.md` before drafting its program and task state.
11. Initialize durable state:

   ```bash
   python3 <plan-skill>/scripts/init_plan.py <project-root> --title "<work title>"
   # Use --profile full only when Full/Loop is already justified.
   ```

12. Replace placeholders and run `scripts/validate_plan.py --strict <project-root>` before execution or handoff.

For a Lite plan that grows into Full:

```bash
python3 <plan-skill>/scripts/upgrade_plan.py <project-root> --dry-run
python3 <plan-skill>/scripts/upgrade_plan.py <project-root>
```

## Execute And Resume

- Resume by reading `program.md`, then the active task package and only the memory/evidence it references.
- If the territory reveals a material unknown or deviation, read `references/unknowns-contract.md`, resolve discoverable facts from evidence, and update or stop the plan before crossing a bound.
- Execute the smallest useful node and run its verifier. In Full Linear mode, read `references/reflection-contract.md` and write `R-*` only when its trigger fires; otherwise mark the node `None: <no trigger reason>`. Loop keeps one evidence-linked `R-*` per verified attempt.
- Create later task packages just in time, after their dependencies and acceptance conditions are known.
- A failed verifier changes the plan, retires an assumption, or triggers escalation; repeating output without new information is not progress.
- If a checker passes but reality fails, treat it as a foundation defect: reopen acceptance, identify the escaped failure class, and add the cheapest decisive sensor.
- When Clean becomes due, or before handoff, `待验收`, or `完成`, read `references/clean-contract.md` and compress stale or duplicated state before continuing.
- Before `阻塞`, `待验收`, or `完成`, read `references/status-and-completion.md`.
- For a shared abstraction change, read `references/abstraction-quality.md`.
- To audit or repair existing plan state, read `references/audit-checklist.md`.

## Invariants

- Planning is read-only unless the user also authorizes execution.
- Every completed node has evidence. Full Linear records reflection only for material learning; Loop records one evidence-linked reflection per verified attempt. Record decision summaries, not hidden chain-of-thought.
- Do not silently invent a material preference. Research discoverable facts, state consequential assumptions, and ask only when human judgment can change the plan.
- Treat unknowns as continuously discoverable: use the four classes as search lenses, then route each discovered unknown into existing plan state instead of maintaining a parallel unknowns diary.
- Prefer declarative objectives with explicit bounds; reserve imperative constraints for fragile, high-stakes, or deliberately standardized paths and surface a materially better option without overriding the lock.
- For behavior-preserving work, treat reference code, translated tests, and differential evidence as specification sources; document intentional differences instead of hiding them behind a broad "equivalent" claim.
- `完成` and `待验收` require acceptance evidence; written code is not completion.
- The executor's self-report is never terminal evidence. Verification must be finer than the change slice and expose a path from acceptance condition to raw evidence.
- A blocked item names the missing input, owner or external condition, and unblock action.
- Loop mode has a finite budget, bounded execution scope, independent checker, sensor stack, granularity alignment, calibration rule, reflect trigger, and stop/escalation condition.
- Preserve user constraints and existing project conventions; escalate before changing scope or acceptance criteria.
- Store historical facts only when they will change future execution; do not duplicate ordinary progress or Git history.
- Clean may compress Markdown state but must preserve stable IDs, evidence links, and raw facts.

## Resources

- `assets/program-lite.template.md`: single-file Lite contract; use through `init_plan.py`
- `assets/program-full-starter.template.md`, `assets/task-full-starter.template.md`, `assets/memory-starter.template.md`: compact Full contracts; use through `init_plan.py`
- `references/preference-contract.md`: strategic/tactical and declarative/imperative preference contract
- `references/unknowns-contract.md`: four unknown classes plus pre-, during-, and post-implementation discovery and routing
- `references/reflection-contract.md`: event-triggered Full reflection and per-attempt Loop feedback contract
- `references/foundation-contract.md`: closed-loop parts, maker/checker separation, granularity alignment, judgment descent, calibration, and comprehension-debt control
- `references/executable-spec-contract.md`: layered specifications, reference behavior, differential verification, and independently owned agent work packets
- `references/loop-contract.md`: exact Full/Loop program, task, and memory interface
- `references/clean-contract.md`: periodic alignment, distillation, and complexity-control contract
- `scripts/init_plan.py`: safe initialization without overwriting existing plan files
- `scripts/upgrade_plan.py`: previewable Lite-to-Full migration
- `scripts/validate_plan.py`: structural and semantic validation; add `--json` for machine-readable results
- `examples/lite-change/`, `examples/csv-export/`: test and migration fixtures; do not load for ordinary creation
- `tests/`: regression and context-budget checks
