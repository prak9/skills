# Web Design Verification Foundation

Use this contract to prevent a design loop from becoming a fast producer of plausible but unverified UI.

## Define The Loop

| Part | Web-design definition |
|---|---|
| Setpoint | User job, primary flow, content truth, design direction, viewports, states, and observable acceptance. |
| Actuator | Files, components, tokens, assets, tools, and external effects the implementation may change. |
| Sensors | Independent structural, behavioral, rendered, performance, and human checks. |
| State | Current slice, frozen fixtures, screenshots, test output, decisions, and evidence-linked reflection. |
| Controller | Finite iteration budget, revision rule, stop/escalation condition, and approval gate. |

The maker may run the sensors, but “I implemented it” or “it looks polished” is never terminal evidence.

## Build A Judgment Coverage Map

Create this map privately for material acceptance conditions:

| Claim | Plausible failure | Cheapest decisive sensor | Raw evidence | Owner / gate |
|---|---|---|---|---|
| Primary task is clear | competing hierarchy or hidden action | rendered first-viewport review | screenshot | independent visual reviewer |
| Flow works | dead end, stale state, wrong navigation | interaction test | trace or test output | deterministic checker |
| Accessible | unlabeled or keyboard-inoperable control | semantic/accessibility check plus keyboard run | DOM report and scenario | deterministic checker |
| Responsive | clipping, overflow, unusable density | narrow and wide render | screenshots | visual checker |
| Brand fit | parallel tokens or copied reference style | token/diff inspection plus visual review | code diff and screenshot | brand owner when material |
| Fast enough | layout shift or slow interaction | runtime/performance trace | measured output | declared budget |

Coverage is complete when every material claim has a decisive sensor or explicit retained human judgment. Do not invent a percentage without a defined denominator.

## Align Granularity

- **Change slice:** one route, flow, composition region, component family, or state model per attempt.
- **Verification precision:** sensors must localize more finely than the slice can fail. A page rewrite needs viewport and flow evidence; a control change needs state and keyboard evidence.
- **Memory event:** record the attempted direction, evidence, defect, retained strength, and next rule. Do not store a token transcript or only “design done.”

If verification is coarser than the change, split the change or strengthen the sensors before continuing.

## Descend Judgment

Use the cheapest layer that can actually decide the claim:

1. Build, types, lint, schema, and static tokens.
2. DOM semantics and automated accessibility checks.
3. Component and interaction tests.
4. Runtime probes for latency, layout shift, hydration, and network behavior.
5. Rendered screenshots across representative viewports, states, and themes.
6. Independent visual/rubric review for hierarchy, composition, density, and brand fit.
7. Human approval for taste, policy, commercial meaning, and high-consequence tradeoffs.

Automation can find missing names and overflow; it cannot fully decide whether the page has the right focal relationship. Human taste cannot replace a keyboard test. Route each bug to its layer.

## Freeze The Evaluator

Within an attempt, freeze:

- content and data fixtures;
- reference images or brand rules;
- viewport, theme, locale, and state matrix;
- accessibility and performance thresholds;
- visual rubric and named reviewer role.

Changing these is a harness revision. Version it, rerun affected evidence, and do not count the moved target as implementation improvement. Use unseen content or an untested viewport before promoting a new design rule across the system.

## Inspect Rendered Evidence

For each relevant case, capture enough evidence to replay the decision:

- first viewport and full-page render;
- narrow and laptop viewport; wide when layout expansion matters;
- default plus material empty, dense, loading, error, success, and destructive states;
- light/dark, reduced motion, locale, or slow network when supported or risky;
- keyboard path and focus order for the primary flow;
- build/test/accessibility/performance output tied to the same revision.

Inspect screenshots at actual size, not only thumbnails. Check hierarchy, alignment, line breaks, clipping, sticky/fixed collisions, local scroll regions, focus visibility, tap targets, and whether important evidence is legible.

## Revise And Stop

Fix one highest-impact systemic defect per pass. Preserve what the evidence says is working. A failed render changes the composition, implementation, fixture, or explicit acceptance contract; repeating cosmetic tweaks without a new hypothesis is not progress.

Stop when:

- declared acceptance and evidence paths pass;
- no known material defect remains in the tested matrix;
- the finite iteration budget is exhausted; or
- an unresolved brand, taste, content, or product judgment requires its human owner.

Completion reports the implementation, evidence, untested cases, and retained judgment. Keep the internal scorecard and process log out of the user-facing artifact unless requested.
