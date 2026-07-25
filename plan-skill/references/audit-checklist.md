# Audit Checklist

Audit the plan by checking authority, usefulness, and evidence rather than template volume.

## Surface

- Inline work did not create durable artifacts without a reason.
- Lite remains a single `program.md`; upgrade it when handoff, multiple sessions, Loop mode, risk, or independently owned task packages appear.
- Full creates task packages just in time rather than pre-populating a backlog.

## Authority

- Lite has one source for node status and evidence.
- New Full plans keep task status only in task packages; `program.md` is an index and project-level summary.
- Legacy duplicated status and task-list views agree until migrated.
- No generated view is maintained by hand when it can be derived.

## Readiness And Scope

- A raw idea was refined only when directions were genuinely open.
- The readiness gate was used because a material uncertainty could flip the decision, not merely because of the task category.
- Locked constraints, negotiable implementation space, acceptance evidence, and the next useful action are concrete.
- Loop mode has a finite budget, verifier, reflect trigger, and stop condition.

## Execution And Evidence

- Each node is independently useful or proves a material assumption.
- Completed or acceptance-ready work has evidence that would fail if the result were broken.
- A blocked item names its unblock condition.
- Outputs are created and gitignored only when the task produces deliverable artifacts.
- Memory contains only decisions, findings, and consequential runs that change future work.

## Validation

- `scripts/validate_plan.py --strict <project-root>` passes.
- Every checked task is referenced, IDs are unique, Markdown tables are valid, and no unresolved placeholder remains.
- Existing legacy plans remain readable; migration is explicit and previewed.
