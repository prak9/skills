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

Ask only when missing human judgment materially changes the result and cannot be inferred from the supplied brief, product, or references. Otherwise choose a reversible direction and proceed. Cheap contrasting directions can inform that choice; they are not a mandatory user-selection gate.

## Inspect Before Designing

- Read the actual routes, components, styles, tokens, assets, tests, and copy that own the experience. Do not design from filenames or a screenshot alone when the implementation is available.
- Identify who opens the interface, in what context, to understand or accomplish what, and what success looks like.
- Inventory content, actions, states, evidence, unknowns, and constraints. Distinguish supplied facts from invented placeholder copy.
- Inspect supplied references directly. Extract hierarchy, rhythm, geometry, typography, interaction, and density; do not copy brand assets or surface decoration blindly.
- In an existing product, reuse its primitives before adding new ones. In a greenfield task, choose the smallest runnable stack; semantic HTML, CSS, and small JavaScript are the fallback.
- Reuse existing dependencies. Add a justified task-local dependency when covered by the requested implementation, and explain its value; do not ask again for ordinary setup. A new paid service, external data transfer, tracking, or material architecture commitment outside the brief needs its own authorization.

## Establish The Design Direction

Before broad implementation, read `references/composition-and-taste.md` for a new page, major redesign, weak hierarchy, or unclear visual direction.

Privately define:

- the primary user job and first-viewport promise;
- the one dominant object or relationship;
- the content order and primary action;
- the design-system inheritance and allowed deviations;
- concrete type, color, spacing, shape, imagery, and motion rules;
- empty, loading, error, success, long-content, and narrow-screen behavior.

When the direction is unclear, comparing structurally different options can help: vary topology, density, or evidence placement, not merely color. Use an established direction directly when it serves the brief; no fixed number of alternatives is required.

Choose geometry before components. Use position, length, sequence, proportion, alignment, and grouping to express relationships. Treat cards, accordions, tabs, charts, and carousels as mechanisms, not default decorations.

## Build The Interface

- Choose an implementation scope that can be meaningfully checked. For an uncertain direction, a representative slice can prove the visual language and primary flow before expanding; it is not a mandatory staging sequence for every task.
- Establish hierarchy through type, alignment, spacing, and proportion before adding surfaces, borders, shadows, color, or motion.
- Compose the page as a connected field with deliberate pacing. Repetition is for true peers; unequal content should not be forced into equal cards.
- Use semantic HTML and native controls. Links navigate; buttons act. Preserve source order as reading order.
- Keep responsive behavior intrinsic with grid, flex, wrapping, `min-width: 0`, and content-driven breakpoints before measuring layout in JavaScript.
- Design all meaningful states. Never leave users at an empty screen, unexplained error, irreversible action, or interaction dead end.
- Keep copy concrete and action-oriented. Do not invent claims, urgency, testimonials, metrics, or fake product screenshots.
- Use motion only to explain state, preserve continuity, or confirm action. The complete experience must work without it and respect reduced-motion preferences.

Read `references/interface-quality.md` before implementing forms, navigation, data-dense UI, motion, responsive behavior, or final interaction polish.

## Verify The Relevant Claims

For ordinary implementation, match each material requirement to an appropriate check. Read `references/verification-foundation.md` for formal multi-round comparisons, automated design optimization, or promotion of a new design rule across a system; those tasks need a stable evaluator and comparable evidence. Routine work does not require a coverage table, memory-event log, or evaluator version.

Use the cheapest check that can decide the claim; the maker's statement that a page “looks good” is not evidence:

- build, types, lint, and schema for structural defects;
- DOM, accessibility, and component checks for semantics and states;
- interaction tests for flows, errors, URL behavior, and keyboard operation;
- rendered screenshots for hierarchy, overflow, responsive reflow, and themes;
- performance traces for latency, layout shift, and expensive interaction;
- evidence-based visual review for taste and brand fit; use an independent reviewer when valuable and retain only consequential human decisions not already delegated.

Checks must cover the changed behavior and localize material defects. A whole-page redesign cannot close on “build passes”; render representative viewports and exercise the changed flows. Preserve acceptance criteria rather than redefining a defect away.

## Render, Inspect, And Revise

Render the actual implementation when tooling permits. Inspect at minimum a narrow mobile viewport and a representative laptop viewport; add wide, dark, high-density, reduced-motion, or slow-network cases when the product supports or risks them.

Use these questions where relevant, prioritizing the highest-risk changes:

1. **Task:** Is the primary job and next action obvious without explanation?
2. **First read:** Is one object dominant, and does the first viewport communicate value rather than merely mood?
3. **Composition:** Does every section advance a new question? Are alignment and whitespace intentional?
4. **Typography:** Are roles, measures, line breaks, numerals, and peer values consistent?
5. **Behavior:** Do keyboard, focus, loading, error, empty, destructive, and navigation states work?
6. **Reflow:** Does content recompose without clipping, accidental scrollbars, tiny text, or character-level wrapping?
7. **Trust:** Are semantics, contrast, labels, sources, privacy, and claims sound?
8. **Restraint:** Can any card, border, pill, icon, effect, label, or paragraph be removed without losing meaning or affordance? Remove it.

Fix material defects and rerun the affected checks; independent fixes may be combined when their effects remain verifiable. A vertical slice or first successful build is not the end of a broader implementation request. Stop polishing once acceptance passes; a self-imposed iteration count is a checkpoint, not permission to abandon unfinished work. At a real limit or necessary human decision, report the incomplete portion accurately. Keep critique notes internal unless requested.

## Deliver The Result

- Return the implemented interface, not a mood-board essay or self-congratulatory design narrative.
- Summarize the chosen direction, changed files, verification evidence, and residual risk concisely.
- Name anything not rendered or tested. Do not convert an unverified assumption into a completion claim.
- Preserve enough rationale that another engineer can explain the hierarchy, state model, and verification path without chat history.

## References

- `references/composition-and-taste.md`: read for new design direction, major redesign, information architecture, data composition, or anti-template review
- `references/interface-quality.md`: read for accessibility, interaction, forms, responsive layout, content resilience, performance, media, and motion
- `references/verification-foundation.md`: read for formal multi-round comparisons, automated optimization, or design-rule promotion requiring comparable evidence
