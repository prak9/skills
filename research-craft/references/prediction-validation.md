# Probability Forecasts And Stochastic Simulators

Use for event probabilities, predictive distributions or stochastic process simulations. Load only for those tasks; ordinary deterministic arithmetic, point-regression diagnostics and descriptive reports do not require this protocol.

## Freeze The Forecast Question

Define the event and exclusions, population/selection rule, forecast origin, horizon and resolution source. Separate states known at the forecast origin from future states that must be predicted or integrated over. Record when each feature, derived aggregate and annotation actually became available, not only its row's nominal date.

An attempt-level success probability conditional on a known distance is not a pre-event probability that an opportunity will arise and succeed. Selected completions cannot stand in for all opportunities. Predict actors' actual policies rather than silently replacing them with theoretically optimal behavior. State the dependence assumptions connecting opportunities, choices and outcomes; a product formula is not evidence of independence.

Fit preprocessing, feature selection, hyperparameters and probability calibration only within the training/validation protocol. Match chronological splits to the deployment question; keep related episodes such as one match or overlapping label windows from leaking across folds, with grouping, purge/gaps where needed. Historical aggregates must be as-of the forecast time. A test set used for adaptation is no longer untouched confirmation.

Compare models on the same event, forecast origin, usable information, evaluation population and scoring rule. Start with a relevant historical-rate or simple direct-prediction baseline. A process simulator must earn its extra cost through predictive improvement or a separately requested process capability; do not force a full simulator when a direct model answers the task.

## Separate Three Claims

| Claim | Evidence required |
|---|---|
| Implementation correctness | Formula/state invariants, boundary tests and reproducible outputs |
| Predictive usefulness | Frozen-pipeline performance against a defensible baseline on unused comparable data, with uncertainty |
| Decision value | Improvement under contemporaneously available prices, costs, constraints and execution conditions |

Passing one level does not pass the next. A prediction-only task can finish with a supported improvement or no demonstrated improvement; it need not discover a profitable strategy. Do not invent historical executable prices or extend the user's authority to satisfy an economic claim.

## Score Probabilities, Not Just Decisions

- Compare proper probability scores such as Brier score or log loss against the baseline, plus calibration/reliability and discrimination/resolution. State clipping or other numerical conventions if used; do not silently repair impossible predictions or invalid probabilities.
- A constant base-rate forecast can be calibrated while providing no discrimination. A lower Brier score does not by itself prove better calibration; it combines several aspects of predictive quality.
- Report sample counts and uncertainty in calibration groups. Select relevant groups before confirmation; post-hoc subgroup discovery needs fresh evidence. Account for clustered or dependent observations rather than treating every row as independent.
- Small perfect samples do not justify probabilities of exactly one. Consider an appropriate prior, shrinkage or partial pooling when supported; no particular algorithm is mandatory.
- A few hand-assigned scenario weights are not an empirically calibrated forecasting system. A single outcome cannot establish whether a probability was calibrated.

## Check The Simulated Process

Before judging a simulator adequate, choose a small set of use-relevant predictive checks: counts, durations, zero-event frequency, dispersion, tails, event ordering, serial dependence and conditional behavior. Compare generated data with observed data on the same basis, not just their means or aggregate payoff.

For trading, matching average P&L can hide wrong trade counts, holding times or loss clustering. Check those paths when they carry the claim. A process check may expose misspecification but cannot prove a unique mechanism; checks against fitting data do not replace held-out prediction evaluation. Keep evaluator repairs separate from candidate improvement and refreeze before comparison.

## Separate Uncertainty Sources

| Source | What can address it |
|---|---|
| Monte Carlo sampling error | More effective simulations or appropriate variance reduction under the fixed model |
| Parameter uncertainty | Relevant data, justified shrinkage, parameter/posterior sensitivity with dependence preserved |
| Structural misspecification | Rival mechanisms, boundary cases, predictive checks and fresh evidence |

For independent Bernoulli simulations under fixed parameters, the estimated Monte Carlo standard error is `sqrt(p_hat * (1 - p_hat) / N)`. At `p_hat = 0.5, N = 100000`, it is about 0.158 percentage points. This describes numerical estimation under the model, not real-world probability accuracy. Correlated draws need dependence-aware effective precision; near-zero/one estimates require care rather than claiming zero uncertainty from no observed failures.

Distinguish these estimation errors from inherent outcome randomness, which can remain even under a correct, known model. More simulations are not more independent observations of reality. Arbitrarily chosen input distributions or independence assumptions do not become supported investment probabilities through repeated sampling.

## Handoff

Report the event and information boundary, strongest baseline, unused-data status, relevant score/process checks, dominant uncertainty and supported claim level. Keep unresolved links visible; do not require a positive result, new framework or economic proof to finish a narrower request.

## Sources

- [scikit-learn probability calibration](https://scikit-learn.org/1.8/modules/calibration.html): proper scores, reliability and discrimination.
- [Stan predictive checks](https://mc-stan.org/docs/2_38/stan-users-guide/posterior-predictive-checks.html): compare replicated and observed process features.
- User-supplied sports-modeling example: forecast origins, process decomposition and the distinction between numerical precision and model validity. The training schedule and named algorithms are not mandatory skill steps.
