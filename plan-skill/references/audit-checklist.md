# Audit Checklist

Audit the plan by checking authority, usefulness, and evidence rather than template volume.

## Surface

- Inline work did not create durable artifacts without a reason.
- Lite remains a single `program.md`; upgrade it when handoff, multiple sessions, Loop mode, risk, or independently owned task packages appear.
- Full creates task packages just in time rather than pre-populating a backlog.

## Authority

- Lite has one source for node status and evidence.
- New Full plans keep task status only in task packages; `program.md` is an index and project-level summary.
- No generated view is maintained by hand when it can be derived.

## Readiness And Scope

- A raw idea was refined only when directions were genuinely open.
- The readiness gate was used because a material uncertainty could flip the decision, not merely because of the task category.
- Locked constraints, negotiable implementation space, acceptance evidence, and the next useful action are concrete.
- Loop mode maps intent, actuator, sensor, state, and controller; it has a finite budget, bounded execution scope, independent checker, evidence path, calibration rule, and stop condition.

## Execution And Evidence

- Each node is independently useful or proves a material assumption.
- Completed or acceptance-ready work has evidence that would fail if the result were broken.
- Verification is finer than the change slice, each material acceptance condition has a decisive sensor or retained human gate, and maker self-report is not terminal evidence.
- Every completed atomic node points to one `R-*` entry that records wrong/changed, right/preserve, evidence, and the next rule.
- A blocked item names its unblock condition.
- Outputs are created and gitignored only when the task produces deliverable artifacts.
- Memory contains the per-node reflection ledger plus only decisions, findings, and consequential runs that change future work.

## Clean And Complexity

- `Clean state` becomes `Due` at handoff or terminal boundaries, after the fixed accumulation thresholds, or when durable state drifts.
- Clean preserves stable IDs, raw evidence, and unique node reflections while retiring duplicate, stale, or superseded Markdown state with pointers.
- Program, active task, memory, and referenced living docs agree on authority, constraints, decisions, and next action.
- A responsible owner can replay why the result passed and name residual gaps without relying on hidden chat history.
- The pass reduces retrieval surface or records a concrete no-op reason; it does not add an unbounded cleanup log.

## Validation

- `scripts/validate_plan.py --strict <project-root>` passes.
- Every checked task is referenced, IDs are unique, Markdown tables are valid, and no unresolved placeholder remains.
