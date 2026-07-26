# Probabilistic Judgment

Use this discipline to turn intuition into a forecast that can be updated, acted on, and calibrated. Do not add numbers merely to make a judgment look rigorous.

## Contents

1. Make the forecast resolvable
2. Anchor the prior
3. Update without counting evidence twice
4. Separate probability, uncertainty, and confidence
5. Convert belief into a decision
6. Score calibration and resolution
7. Use meta-models carefully
8. Compact forecast record

## Core Loop

```text
Reference class → prior → evidence → posterior range
→ payoff and action threshold → outcome → score → model update
```

A probability earns trust only when it has a defined target, resolves against observable evidence, changes an action, and survives repeated scoring.

## 1. Make The Forecast Resolvable

Write the claim so another person can settle it without interpreting your intent:

- define the event and threshold
- set the deadline
- name the source of truth
- specify edge cases before the result

Replace `AI adoption will accelerate: 70%` with a measurable event such as `By date D, metric M reported by source S exceeds threshold T: 70%`.

Use a range when evidence cannot support a point estimate. Do not report `58%` when the honest state is `roughly 55–65%`.

## 2. Anchor The Prior

Start from the closest defensible reference class before using case-specific detail. Record:

- the base rate and sample behind it
- why this case belongs in that class
- important ways this case differs

When no stable reference class exists, widen the interval and lower the bet. Do not disguise ignorance with a neutral-looking `50%`.

## 3. Update Without Counting Evidence Twice

For each material observation, record:

- whether it is genuinely new
- which causal variable it informs
- whether it is independent of earlier evidence
- the direction and plausible magnitude of the update
- what observation would move the belief the other way

Update odds by evidence strength when a defensible likelihood ratio exists. Otherwise use a directional or interval update. Do not mechanically add percentage points.

Cluster correlated signals under their shared cause. A product launch, procurement increase, and supplier shortage may all express one demand cycle; counting them as three independent confirmations inflates confidence.

## 4. Separate Probability, Uncertainty, And Confidence

- **Probability:** chance of the defined event.
- **Uncertainty:** width or shape of the outcome distribution.
- **Confidence in the estimate:** quality and relevance of evidence supporting that distribution.

Do not create a free-floating confidence score. Give it a target such as conditional forecast error, probability of positive net return, prediction-interval coverage, or model-failure probability.

Treat intuition as compressed evidence only when trained on relevant, repeated cases with timely feedback. In sparse, adaptive, or one-shot domains, use it as a hypothesis and widen uncertainty.

## 5. Convert Belief Into A Decision

Evaluate the outcome distribution, not probability alone:

```text
Expected utility = Σ probability(outcome) × utility(outcome) − friction
```

Apply survival, rights, liquidity, correlation, and irreversibility constraints before optimizing expected value. Predeclare:

- the probability or expected-value threshold for action
- how size changes across probability ranges
- maximum loss
- evidence required to add, reduce, exit, or wait

If moving from `55%` to `70%` never changes action or size, the number may be decorative.

## 6. Score Calibration And Resolution

Timestamp the forecast before resolution. For binary events, use:

- **Calibration buckets:** among events forecast near 70%, how often did they occur?
- **Brier score:** `(forecast probability − outcome)^2`; lower is better.
- **Log loss:** use when false extreme confidence should be penalized heavily.
- **Resolution/sharpness:** check whether forecasts distinguish high- from low-probability events; always saying 50% can be calibrated but useless.

Use enough comparable forecasts before drawing conclusions. Review both aggregate calibration and slices by domain, horizon, regime, and confidence band.

After resolution, separate:

1. forecast-process quality from outcome variance
2. bad priors from bad evidence interpretation
3. model error from regime change
4. missing evidence from double-counted noise

Update the reusable causal or reference-class assumption, not just the last probability.

## 7. Use Meta-Models Carefully

For prediction systems, estimate conditional error or a predictive distribution rather than appending an undefined confidence layer:

```text
point forecast
→ conditional uncertainty / calibrated outcome probability
→ after-friction payoff distribution
→ tail and correlation limits
→ trade / no-trade and size
```

Validate the uncertainty or meta-model out of sample and by regime. Guard against target leakage, overlapping labels, selection bias, and a meta-model that merely relearns the base model's score.

For trading, include fees, slippage, adverse selection, latency, capacity, tails, and portfolio interaction. Hit rate alone is not expected value.

## Compact Forecast Record

```text
Resolvable event, deadline, and source:
World: small / large / mixed — why?
Reference class and prior:
Evidence for / against; dependence clusters:
Posterior range:
Evidence that would move it materially:
Outcome distribution and friction:
Action threshold, size, and maximum loss:
Resolution:
Score and calibration bucket:
Process error, variance, or regime change:
World-model update:
```
