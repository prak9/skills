# Ablation And Component Attribution

Use when asking which component earns its cost, why a combination works, or whether a simpler system preserves useful behavior. Components can be model modules, data sources, losses, retrieval/memory stages, tools or instruction groups. Ordinary source research needs no ablation. Reuse the [controlled protocol](controlled-research.md) and existing harness/results; this guide does not require a new platform or exhaustive search.

## Choose The Question Before The Arms

| Question | Useful contrast | What it establishes within the tested scope |
|---|---|---|
| Does this deployed configuration rely on A? | Full system vs full minus A | Conditional removal effect with the other components present, not A's universal value |
| Does A help a simpler baseline? | Base vs base plus A | Incremental benefit at that baseline, not A's contribution inside every larger system |
| Do A and B complement or substitute for each other? | Base, A only, B only, A+B | Conditional effects and an interaction contrast on the chosen response scale |
| Is the mechanism specific to A? | A vs an interface-compatible simpler or resource-matched substitute | Narrows alternatives such as extra compute, capacity or access; substitution is not identical to removal |
| Can A be removed without meaningful harm? | Full vs simplified under predeclared quality margin and cost/risk limits | Non-inferiority/equivalence only if precision and design support it; an insignificant difference is not proof of no effect |

Define the response, direction, population, resource constraint and smallest practically important change. Full-vs-base alone measures a bundle. Sequential add-ons are order-dependent; full-minus-one effects are conditional and generally do not sum to total gain. Redundant components can each look removable while removing both fails. Do not infer a unique contribution allocation without defining and supporting that separate question.

## Make The Intervention Real And Comparable

Retain an arm matrix and inspect effective configurations/traces, not just flag names. Keep data/splits, tools, evaluator, stopping/selection rules and relevant versions comparable. No arm may edit acceptance tests, secrets, required permissions or platform safety constraints. Instruction ablations operate on optional task-method content inside those shared boundaries.

Check dependency validity before running: if B consumes A's output, deleting A may only break B's input contract. Use a documented valid bypass/substitute or compare a dependency group; state what changed. Broken execution is an operational result, not a numerical estimate of model quality. Record it separately rather than dropping it or treating it as zero.

Name the intervention stage. Masking a feature/module at inference tests reliance of an already-trained system and may create a distribution shift. Retraining without it tests a different learning setup; retuning adds an adaptation opportunity. For a fixed-setting mechanistic comparison keep tuning fixed; for best-achievable-system comparisons grant comparable declared tuning opportunities and report their cost. Do not give only the preferred arm extra rescue tuning.

Removing a stage may change tokens, latency, data volume, capacity or rollout length. If the question is deployable total value, include those changes in the outcome. If claiming a specific mechanism, add a justified resource/control comparison where feasible; equal ceilings alone do not equalize consumed compute. Data-mixture ablations must specify replacement versus deletion and resulting total exposure. Report the unseparated explanation when a suitable control is unavailable.

## Cross Suspected Interactions

For two binary components, let `y00`, `y10`, `y01`, `y11` be comparable response estimates for base, A, B and A+B. Retain the original metric and direction.

- A without B: `y10 - y00`; A with B: `y11 - y01`.
- Interaction contrast on this response scale: `I = y11 - y10 - y01 + y00`.
- For a higher-is-better metric, positive I indicates greater-than-additive response on this scale; it is not automatically a mechanistic explanation or statistical significance. Coefficients from a differently coded regression can have a different scale.

The [worked report](../examples/ablation/report.md) uses hypothetical scores 60, 62, 63 and 75. A's conditional differences are 2 and 12 points; I is 10 points. This arithmetic illustrates a possibility, not measured performance. On probability, log-odds or another response scale, the interaction can differ; choose the scale for the intended claim, not after seeing which looks impressive.

Choose the smallest design that distinguishes the live rivals. Full binary factorials require `2^k` configurations before repetitions; do not enumerate them by default. Group dependent components, screen candidates and investigate plausible pairs. Fractional designs can reduce runs but alias effects: declare which effects cannot be separated and the assumptions used. With missing cells or inadequate budget, report the unidentified contrast instead of imputing the desired result. No default number of arms, seeds or spending is imposed.

## Control Noise And Selection

Use comparable task IDs, folds or time/regime blocks when appropriate, randomize/interleave run order where feasible, and isolate mutable memory, caches and artifacts that would contaminate arms. Pair runs when genuinely comparable; the same seed does not guarantee the same trajectory after a structural change. Deterministic replay checks implementation but repeated copies of one fixed run are not independent evidence.

Retain the independent sampling unit. Tokens from one trajectory, overlapping time windows or many grades of one answer do not become independent repetitions. Report paired differences, subgroup/tail failures and uncertainty supported by the data. When only aggregate scores exist, do not invent paired intervals or claim statistical separation. Choose repeats for consequential precision under the actual budget, not a ritual seed count.

Fix primary contrasts and practical margins before confirmation. Exploration may screen many arms; preserve failed/unselected attempts and confirm selected changes on untouched tasks/periods or a justified independent sample. Multiple comparisons and adaptive stopping weaken naive significance claims. A noisy null leaves the contribution unresolved; safe simplification needs the declared harm margin and guardrails, not merely `p > 0.05`.

## Deliver A Decision About The Component, Not Just A Ranking

Use the existing experiment report: question/estimand; arm matrix and actual changes; intervention stage, resources and tuning; raw observations and failures; conditional effects/interactions with supported uncertainty; quality, tail-risk and cost tradeoffs; keep/remove/revise/unresolved with scope and confirmation status. Distinguish a cheap mechanism probe from a deployable improvement. Do not require a production experiment when a sandbox can answer the question, or authorize deployment from an offline pass.

Verification basis and a source-backed explanation are in the worked report. Classical factorial/blocking principles guide the design; they do not by themselves validate an Agent intervention, causal mechanism or production benefit.
