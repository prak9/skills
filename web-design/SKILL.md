---
name: web-design
description: "Design, build, redesign, or visually review responsive and accessible web interfaces with rendered verification. Use for substantial UI/UX work, not backend-only or narrow logic fixes."
---

# Web Design

Create interfaces specific to the user's job, content, brand and constraints. Define what good means, build the smallest coherent direction, render it and verify the relevant claims. Reviews inspect; implementation requests may edit.

## Preserve Outcomes And Boundaries

Preserve supplied facts, content meaning, brand rules, user flows, privacy, task constraints, and the host product's framework and conventions. The result should make the user's primary job and next action legible, use a composition specific to the material, and keep important states responsive, accessible, keyboard-usable, and recoverable. Visual polish cannot compensate for broken meaning or behavior.

When direction is underspecified, infer a reversible choice from the brief and product. Alternatives are useful only when they resolve a material uncertainty; they are not a mandatory approval gate.

## Inspect And Choose A Direction

Read the implementation and supplied references that own the experience, enough to identify the user job, observable success, content, actions, states, constraints, and existing design language. Reuse established primitives and dependencies unless a concrete requirement justifies a change; external services, tracking, data transfer, or architecture commitments still require scope coverage.

Read `references/composition-and-taste.md` for a new page, major redesign, weak hierarchy, unclear direction, or anti-template review. It contains the optional methods for comparing directions, mapping meaning to geometry, building hierarchy, and testing visual taste. An established direction that satisfies the task needs no invented alternative.

## Build The Interface

- Implement the smallest coherent slice that can establish the requested experience; a representative slice is useful when direction remains uncertain, not a required phase.
- Use semantic controls and resilient responsive layout. Preserve reading order, keyboard operation, recovery paths, and every meaningful state the chosen flow can enter.
- Keep copy and media grounded in supplied or authorized material. Do not invent claims, urgency, testimonials, metrics, or fake product screenshots.
- Motion may explain state or continuity, but the experience must work without it and respect reduced-motion preferences.

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

Render the actual implementation when tooling permits. Choose viewports, themes, content extremes, network conditions, and interaction states from the changed behavior and product risks; a general responsive redesign normally includes narrow mobile and representative laptop evidence. Inspect whether the primary task, hierarchy, behavior, reflow, semantics, trust, and visual restraint satisfy the brief. `references/composition-and-taste.md` and `references/interface-quality.md` provide deeper diagnostic questions when needed.

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
