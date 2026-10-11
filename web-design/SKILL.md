---
name: web-design
description: "Design, build, redesign, and visually review production web interfaces with intentional information architecture, composition, responsive behavior, accessibility, interaction states, and evidence-backed rendered verification. Use when Codex creates or substantially changes landing pages, product pages, dashboards, forms, web apps, reports, design systems, or HTML/CSS/React/Next.js/Vue/Svelte UI; or when a user asks to improve aesthetics, UX, visual hierarchy, responsiveness, accessibility, or generic AI-generated design. Do not trigger for backend-only work or a narrow logic-only frontend fix with no interface impact."
---

# Web Design

Create interfaces specific to the user's job, content, brand and constraints. Define what good means, build the smallest coherent direction, render it and verify the relevant claims. Reviews inspect; implementation requests may edit.

## Protect This Priority Order

1. Preserve supplied facts, content meaning, brand rules, user flows, privacy, and task constraints.
2. Preserve the host framework, routes, component conventions, design tokens, and delivery surface.
3. Make the user's primary job and the interface's next action immediately legible.
4. Choose a composition and visual language specific to the material instead of a reusable AI template.
5. Make every important state keyboard-usable, responsive, accessible, and recoverable.
6. Refine detail and delight only after structure, behavior, and verification are sound.

When direction is underspecified, infer a reversible choice from the brief and product; contrasting sketches are evidence, not a mandatory selection gate.

## Inspect Before Designing

- Read the actual routes, components, styles, tokens, assets, tests, and copy that own the experience. Do not design from filenames or a screenshot alone when the implementation is available.
- Identify the user, context, job and observable success.
- Inventory content, actions, states, evidence, unknowns, and constraints. Distinguish supplied facts from invented placeholder copy.
- Inspect supplied references directly. Extract hierarchy, rhythm, geometry, typography, interaction, and density; do not copy brand assets or surface decoration blindly.
- In an existing product, reuse its primitives before adding new ones. In a greenfield task, choose the smallest runnable stack; semantic HTML, CSS, and small JavaScript are the fallback.
- Reuse dependencies. Add one only when its concrete value exceeds its maintenance cost; paid services, tracking, external transfers or architecture commitments require scope coverage.

## Establish The Design Direction

Read `references/composition-and-taste.md` for a new page, major redesign, weak hierarchy or unclear direction.

Privately define:

- the primary user job and first-viewport promise;
- the one dominant object or relationship;
- the content order and primary action;
- the design-system inheritance and allowed deviations;
- concrete type, color, spacing, shape, imagery, and motion rules;
- empty, loading, error, success, long-content, and narrow-screen behavior.

If comparison is useful, vary topology, density or evidence placement—not merely color. Use an established direction directly when it fits.

Choose geometry before components. Use position, length, sequence, proportion, alignment, and grouping to express relationships. Treat cards, accordions, tabs, charts, and carousels as mechanisms, not default decorations.

## Build The Interface

- Choose a checkable implementation slice; use a representative slice first only when direction remains uncertain.
- Establish hierarchy through type, alignment, spacing, and proportion before adding surfaces, borders, shadows, color, or motion.
- Compose the page as a connected field with deliberate pacing. Repetition is for true peers; unequal content should not be forced into equal cards.
- Use semantic HTML and native controls. Links navigate; buttons act. Preserve source order as reading order.
- Keep responsive behavior intrinsic with grid, flex, wrapping, `min-width: 0`, and content-driven breakpoints before measuring layout in JavaScript.
- Design all meaningful states. Never leave users at an empty screen, unexplained error, irreversible action, or interaction dead end.
- Keep copy concrete and action-oriented. Do not invent claims, urgency, testimonials, metrics, or fake product screenshots.
- Use motion only to explain state, preserve continuity, or confirm action. The complete experience must work without it and respect reduced-motion preferences.

Read `references/interface-quality.md` before implementing forms, navigation, data-dense UI, motion, responsive behavior, or final interaction polish.

## Verify The Relevant Claims

Match each material requirement to a check. Read `references/verification-foundation.md` only for formal comparisons, automated optimization or system-wide rule promotion requiring a stable evaluator.

Use the cheapest check that can decide the claim; the maker's statement that a page “looks good” is not evidence:

- build, types, lint, and schema for structural defects;
- DOM, accessibility, and component checks for semantics and states;
- interaction tests for flows, errors, URL behavior, and keyboard operation;
- rendered screenshots for hierarchy, overflow, responsive reflow, and themes;
- performance traces for latency, layout shift, and expensive interaction;
- evidence-based visual review for taste and brand fit; use an independent reviewer when valuable and retain only consequential human decisions not already delegated.

Checks must cover changed behavior and localize defects. A redesign cannot close on “build passes”; render representative viewports and exercise changed flows.

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
8. **Restraint:** Can any card, border, pill, icon, effect, label, or paragraph be removed without losing meaning or affordance? Remove it when changes are authorized; otherwise report consequential excess.

Fix material defects and rerun affected checks. A first successful slice does not complete a broader request; stop polishing once acceptance passes and report any real limit accurately.

## Deliver The Result

- For a review, report material findings with locations, evidence, consequences, and repair directions.
- For implementation, return the implemented interface, not a mood-board essay or self-congratulatory design narrative. Summarize the chosen direction, changed files, verification evidence, and residual risk concisely.
- Name anything not rendered or tested. Do not convert an unverified assumption into a completion claim.
- Preserve enough rationale that another engineer can explain the hierarchy, state model, and verification path without chat history.

## References

- `references/composition-and-taste.md`: read for new design direction, major redesign, information architecture, data composition, or anti-template review
- `references/interface-quality.md`: read for accessibility, interaction, forms, responsive layout, content resilience, performance, media, and motion
- `references/verification-foundation.md`: read for formal multi-round comparisons, automated optimization, or design-rule promotion requiring comparable evidence
