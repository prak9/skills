---
name: research-craft
description: 设计和评估可证伪的研究或 Agent Harness 实验，包括 Prompt、Skill、AGENTS、模型迁移、自我改进与自动化研究；用于需要固定基线、可观测证据和接受门槛的比较，不用于普通事实检索、一次性解释或仅需做选择的决策。
---

# Research Craft

Change beliefs with evidence. Find the uncertainty that matters, obtain the cheapest discriminating observation, and preserve what the result actually supports. Intuition and open-ended inspection can generate ideas; they do not validate them.

Optimize trustworthy learning, not experiment count, researcher count or hardware utilization. The workflow below supplies decision criteria, not mandatory forms, a fixed sequence or extra approvals.

## Choose the mode and reference

- **Exploration:** inspect unfamiliar material, follow clues and compare provisional explanations. No invented hypothesis, probability, baseline or permanent log is required before a cheap reversible probe.
- **Controlled comparison:** compare a candidate with an honest baseline under a fixed protocol. Freeze the evaluator before optimizing code, prompts, rules or configuration.
- **Results delivery:** for substantive comparisons, use [experiment reporting](references/experiment-reporting.md). Preserve configurations, raw evidence, metric deltas and supporting tables in the existing authorized result location. Ordinary checks need no report bundle.

Load specialist detail only when its condition applies:

| Condition | Reference |
|---|---|
| Ambiguous construct, unfamiliar mechanism, observational tie, consequential delay/feedback, or pressure-testing a research thesis | [Hypothesis formation](references/hypothesis-formation.md) |
| Evidence changes a load-bearing premise, dependent conclusion or current method | [Belief updates and route revision](references/hypothesis-formation.md#resolve-claims-without-rewriting-history) |
| Open research has a consequential coverage gap, one-sided sources or unresolved source disagreement | [Perspective discovery](references/perspective-discovery.md); not supplied-text summaries or narrow checks |
| Predictive-model inputs/timing, probability forecasts or stochastic simulators | [Prediction validation](references/prediction-validation.md) |
| Recurring failure, regression or diminishing optimization returns | [Trace attribution](references/trace-attribution.md) |
| Instructions change because the base model, harness or tools changed | [Instruction migration](references/instruction-migration.md) |
| Agent runtime, persistent memory, verification closure, permissions, self-edits or autonomy scaling | [Harness engineering](references/harness-engineering.md) |
| Parallel experiment design, research-team ownership, throughput or reusable discovery infrastructure | [Automated discovery](references/automated-discovery.md) |
| Repeated task-feedback experiments, sampling and data reuse | [Research flywheel](references/research-flywheel.md) |
| Strategy, backtest, scorer, data split, promotion gate or distributed trading experiment changes | [Quant strategy iteration](references/quant-strategy-iteration.md) |
| A claim about assisted performance, independent learning, retention or transfer | [Human-learning evaluation](references/human-learning.md) |

Reuse confirmed goals, budgets, permissions and project records. Implementation requests authorize scoped local work, not deployment or publication. Resolve discoverable gaps yourself; ask only for consequential user-owned choices, while progressing independent authorized work. Do not invent a budget when none was specified.

## Frame the question around the outcome

State what is being explained, predicted or compared, for which population/system and horizon, and what uncertainty the result should resolve. Clear requests proceed directly; use stated working assumptions for ordinary gaps.

Check the premise before explaining it: “why did the model fail?” may first require verifying failure against the intended metric and baseline. Preserve the user's objective rather than substituting an easier question. Explanation does not itself authorize action.

Name the decisive unknowns and plausible rivals, preserving interactions that could change the result. Before a consequential test, record its prediction and provenance so hindsight cannot rewrite it. A line of inquiry with no plausible effect on the requested outcome may be narrowed or retired without stopping unrelated work.

When training problem-selection judgment, preserve the dated opportunity portfolio, including unchosen alternatives, resolution horizons and sources of truth. Use `decision` for choosing real actions; research makes predictions resolvable. Do not add portfolio tracking to ordinary questions.

## Fix the comparison, not every exploratory step

For a consequential run, record enough to recover the claim, baseline, allowed changes, acceptance and evidence. Include only relevant fields: population and horizon; mechanism and rival; observed variables versus latent construct / model boundary; data, splits and source versions; metric and guardrails; command/configuration, artifacts and actual resource use. Honor an existing required schema rather than creating a parallel form.

Separate:

- **Candidate work:** change the tested idea under a fixed evaluator.
- **Harness work:** repair data, scoring, orchestration or reproducibility, check replay anchors, record the new version and refreeze before candidate comparisons.

Never redefine success to rescue the candidate in the same round. Exploratory combinations can find a direction, but attributing a gain to one component needs a discriminating comparison. Predeclare comparable search/tuning resources when claiming superiority; unequal trials, compute or human intervention limit attribution.

Candidate-generation filters are not final acceptance gates. If an early proxy may discard useful directions, inspect a proportionate sample of rejects or near-threshold cases. An unfamiliar candidate with a plausible mechanism and a cheap discriminating test can merit a probe; neither familiarity nor novelty establishes quality. Preserve missing evidence versus actual failure and reopening conditions; broaden discovery without weakening the frozen evaluator.

## Inspect reality and preserve the distinctions that matter

Start with primary sources, original data, code, traces and raw samples; summaries can hide labeling errors or assumptions. Operationalize concepts that determine inclusion, labels, metrics or causality. A convenient proxy is not automatically the claimed construct.

Judge a source by incremental information: a discriminator between explanations, missing coverage, an independent observation or better measurement. Different publishers may repeat one observation, share selection bias or describe outdated conditions. Diversify into old or cross-field work when the current feed or framing is saturated, not merely to increase source count.

Shrink the test to a batch, trace, symbol, regime or minimal failure that can discriminate the current uncertainty. Tune the strongest honest baseline before calling a candidate better.

### Check what simplification preserves

If abstraction carries the conclusion, examine a contrastive pair: cases treated as equivalent that could require different predictions or actions. Use observed cases or labeled hypotheticals, not forced distinctions. Preserve relevant outcomes, timing, constraints, interactions and evidence. A payment that never executed differs from one that committed but lost its response; unconditional retry cannot erase that distinction.

A proof of redundancy within a defined domain can justify permanently omitted work. Historical non-use supports only conditional deprioritization with recoverable provenance and reopening conditions. For algorithm reformulation, pruning, state merging or penalty relaxation, use [structural optimization](../performance/references/structural-optimization.md); check original outputs and constraints, not just a scalar score. An approximation, bound or sampled pass is not exact equivalence.

For learned inputs, consult [representation and availability](references/prediction-validation.md#test-the-input-representation); for memory, [history and noise](references/harness-engineering.md#test-state-through-decisions); for historical/cross-domain data, [conditional data value](references/research-flywheel.md#test-the-incremental-value-of-data).

Keep the simpler model when it preserves the required distinctions; add only what an evidenced failure requires. Fewer concepts, a fixed variable count or a hand-picked pair proves neither quality nor generality. Transfer an analogy only after checking its load-bearing mechanism and boundaries.

## Run the cheapest informative test

Judge a probe by decision-relevant evidence gained relative to its full cost, not subjective confidence gained. Discovering a missing mechanism or unreliable measurement can usefully increase uncertainty; unrelated information gain does not justify a detour.

Choose the probe for the uncertainty:

- Missing facts or suspect measurements: inspect sources or instrumentation.
- Competing mechanisms with the same observations: seek a discriminating comparison.
- Imprecise parameters: obtain comparable observations or examine sensitivity.
- Changed conditions: revisit the model boundary and structural-break evidence.
- Remaining outcome randomness: report predictive ranges or robustness where supported, not endless reading. A failed search alone does not establish irreducibility.

A controlled round usually reproduces the baseline, diagnoses a weakness, states a testable prediction, makes a bounded change, collects comparable evidence, then accepts/rejects/revises. Reorder or combine discovery work as useful. Change one meaningful variable or rule family when causal attribution matters; let weak ideas die cheaply.

Build only the harness needed for the claim. Record commands and material inputs, seeds, versions and configurations; validate expected tasks, rows, keys, files and failed cells before scoring. Preserve raw artifacts and interruption-safe state for consequential runs, including rejected attempts. Keep safety, permissions, secrets, holdouts and the evaluator outside candidate self-edits.

[run_experiment.py](scripts/run_experiment.py) can capture local command runs, separate artifact grading and elapsed time. Reuse an existing capable harness when available. Its receipts do not attest to hidden holdout isolation, nested agent behavior or model improvement. Prove the reach–act–observe–verify–recover path before multiplying workers or authority; record unresolved human-verification debt.

Route feedback by what it asserts: verify factual corrections against evidence; test causal diagnoses against plausible rivals; honor authorized preferences within their stated scope without treating approval as proof of correctness or utility. Mixed feedback may require all three. Tie a claimed defect to an artifact and criterion, seek counterevidence, and verify the correction plus relevant regressions. Consolidate repeated low-information comments instead of editing to please a reviewer. A legitimate goal or criterion change needs the applicable authority and a separately versioned comparison; a wrong evaluator is harness work. Neither can retroactively rescue a failed candidate. Local correction proves a local result, not persistent learning or transfer.

## Gate claims, not just scores

Apply the gates material to the claim:

- **Protocol integrity:** fixed objective, evaluator, data/split, costs and relevant seeds during comparison; declared selection/weighting surface when training data is the intervention.
- **Argument integrity:** supported premises, stable terms, valid inference and the strongest plausible rival considered.
- **Task completion:** original required scope reconciled with completed, permitted-deferred and unresolved items under the same denominator. Easy-subset scores cannot offset missing deliverables; explicit optional work does not block completion.
- **Baseline and confirmation:** tuned reproducible baseline; tuning/selection data separate from untouched confirmation. Repeated acceptance exposure is contamination, not independent evidence.
- **Sample and model validity:** effective independent sample supports precision; material measurement, interaction, feedback, stationarity and adaptation assumptions face plausible rival processes and breaks. Narrow or condition unsupported claims; do not manufacture uncertainty intervals.
- **Raw evidence and replay:** inspect actual outputs, failures and tails, preserve known useful behavior and unrelated passing cases.
- **Mechanism and anti-Goodhart:** prefer explanations to fragmented exceptions; test irrelevant-change stability and meaningful-change sensitivity where relevant. Neither smoothness nor a sharp jump alone proves generalization; check judge gaming, leakage and format shortcuts.
- **Operational validity:** include latency, execution friction, capacity, permissions, maintenance and downstream ownership as applicable. Added complexity must earn its benefit; neither isolated scores nor fewer lines establish improvement.

A failed gate rejects the claim, not automatically the whole task. Repair a recoverable measurement problem or revise the route within existing authority and resources, preserving rejected evidence. Stop at the verified requested outcome, exhausted agreed budget, user stop, or a real boundary requiring input/authority. When further feasible work cannot change the scoped judgment, deliver the supported answer and remaining uncertainty rather than inventing another experiment.

## Preserve and hand off the useful result

Use the existing log or control documents. Keep the question/prediction, exact changed surface and protocol, result/raw evidence, acceptance decision, belief update and consequential failure or reopening condition. Disposable exploration needs no separate permanent entry unless the active protocol requires it.

Keep observation separate from interpretation, process quality from outcome luck, and current context from durable lessons. Resolve the full declared opportunity portfolio at its horizon, including misses and unchosen winners, before inferring selection skill from one successful bet.

Scale compute, data, capital or autonomy only after bounded tests and replay support the change. Ablate when component attribution matters; use current disconfirming evidence before promotion, rerunning only when relevant changes or unresolved concerns invalidate it. Test transfer before generalizing. Expose ideas to critics and publish useful artifacts only within existing permissions.

End substantial work with the supported conclusion, decisive evidence and baseline, accepted/rejected changes, uncertainty and untested scope, and links needed to reproduce or challenge it. Include a next discriminating step or human decision only if genuinely unresolved—not as a compulsory extra round. Missing artifacts, moved evaluators, contaminated confirmation or an unanswered original question prevent a success claim.
