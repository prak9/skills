---
name: plan-skill
description: "Use this skill when work needs durable planning state: a requested implementation plan, cross-session or multi-agent handoff, uncertainty-driven Loop execution, or audit/repair of existing plan artifacts. It can refine a raw idea, create a single-file Lite plan, expand work into Full task packages, preserve consequential decisions and findings, and validate status and evidence. Do not trigger it merely because an ordinary single-session task has several steps."
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

- In Lite, `program.md` is the only plan artifact.
- In Full, `program.md` owns project outcome, constraints, acceptance, task index, checkpoints, blockers, and next action. A task package is the only source of its task status and atomic execution state.
- `memory.md` is optional in Lite and required in Full. Record only decisions, findings, or consequential runs that change future work.
- Code, tests, CI, logs, and runtime output are facts. Markdown points to evidence; it does not replace it.
- Generated deliverables may use `tasks/output/TASK-NNN-<slug>/` as a latest snapshot. Create and gitignore it only when a task actually produces such artifacts.

Never create a second hand-maintained view of state that can be derived from an authoritative field.

## Create Or Refresh

1. Read the request, relevant repository instructions, specs, entry points, tests, configuration, and recent changes.
2. State the observable outcome, locked constraints, acceptance evidence, material unknowns, and next useful action.
3. Choose Inline, Lite, Full, or Loop.
4. For a raw idea with several plausible directions, read `references/concept-refinement.md`.
5. Read `references/pre-execution-grill.md` only when unresolved judgment or evidence could change scope, method, risk, or whether to proceed.
6. For Loop, read `references/loop-contract.md` before drafting its program and task state.
7. Initialize durable state:

   ```bash
   python3 <plan-skill>/scripts/init_plan.py <project-root> --title "<work title>"
   # Use --profile full only when Full/Loop is already justified.
   ```

8. Replace placeholders and run `scripts/validate_plan.py --strict <project-root>` before execution or handoff.

For a Lite plan that grows into Full:

```bash
python3 <plan-skill>/scripts/upgrade_plan.py <project-root> --dry-run
python3 <plan-skill>/scripts/upgrade_plan.py <project-root>
```

## Execute And Resume

- Resume by reading `program.md`, then the active task package and only the memory/evidence it references.
- Execute the smallest useful node, run its verifier, record evidence, and update the authoritative status once.
- Create later task packages just in time, after their dependencies and acceptance conditions are known.
- A failed verifier changes the plan, retires an assumption, or triggers escalation; repeating output without new information is not progress.
- Before `阻塞`, `待验收`, or `完成`, read `references/status-and-completion.md`.
- For a shared abstraction change, read `references/abstraction-quality.md`.
- To audit or repair existing plan state, read `references/audit-checklist.md`.

## Invariants

- Planning is read-only unless the user also authorizes execution.
- `完成` and `待验收` require acceptance evidence; written code is not completion.
- A blocked item names the missing input, owner or external condition, and unblock action.
- Loop mode has a finite budget, verifier, reflect trigger, and stop/escalation condition.
- Preserve user constraints and existing project conventions; escalate before changing scope or acceptance criteria.
- Store historical facts only when they will change future execution; do not duplicate ordinary progress or Git history.
- Keep legacy plans valid while migrating them deliberately; do not silently rewrite user-maintained state.

## Resources

- `assets/program-lite.template.md`: single-file Lite contract; use through `init_plan.py`
- `assets/program-full-starter.template.md`, `assets/task-full-starter.template.md`, `assets/memory-starter.template.md`: compact Full contracts; use through `init_plan.py`
- `assets/program.template.md`, `assets/task.template.md`: legacy detailed repair references; do not use for new plans
- `assets/memory.template.md`: optional detailed memory contract
- `references/loop-contract.md`: exact Full/Loop program, task, and memory interface
- `scripts/init_plan.py`: safe initialization without overwriting existing plan files
- `scripts/upgrade_plan.py`: previewable Lite-to-Full migration
- `scripts/validate_plan.py`: structural and semantic validation; add `--json` for machine-readable results
- `examples/lite-change/`, `examples/csv-export/`: test and migration fixtures; do not load for ordinary creation
- `tests/`: regression and context-budget checks
