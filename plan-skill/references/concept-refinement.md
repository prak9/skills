# Concept Refinement

Use this guide only when a raw idea has several materially different directions. Stop once one direction is concrete enough to plan.

```text
Idea -> Confirmed brief -> Lite or Full plan
```

## Understand And Expand

- Restate the idea as an observable problem for a named user or operator.
- Inside a codebase, read relevant specs, entry points, tests, and prior docs before generating options.
- Ask only questions whose answers could change the direction, scope, or success criterion.
- Generate distinct options only while meaningful alternatives remain. Useful lenses include simplification, inversion, audience shift, constraint removal, and adjacent combination.

## Evaluate And Converge

Compare the viable directions on:

- user value: who benefits, how much, and whether the idea is a painkiller or a vitamin
- feasibility: technical/resource cost and hardest unknown
- differentiation: why it wins or why users would switch

For each serious direction, name what must be true, what could kill it, and what is intentionally ignored. Recommend one direction when the evidence supports it; do not preserve rejected alternatives as plan state.

## Sharpen And Ship The Brief

The confirmed brief needs only:

- observable problem and target user
- observable success
- chosen direction and why
- locked constraints and non-goals
- assumptions or open questions that can still change execution

For Lite, map these directly into `Outcome`, `Constraints`, `Acceptance`, and `Plan`. For Full, use `Outcome`, `Context`, `Constraints And Decisions`, `Acceptance`, and `Node Index`.

After convergence, read `pre-execution-grill.md` only if a remaining uncertainty could change scope, method, risk, or whether to proceed.
