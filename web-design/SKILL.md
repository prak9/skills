---
name: web-design
description: "Design, build, redesign, and visually review production web interfaces with intentional information architecture, composition, responsive behavior, accessibility, interaction states, and evidence-backed rendered verification. Use when Codex creates or substantially changes landing pages, product pages, dashboards, forms, web apps, reports, design systems, or HTML/CSS/React/Next.js/Vue/Svelte UI; or when a user asks to improve aesthetics, UX, visual hierarchy, responsiveness, accessibility, or generic AI-generated design. Do not trigger for backend-only work or a narrow logic-only frontend fix with no interface impact."
---

# Web Design

Create interfaces that are specific to the user's job, content, brand, and constraints. Treat visual quality as an engineered outcome: define what good means, build the smallest coherent direction, render it, and verify it with the right sensors.

## Protect This Priority Order

1. Preserve supplied facts, content meaning, brand rules, user flows, privacy, and task constraints.
2. Preserve the host framework, routes, component conventions, design tokens, and delivery surface.
3. Make the user's primary job and the interface's next action immediately legible.
4. Choose a composition and visual language specific to the material instead of a reusable AI template.
5. Make every important state keyboard-usable, responsive, accessible, and recoverable.
6. Refine detail and delight only after structure, behavior, and verification are sound.

Ask only when missing human judgment can materially change the audience, content meaning, brand direction, primary flow, or acceptance bar. Research code and references before asking. When taste is tacit, show cheap contrasting directions instead of asking the user to describe an aesthetic vocabulary they do not have.

## Inspect Before Designing

- Read the actual routes, components, styles, tokens, assets, tests, and copy that own the experience. Do not design from filenames or a screenshot alone when the implementation is available.
- Identify who opens the interface, in what context, to understand or accomplish what, and what success looks like.
- Inventory content, actions, states, evidence, unknowns, and constraints. Distinguish supplied facts from invented placeholder copy.
- Inspect supplied references directly. Extract hierarchy, rhythm, geometry, typography, interaction, and density; do not copy brand assets or surface decoration blindly.
- In an existing product, reuse its primitives before adding new ones. In a greenfield task, choose the smallest runnable stack; semantic HTML, CSS, and small JavaScript are the fallback.
- Do not add a framework, component library, icon set, font service, analytics package, or animation dependency unless it earns its cost and the user authorizes it.

## Establish The Design Direction

Before broad implementation, read `references/composition-and-taste.md` for a new page, major redesign, weak hierarchy, or unclear visual direction.

Privately define:

- the primary user job and first-viewport promise;
- the one dominant object or relationship;
- the content order and primary action;
- the design-system inheritance and allowed deviations;
- concrete type, color, spacing, shape, imagery, and motion rules;
- empty, loading, error, success, long-content, and narrow-screen behavior.

When multiple structures are plausible, compare 2 materially different composition hypotheses before coding. Change topology, density, and evidence placement, not merely color. Select the direction that makes the user's job clearest with the least mediation.

Choose geometry before components. Use position, length, sequence, proportion, alignment, and grouping to express relationships. Treat cards, accordions, tabs, charts, and carousels as mechanisms, not default decorations.

## Build One Coherent Vertical Slice

- Implement the smallest slice that proves the visual language and primary flow: often the shell, first viewport, one representative content section, and one interactive state.
- Establish hierarchy through type, alignment, spacing, and proportion before adding surfaces, borders, shadows, color, or motion.
- Compose the page as a connected field with deliberate pacing. Repetition is for true peers; unequal content should not be forced into equal cards.
- Use semantic HTML and native controls. Links navigate; buttons act. Preserve source order as reading order.
- Keep responsive behavior intrinsic with grid, flex, wrapping, `min-width: 0`, and content-driven breakpoints before measuring layout in JavaScript.
- Design all meaningful states. Never leave users at an empty screen, unexplained error, irreversible action, or interaction dead end.
- Keep copy concrete and action-oriented. Do not invent claims, urgency, testimonials, metrics, or fake product screenshots.
- Use motion only to explain state, preserve continuity, or confirm action. The complete experience must work without it and respect reduced-motion preferences.

Read `references/interface-quality.md` before implementing forms, navigation, data-dense UI, motion, responsive behavior, or final interaction polish.

## Build The Verification Foundation

Read `references/verification-foundation.md` whenever an agent may implement more than one visual slice without review, when the acceptance bar is mostly aesthetic, or before declaring a substantial interface complete.

Do not accept the maker's statement that a page “looks good.” For each important claim, define a failure class, sensor, and evidence path. Descend judgment to the cheapest decisive layer:

- build, types, lint, and schema for structural defects;
- DOM, accessibility, and component checks for semantics and states;
- interaction tests for flows, errors, URL behavior, and keyboard operation;
- rendered screenshots for hierarchy, overflow, responsive reflow, and themes;
- performance traces for latency, layout shift, and expensive interaction;
- an independent visual reviewer or retained human decision for taste and brand fit.

Verification must be finer than the change. A whole-page redesign cannot close on “build passes”; render representative viewports and exercise the changed flows. Freeze the content fixture, reference, viewport set, and rubric within an attempt. If the rubric changes, record it as a new evaluator version rather than moving the goalposts.

## Render, Inspect, And Revise

Render the actual implementation when tooling permits. Inspect at minimum a narrow mobile viewport and a representative laptop viewport; add wide, dark, high-density, reduced-motion, or slow-network cases when the product supports or risks them.

Review in this order:

1. **Task:** Is the primary job and next action obvious without explanation?
2. **First read:** Is one object dominant, and does the first viewport communicate value rather than merely mood?
3. **Composition:** Does every section advance a new question? Are alignment and whitespace intentional?
4. **Typography:** Are roles, measures, line breaks, numerals, and peer values consistent?
5. **Behavior:** Do keyboard, focus, loading, error, empty, destructive, and navigation states work?
6. **Reflow:** Does content recompose without clipping, accidental scrollbars, tiny text, or character-level wrapping?
7. **Trust:** Are semantics, contrast, labels, sources, privacy, and claims sound?
8. **Restraint:** Can any card, border, pill, icon, effect, label, or paragraph be removed without losing meaning or affordance? Remove it.

Fix the highest-impact systemic defect, render again, and stop only when acceptance passes, the finite iteration budget is reached, or a retained human judgment is needed. Keep critique and iteration notes internal unless requested.

## Deliver The Result

- Return the implemented interface, not a mood-board essay or self-congratulatory design narrative.
- Summarize the chosen direction, changed files, verification evidence, and residual risk concisely.
- Name anything not rendered or tested. Do not convert an unverified assumption into a completion claim.
- Preserve enough rationale that another engineer can explain the hierarchy, state model, and verification path without chat history.

## References

- `references/composition-and-taste.md`: read for new design direction, major redesign, information architecture, data composition, or anti-template review
- `references/interface-quality.md`: read for accessibility, interaction, forms, responsive layout, content resilience, performance, media, and motion
- `references/verification-foundation.md`: read for independent checking, judgment coverage, rendered evidence, granularity, calibration, and completion

This skill generalizes lessons from [Vercel's design.md](https://vercel.com/design.md) and [Web Interface Guidelines](https://vercel.com/design/guidelines). The user's product and brand remain the authority; Vercel's visual identity does not.
