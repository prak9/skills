# Audit Checklist

Check a plan for these failures:

- `program.md` lacks measurable goals, final acceptance criteria, or task-package status.
- `program.md` lacks preferences/tradeoffs for a non-trivial plan, or fails to mark locked constraints and negotiable space.
- `program.md` contains CHANGELOG, run-log, historical status, or old Loop-attempt sections instead of only latest state.
- context and references are missing, stale, or lack source/freshness information.
- dependency graph, node-status table, checkpoints, or parallelization assumptions are missing (Full profile).
- Loop mode is enabled but no finite loop budget, verifier, reflect trigger, or stop condition exists.
- `memory.md` is missing (Full profile), stale, or lacks findings, CHANGELOG entries, run logs, or history summaries for completed or failed task packages.
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
- A task package lacks a Standing Checklist.
- A task package reached `待验收` or `完成` while applicable Standing Checklist items are unchecked or marked N/A without reasons.
- A task package reached `待验收` or `完成` without answered Pre-completion Red Team questions.
- A Lite-profile plan grew past ~3 task packages, multiple sessions, or Loop mode without upgrading to Full.
