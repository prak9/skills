---
name: code-review-craft
description: Read unfamiliar code and diffs, reconstruct behavior and invariants, evaluate correctness, maintainability, efficiency, security, operability, and tests, then produce evidence-backed review findings. Use when Codex needs to explain a code path, understand a repository or subsystem, review a PR/diff/commit, audit AI-generated code, assess an architectural change, find edge cases or failure modes, judge whether code is safe to approve, or train and evaluate code-review judgment. Work review-first and do not implement fixes unless the user explicitly asks.
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
- **Review a diff or PR:** compare intended behavior with actual behavior and report actionable findings. Read `references/review-rubric.md` for the relevant risk dimensions.
- **Audit a subsystem or architecture:** trace trust boundaries, persistence, concurrency, recovery, and operational consequences beyond the changed lines. Read both references above.
- **Train or evaluate judgment:** predict before validation, keep an error ledger, and score review quality across real changes. Read `references/judgment-training.md`.

## Set the review contract

Before judging the code:

1. Read applicable repository instructions and the files under review in full.
2. Identify the change intent, expected behavior, base revision, scope, and explicit acceptance criteria.
3. Name the protected properties: correctness, compatibility, data integrity, security, latency, availability, or another project-specific constraint.
4. Calibrate depth to impact and reversibility. Inspect architecture, migrations, auth, billing, concurrency, public APIs, and destructive operations more deeply than local formatting or generated boilerplate.
5. Infer missing intent from callers, tests, docs, schemas, history, and existing patterns. State any material assumption; do not invent a specification.

Do not modify code during a review unless the user also asks for a fix. Run read-only inspection and relevant diagnostics; treat generated caches or test artifacts as incidental, not as permission to change source.

## Predict before validation

After learning the intent but before trusting tests or the author's explanation, write a short private risk forecast:

- Which invariant is easiest to break?
- Which boundary, failure path, or state transition is most likely missing?
- Which downstream caller or operational behavior could change?
- What evidence would disprove the concern?

Use the forecast to direct attention, not to anchor the verdict. Revise it when the code disagrees. In judgment-training mode, preserve the forecast and compare it with the final result.

## Reconstruct the system

Read beyond the diff until the behavior can be explained without guessing:

1. Locate entry points, callers, callees, interfaces, schemas, configuration, and tests.
2. Trace inputs through branches and state transitions to outputs, side effects, and recovery paths.
3. Identify invariants, ownership, trust boundaries, lifecycle, and concurrency assumptions.
4. Check how the code behaves when inputs are empty, malformed, duplicated, delayed, reordered, partially applied, retried, or interrupted.
5. Perform the explain-back gate: state what the code does, why it does it, what must remain true, and how failure becomes visible.

If any material step still depends on “the framework probably handles it,” keep reading or mark the uncertainty. Passing the explain-back gate is required before approval.

## Evaluate the change

Compare implementation against the contract and the surrounding system:

- Check the hard path, not only the intended path: boundaries, partial failure, retry, rollback, concurrency, compatibility, and cleanup.
- Judge tests as evidence, not as truth. Verify that they would fail for the defect they claim to prevent and that assertions cover behavior rather than incidental implementation.
- Prefer project conventions and existing dependencies. Flag abstractions only when they create a concrete cost or hide an invariant.
- Separate defects from preferences. Report style only when it causes ambiguity, inconsistency, maintenance risk, or a documented rule violation.
- Look for the final 10%: error semantics, observability, safe rollout, migration ordering, resource cleanup, and the exact behavior at limits.

Use targeted tests, static analysis, type checking, minimal reproductions, logs, or history when they can confirm or refute a concern. Read the full output and connect each result to a claim. Do not inflate confidence because a broad suite passed.

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

## Deliver the review

Lead with findings, ordered by severity. Use this shape:

```text
[P1] Imperative, specific title — path/to/file.ext:line
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

If no qualifying findings remain, say so plainly. State what was inspected and any residual test or comprehension gap; do not invent a concern to make the review look useful.

## Preserve accountability

Recommend an approval state only when the evidence supports it. Require an explicit human checkpoint for expensive or hard-to-reverse decisions such as architecture, security boundaries, destructive migrations, billing, compliance, and public compatibility. Make the uncertainty and owner decision visible; never imply that tool output has accepted the consequence for them.
