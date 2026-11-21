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

Avoid adversarial review on abstract paper plans alone—critiquing unbuilt prose tends to hallucinate theoretical edge cases. When API ergonomics or runtime behavior is the crux, settle open questions with **empirical design artifacts**:
- draft a concise caller-facing README/tutorial first to work backward from real usage; or
- run an **isolated throwaway prototype** where the usual production-quality and smallest-change bars invert: build 2–3 labeled variants behind one switcher in an isolated scratch directory separate from production source (no production framework, no unit tests, no abstractions), treat the concrete observation (rendered screenshot, output, or measured timing) as the test, and deliver the **design decision**—not shippable code—before handing the winning direction to real implementation.

## Sharpen And Ship The Brief

The confirmed brief needs only:

- observable problem and target user
- observable success
- chosen direction and why
- locked constraints and non-goals
- assumptions or open questions that can still change execution

For a new or materially changed user-facing workflow, include the primary human or Agent user and the core journey: starting state, actions through the supported interface, observable result, and any material failure or recovery scenario. Map the journey to acceptance evidence and the delivery documentation the user will actually follow. Reuse accepted requirements; ask the owner only about unresolved product choices that change the journey or acceptance. A short brief is sufficient unless the project needs a fuller PRD.

When the requested outcome extends beyond implementation into adoption or ongoing operation, also name the consuming user or system, the owner of rollout and continued operation, and the observable signal that the result is being used successfully. Do not add adoption, rollout, or maintenance obligations to a task whose accepted scope ends at a bounded artifact or technical change.

For Lite, map these directly into `Outcome`, `Constraints`, `Acceptance`, and `Plan`. For Full, use `Outcome`, `Context`, `Constraints And Decisions`, `Acceptance`, and `Node Index`.

After convergence, read `pre-execution-grill.md` only if a remaining uncertainty could change scope, method, risk, or whether to proceed.
