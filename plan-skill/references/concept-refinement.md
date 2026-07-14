# Concept Refinement

Refine a raw idea into a confirmed concept before decomposing implementation work.

```text
Idea -> Concept brief -> Plan -> Task packages -> Execute -> Verify -> Memory
```

## Understand And Expand

- Restate the idea as a concise "How might we..." problem statement.
- Ask at most 3-5 sharpening questions. Target user and success criteria are required.
- Inside a codebase, read relevant specs, entry points, tests, and prior docs before generating options.
- Generate 5-8 considered variations using only useful lenses: inversion, simplification, audience shift, constraint removal, adjacent combination, 10x scale, or expert-domain obviousness.

## Evaluate And Converge

After the user reacts, cluster promising options into 2-3 distinct directions. Stress-test each on:

- user value: who benefits, how much, and whether the idea is a painkiller or a vitamin
- feasibility: technical/resource cost and hardest unknown
- differentiation: why it wins or why users would switch

For each direction, name what must be true, what could kill the idea, and what is intentionally ignored for now. Be direct when an idea is weak.

## Sharpen And Ship The Brief

Write the confirmed one-page brief into `program.md#concept-refinement` and map it into the plan:

- Problem Statement -> `program.md#problem-definition`
- Target User / Success Criteria -> `program.md#goals-and-metrics`
- Recommended Direction -> `program.md#strategy`
- Key Assumptions -> `program.md#exploration-and-hypothesis-validation`
- MVP Scope -> initial `program.md#implementation-plan` nodes
- Not Doing -> `program.md#problem-definition` Non-goals
- Open Questions -> `program.md#optional-state` or the relevant implementation subsection
