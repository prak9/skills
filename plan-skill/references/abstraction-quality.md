# Abstraction Quality Gate

Use this contract when a task introduces, modifies, or removes a shared software abstraction. A shared abstraction includes a cross-module interface, service boundary, reusable domain object, base class, provider/factory, shared utility, protocol, or durable data contract. A local helper with one narrow caller is not automatically a shared abstraction.

## Declare The Impact

Set exactly one task-package value:

- `none`: no shared abstraction is involved
- `reuse`: use an existing abstraction without changing its contract
- `new`: introduce a shared abstraction or extension point
- `modify`: change the responsibility, boundary, or contract of an existing abstraction
- `remove`: delete or inline an existing abstraction

For `none` or `reuse`, write `N/A: <concrete reason>` under `Abstraction Gate`. For `new`, `modify`, or `remove`, complete every gate field before execution.

## Gate Fields

| Field | Quality bar |
|---|---|
| Concrete pressure / current consumers | Name the present duplication, change pressure, boundary need, or external contract and its real callers. Do not cite hypothetical future reuse alone. |
| Existing pattern / direct alternative | Name the repository pattern inspected and compare the simplest direct implementation. |
| Boundary / owned invariant | State the one responsibility or invariant the abstraction owns. |
| Explicit non-responsibilities | State nearby concerns that remain outside the boundary. |
| Expected variation | Name what is expected to vary and what must stay stable, based on evidence. |
| Concept count / indirection | Explain what concepts or branches disappear and why total cognitive load falls despite another layer. |
| Coupling / interface impact | Identify callers, dependencies, public surface, compatibility, migration, and ownership effects. |
| Contract verification | Define consumer-facing or contract tests that fail when the boundary is wrong, not only when the implementation is broken. |
| Rollback / deletion trigger | Define how to revert it and the evidence that would justify inlining, replacing, or deleting it. |

## Decision Rules

- Prefer direct code when the only justification is possible future reuse.
- Do not treat small or unstable similarity as sufficient evidence. Duplication can be cheaper than a wrong shared dependency.
- Treat “two consumers” as a heuristic, not a law. One consumer can justify an abstraction at an external protocol, security, ownership, or volatility boundary.
- Reject an abstraction that merely renames or hides complexity without reducing concepts, branching, coupling, or change cost.
- Keep the public surface smaller than the implementation surface. Expose only behavior required by current consumers.
- Record durable cross-task abstraction decisions in `program.md#decisions`; keep task-local implementation choices in the task package.

Before acceptance, ask:

1. Would deleting this layer make the code easier to understand?
2. Is the variation real and current, or speculative?
3. Did the abstraction reduce total concepts and change cost for its consumers?

The validator checks declarations and evidence fields. It cannot judge semantic cohesion or predict future change; verify those through code review, real consumers, and contract tests.
