# Pre-Execution Grill And Readiness Gate

Use this gate only when an unresolved judgment or evidence gap could change scope, method, risk, or whether the work should proceed. A task category alone does not trigger it.

## Decide Whether It Is Needed

Use `Not required: <reason>` when the specification is accepted, behavior is directly observable, and no hidden decision is material.

Investigate readiness when one of these is material:

- the claim, comparison, pass/fail evidence, or data-generating process is unclear;
- cost, capacity, safety, irreversibility, or an external commitment could change the decision;
- a polished artifact or local metric could look successful without answering the real question;
- a domain owner retains judgment that cannot be recovered from code, documents, or data.

Set `Blocked` only when the next dependent action cannot proceed within existing authorization and bounded uncertainty. A missing fact is not automatically a user question: research it or make the cheapest authorized diagnostic the next node. A ready diagnostic does not authorize a later gated action.

Ask only for missing judgment that cannot be inferred safely, after useful independent work. End questioning as soon as the decisive uncertainty is bounded and continue the authorized task; readiness is not a request for another approval.

## Run The Grill

1. Name the decision that would change after a pass or fail.
2. Identify the one or two uncertainties capable of flipping that decision.
3. Define evidence that permits execution and evidence that stops or redirects it.
4. Put the cheapest belief-changing check before broad implementation.
5. Ask one consequential question at a time only when its answer can change the plan.

Do not turn the gate into a questionnaire. The stopping condition is decision readiness, not a quota.

## Readiness Contract

Every required gate records four core fields:

| Field | Meaning |
|---|---|
| Decision this work informs | Action changed by a pass or fail |
| Key uncertainty / hypothesis | Material uncertainty or falsifiable claim |
| Pass / fail evidence | Evidence that permits, kills, pauses, or redirects |
| Cheapest informative check | Smallest test that can change belief |

Add data quality, baseline, operational constraints, False-positive loop, or retained human judgment only when they are material to this decision.

Set readiness to `Ready` when the core fields are concrete, contradictions are bounded, and the cheapest informative check is the first relevant node.

## Keep Loops Informative

- Pre-register the verifier and stop condition.
- Name an independent checker and raw evidence path; maker self-report cannot close the loop.
- Keep the change slice smaller than what the verifier can localize, or strengthen the sensor before acting.
- Prefer a check that can disprove the idea.
- On reflection ask: “What new information changed the plan?”
- If nothing changed, stop local optimization and revisit the readiness contract.
- Treat a sound falsification as a successful research result.
