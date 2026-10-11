---
name: code-review-craft
description: Review code changes or implemented subsystems for evidence-backed defects and code-health risks. Use for code-bearing PRs, diffs, commits or explicit code audits; do not invoke merely because a request says review, concerns Skill instructions, documents, research or plans, asks only for a code explanation, or involves implementation. Do not implement fixes unless requested.
---

# Code Review Craft

Reconstruct behavior, test the important risks, and judge the evidence. Automate collection, not accountability. The target is net code health—not comment count, perfection or personal taste.

## Route the task

- **Scope gate:** use this skill only when the requested work is code review. Review wording, a repository location or a PR wrapper alone is insufficient. Reviewing Skill instructions, prose, research logic, plans or a conceptual architecture is not code review; auditing a Skill's executable scripts or an implemented software architecture is. For mixed tasks, apply this skill only to the code-review portion.
- **Understand code within a review:** trace purpose, execution, state, invariants, side effects and failure behavior. For unfamiliar or cross-file systems, read [comprehension protocol](references/comprehension-protocol.md). A standalone code explanation does not trigger this skill.
- **Review a diff, PR or subsystem:** use the relevant dimensions in [review rubric](references/review-rubric.md). Follow the behavior beyond changed lines where compatibility, trust, concurrency, persistence or recovery depends on it.
- **Large/mixed changes, stacked work, author collaboration or disagreement:** additionally read [review flow](references/review-flow.md). A small coherent review does not need that process adapter.
- **Train judgment or Calibrate review or merge autonomy:** read [judgment training](references/judgment-training.md); preserve predictions, errors and revision-linked verification by task class. Do not require a training ledger for ordinary reviews.

## Establish the contract and reconstruct the behavior

Recover intent, base revision, acceptance criteria and protected properties from the request, callers, tests, schemas, docs and history. Do not invent requirements.

Calibrate depth to consequences and reversibility. Auth, billing, migrations, concurrency, destructive operations and public APIs deserve closer scrutiny than formatting; use actual lifecycle and workload, not hypothetical scale.

Check that the description matches the diff and that the change is a coherent, independently safe step with relevant tests. If mixed churn or breadth prevents reliable review, state the coverage limit and suggest concrete split boundaries. Do not simulate whole-change approval.

Inspect the load-bearing design early, then every assigned line in a logical order. Trace inputs through state transitions to outputs, side effects, cleanup and recovery; check ownership, trust, malformed inputs, retries, partial success, interruption, concurrency and compatibility where relevant.

Before relying on a green suite or author explanation, identify the strongest plausible broken invariant or downstream effect and evidence that would disprove it. Revise the concern when evidence disagrees; keep forecasts only in training mode.

Before approval, be able to explain what the code does, why, what must remain true and how failures become visible. If a material step still depends on “the framework probably handles it,” inspect further or report uncertainty.

## Audit The Approval Argument

- Compare terms, units, defaults, boundaries and lifecycle across requirements, docs and implementation; matching words are not matching semantics.
- Run proportionate diagnostics, tests or minimal reproductions and connect their full output to the claim.
- Tests support the cases they exercise, not the completeness of the contract or the safety of untested paths.
- Treat changed documentation and Quickstart examples as executable claims. A passing internal test does not validate a public journey with hidden setup.
- Try the strongest realistic counterexample before accepting a finding or verdict. State material residual uncertainty; neither author confidence nor reviewer consensus substitutes for acceptance evidence.

## Inspect structural cost

Check the states, branches, flags, wrappers, type escapes and boundaries introduced by a meaningful change. Look for an evidenced, behavior-preserving simplification to ownership, representation or control flow that removes concepts—not merely more files that relocate them.

The rubric covers scattered policy, duplicate canonical logic, pass-through abstractions, dependency cost, avoidable serialization and partially applied updates. Follow existing patterns unless evidence supports departing.

A structural finding needs a concrete maintenance or operational cost, repository evidence for a simpler direction, and the smallest safe migration/test boundary. File length and numeric thresholds are signals, not verdicts. A proven net-health regression can block even when tests pass; speculative rewrites or preferred style cannot.

Recurring required defects—or one high-consequence systemic failure—may justify a guard at the earliest maintainable layer. Keep that hardening opportunity separate unless the absent guard makes this revision unsafe; one example does not justify a framework.

## Decide what is a finding

Report only when all are supported:

1. A specific input, state or realistic sequence triggers the problem.
2. The current code permits the path.
3. The consequence matters to behavior, security, data, operations or maintainability.
4. Code, a reproduction, documented intent or an established invariant supports the claim.

Try to disprove each finding; drop speculative complaints, duplicate symptoms and unrelated pre-existing issues unless the change activates them. Missing validation is not proof that behavior is broken.

Assign severity by impact and likelihood, uncertainty separately:

- **P0:** active or near-certain catastrophic loss, compromise or outage.
- **P1:** likely severe security, data, availability or core-function failure.
- **P2:** meaningful regression or failure under realistic conditions.
- **P3:** limited edge-case defect or concrete maintenance/operational debt.

Distinguish **Required** corrections from **Optional / Consider**, **Nit** and **FYI** comments. P0–P3 defects normally require correction; do not disguise an optional preference as P3. Repository standards and technical evidence outrank taste. Accept an author's choice among equally valid approaches.

## Deliver the judgment

Lead with findings ordered by severity. Each needs a specific title, narrow file/line location, trigger, consequence, supporting evidence and smallest safe fix direction. Use only enough structure to make it actionable; do not implement a proposed fix unless asked.

Add only relevant assumptions, decisive test results, unreviewed scope or residual risks. Include a system explanation when requested, and label nonblocking comments explicitly. A review with no qualifying findings should say so plainly, not manufacture criticism.

For a PR, end with one calibrated state:

- **Approve:** no required concern remains; system health improves or is safely preserved.
- **Approve with comments:** only explicitly nonblocking comments remain.
- **Request changes:** a required finding remains.
- **Blocked / needs specialist:** coverage or evidence cannot support a responsible verdict; identify what is missing.

Do not approve known net degradation merely because a change is urgent or costly to revise; do not demand perfection once the bar is met. Give early evidence-backed design/scope feedback for a large review, clearly marked preliminary rather than approval.

## Preserve authority and accountability

Review permits inspection and diagnostics, not source changes, merge or publication. Auto-merge is a task-class-specific privilege backed by revision-linked evidence, never a general entitlement. A technical verdict cannot accept a user-owned consequence; explicitly requested fixes may proceed through scoped verification without another approval gate.
