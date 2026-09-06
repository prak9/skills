---
name: code-review-craft
description: Review a code change or subsystem to reconstruct behavior, find evidence-backed defects, and give a calibrated approval decision. Use for a PR, diff, commit, explicit code audit, architectural review, or requested code-path explanation; do not invoke merely because an implementation task touches code, and do not implement fixes unless requested.
---

# Code Review Craft

Treat review as the judgment-bearing outer loop around automated engineering work.

```text
inner loop: inspect -> hypothesize -> test -> report
outer loop: choose what matters -> judge evidence -> approve or reject -> own the result
```

Automate evidence collection aggressively. Do not outsource comprehension, quality judgment, or accountability.

## Route the task

- **Explain code:** reconstruct purpose, execution path, state, invariants, side effects, and failure behavior. Read `references/comprehension-protocol.md` for an unfamiliar or cross-file system.
- **Review a diff, PR, or strict code-quality audit:** compare intended behavior with actual behavior and report actionable findings plus an approval state. For a maintainability-focused audit, explicitly run the structural-simplification pass below. Read `references/review-flow.md` and `references/review-rubric.md`.
- **Audit a subsystem or architecture:** trace trust boundaries, persistence, concurrency, recovery, and operational consequences beyond the changed lines. Read both references above.
- **Train or evaluate judgment:** predict before validation, keep an error ledger, and score review quality across real changes. Read `references/judgment-training.md`.
- **Calibrate review or merge autonomy:** evaluate representative task classes, choose the least authority supported by evidence, and gate auto-merge with revision-linked verification. Read `references/judgment-training.md`.

## Set the review contract

Before judging the code:

1. Read applicable repository instructions and the files under review in full.
2. Identify the change intent, expected behavior, base revision, scope, explicit acceptance criteria, and, when design depends on them, the lifecycle phase and realistic workload. Check that the change description says what changed and why, and still matches the diff. Clarify any load-bearing term whose meaning differs across the request, public API, implementation, documentation, or tests.
3. Name the protected properties: correctness, compatibility, data integrity, security, latency, availability, consistency, reliability, maintainability, cost, or another project-specific constraint. Require evidence only for properties material to this change.
4. Calibrate depth to impact and reversibility. Inspect architecture, migrations, auth, billing, concurrency, public APIs, and destructive operations more deeply than local formatting or generated boilerplate.
5. Check reviewability: the change should be one coherent, independently safe step with related tests. If mixed behavior, refactoring, generated churn, or sheer breadth prevents reliable review, say so early and propose concrete split boundaries.
6. Infer missing intent from callers, tests, docs, schemas, history, and existing patterns. State any material assumption; do not invent a specification.

Do not modify code during a review unless the user also asks for a fix. Run read-only inspection and relevant diagnostics; treat generated caches or test artifacts as incidental, not as permission to change source. If fixes are requested, continue through the supported in-scope corrections and verification without waiting for a second approval of each finding. A review verdict does not authorize merging or publishing.

## Apply the approval standard

Optimize for team progress and long-term code health together. Approve when the change definitely improves or preserves the system's overall health and no required concern remains; do not demand perfection or block on personal preference. Do not approve a known net degradation merely because the change is urgent, large, or expensive to revise.

Technical evidence and repository rules outrank taste. When several approaches are equally valid under those constraints, accept the author's choice. Keep required corrections separate from optional improvement, polish, education, and praise so the author can act without guessing.

## Predict before validation

After learning the intent but before trusting tests or the author's explanation, write a short private risk forecast:

- Which invariant is easiest to break?
- Which boundary, failure path, or state transition is most likely missing?
- Which downstream caller or operational behavior could change?
- What evidence would disprove the concern?

Use the forecast to direct attention, not to anchor the verdict. Revise it when the code disagrees. In judgment-training mode, preserve the forecast and compare it with the final result.

## Navigate for early feedback

Read `references/review-flow.md` for a PR, multi-file diff, oversized change, author-facing review, or approval recommendation.

1. Take a broad view: decide whether the change belongs, its description is trustworthy, and its shape is reviewable.
2. Inspect the load-bearing design or main file first. If the direction is wrong, report that immediately with a constructive alternative; do not spend the review budget polishing code likely to disappear.
3. Then inspect every in-scope human-written line in a logical sequence, using tests early when they recover intent.
4. State which files, layers, or risk dimensions were and were not reviewed. Route specialist concerns to a qualified reviewer instead of implying expertise.

Fast review means low response latency and a clear next action, not shallow judgment. For a huge change, an early scope or design response is more useful than silence followed by an incomplete pseudo-approval.

## Reconstruct the system

Read beyond the diff until the behavior can be explained without guessing:

1. Locate entry points, callers, callees, interfaces, schemas, configuration, and tests.
2. Trace inputs through branches and state transitions to outputs, side effects, and recovery paths.
3. Identify invariants, ownership, trust boundaries, lifecycle, and concurrency assumptions.
4. Check how the code behaves when inputs are empty, malformed, duplicated, delayed, reordered, partially applied, retried, or interrupted.
5. Perform the explain-back gate: state what the code does, why it does it, what must remain true, and how failure becomes visible.

If any material step still depends on “the framework probably handles it,” keep reading or mark the uncertainty. Passing the explain-back gate is required before approval.

## Search for structural simplification

After checking behavior, inspect every meaningful change for the complexity it adds:

1. Inventory new branches, flags, modes, wrappers, state owners, type escape hatches, and boundary crossings.
2. Look for a behavior-preserving change to the state model, ownership boundary, or control-flow shape that would make several of those concepts disappear. Treat this as a **code-judo move**: use the existing architecture more effectively so the implementation becomes smaller and more direct.
3. Prefer deleting concepts and special cases over moving the same complexity into more helpers, files, or generic machinery. A decomposition is not a simplification when readers must still hold the same states and branches in mind.
4. Check whether policy is scattered through unrelated paths, canonical logic is duplicated or placed in the wrong layer, or unnecessary optionality, casts, and pass-through abstractions obscure the real contract.
5. Check orchestration for needlessly serialized independent work and related updates that can become partially applied, but propose concurrency or atomicity changes only when they preserve required ordering and make the design clearer.

Publish a structural finding only when the diff demonstrates a concrete maintenance cost and repository evidence supports a materially simpler direction. Cite the affected decision sites or invariant, explain which concepts the direction removes, and give the smallest safe migration and test boundary. Treat file growth and numeric line thresholds as investigation signals, not verdicts. If no clear, behavior-preserving simplification is supported, keep the idea optional or drop it; do not demand speculative rewrites, future-proof abstractions, or personal style.

## Audit The Approval Argument

Treat every verdict as a compact argument: the approval claim depends on supported requirements and invariants, evidence from the actual code and probes, and an inference that survives the strongest realistic failure path. Keep these separate:

- Tests demonstrate the cases they exercise; they do not prove that the contract or case selection is complete.
- Matching words do not prove matching semantics; compare definitions, units, defaults, boundaries, and lifecycle across specification and implementation.
- A plausible concern is not a finding until its premises and trigger are evidenced; absence of an observed failure is not proof of safety.
- Before approving or reporting, try the strongest counterexample and state the residual boundary that remains unverified.

## Convert recurring review work into enforcement

When the same evidence-backed `Required` finding recurs, or one high-consequence systemic defect exposes a stable invariant, identify the earliest maintainable layer that can prevent or reject it: state or ownership design, types and module boundaries, compiler or static analysis, lint or architecture checks, deterministic regression tests, then runtime guards. Keep project guidance and review rules for contextual judgment that cannot be decided reliably by code.

Keep the current finding and the hardening opportunity separate. Do not block a focused PR on building general infrastructure unless the absent guard makes that revision unsafe, and do not infer recurrence from one example. A proposed guard should name its target failure, clean negative, false-positive cost, owner, and condition for narrowing or retirement.

## Allocate attention by cost of late change

Review from the base of this pyramid upward. Spend the most human judgment where a mistake becomes most expensive to change later:

1. **API semantics:** judge public contracts, compatibility, consistency, boundaries, defaults, and whether the interface is as small as possible but as large as required.
2. **Implementation semantics:** verify requirements, invariants, failure behavior, security, performance, observability, dependency cost, and unnecessary complexity.
3. **Documentation:** check that changed behavior, configuration, migration, and operational expectations are documented accurately where their users will look.
4. **Tests:** use tests as evidence that important behavior, boundaries, integrations, and non-functional requirements are protected.
5. **Code style:** leave formatting and mechanical convention checks to automation when possible; spend human review only on readability or consistency problems with a concrete consequence.

This order allocates attention; it does not rank severity or require a rigid reading sequence. Read tests early when they help recover intent, use them as evidence at every layer, and pursue a plausible high-impact risk immediately. Rank findings by impact and likelihood regardless of their layer.

Compare the change against the contract and surrounding system at each layer. Check the hard path, not only the intended path: boundaries, partial failure, retry, rollback, concurrency, compatibility, and cleanup. Look for the final 10%: error semantics, observability, safe rollout, migration ordering, resource cleanup, and exact behavior at limits.

Use targeted tests, static analysis, type checking, minimal reproductions, logs, or history when they can confirm or refute a concern. Read the full output and connect each result to a claim. Do not inflate confidence because a broad suite passed. Prefer project conventions and existing dependencies. Flag abstractions only when they create a concrete cost or hide an invariant, and separate defects from preferences.

## Decide what qualifies as a finding

Report a finding only when all four conditions hold:

1. A specific trigger or realistic state reaches the problem.
2. The current code permits that path.
3. The consequence matters to behavior, security, data, operations, or maintainability.
4. The claim is supported by code, a reproducible check, documented intent, or a clearly stated invariant.

Before publishing, try to disprove each finding. Drop speculative complaints, duplicate symptoms, and issues outside the change unless the change activates them.

Assign severity by impact and likelihood:

- **P0:** active or near-certain catastrophic loss, compromise, or outage.
- **P1:** likely severe security, data, availability, or core-function failure.
- **P2:** meaningful functional regression or failure under realistic conditions.
- **P3:** limited edge-case defect or concrete maintenance/operational debt.

Do not use severity to express certainty. State uncertainty separately.

Also assign comment disposition independently from severity:

- **Required:** must be resolved before approval because a contract, invariant, standard, or net code health would otherwise fail.
- **Optional / Consider:** credible improvement that is not needed for approval.
- **Nit:** minor polish; never blocks.
- **FYI:** educational context or future consideration; no action expected in this change.

P0–P3 findings are normally `Required`. Do not inflate an optional preference into a P3 defect. Positive reinforcement may be included when it names a practice worth preserving.

## Deliver the review

Lead with findings, ordered by severity. Use this shape:

```text
[P1] Imperative, specific title — path/to/file.ext:line
Disposition: Required
Trigger: the input, state, sequence, or environment that reaches the issue.
Impact: the observable failure and affected user or system.
Evidence: the relevant control/data path, test result, or violated contract.
Fix direction: the smallest safe direction, without implementing it unless asked.
```

Keep each finding self-contained and cite the narrowest useful location. Do not bury findings in a general summary.

After the findings, add only what helps the decision:

- material assumptions or open questions;
- tests run and decisive evidence;
- residual risks or untested paths;
- a brief system model when the user asked for understanding.
- optional, Nit, FYI, or positive comments only when their nonblocking intent is explicit.

End a PR review with one calibrated state:

- **Approve:** no required concern remains and the change improves or preserves code health.
- **Approve with comments:** only explicitly nonblocking comments remain.
- **Request changes:** at least one required finding remains.
- **Blocked / needs specialist:** the reviewed scope or evidence cannot support a responsible verdict; name the missing reviewer, evidence, or split.

If no qualifying findings remain, say so plainly. State what was inspected and any residual test or comprehension gap; do not invent a concern to make the review look useful.

## Preserve accountability

Recommend an approval state only when the evidence supports it. Treat auto-merge as an earned, task-class-specific privilege, never an agent-wide capability or throughput target. Separate local implementation, technical review, and authority to release. Honor existing approval for its exact scope; ask at an unresolved consequential choice, a reserved human gate, or a new side effect—not merely because a task mentions architecture, auth, or compatibility. Prepare authorized analysis, fixes, and verification before that gate. Make the outstanding owner decision visible; never imply that tool output has accepted the consequence for them.
