---
name: research-craft
description: "Run rigorous, instrumented research as a controlled learning loop: choose consequential problems, form falsifiable hypotheses, design trustworthy evaluators, build reproducible harnesses, inspect raw evidence, keep durable experiment memory, and accept changes only through explicit gates. Use when planning or conducting research, choosing a direction, reading literature, designing experiments or evals, debugging models, iterating experimental code or quantitative/trading strategies, building agent harnesses or self-improvement loops, managing research logs, controlling overfitting and reward hacking, or improving research quality and speed."
---

# Research Craft

Treat research as a system for changing beliefs with evidence, not as idea generation or repeated execution.

```text
important question
  -> falsifiable hypothesis and prediction
  -> explicit research contract
  -> cheapest informative probe
  -> raw evidence and fixed evaluation
  -> accept / reject / revise
  -> durable memory and next bet
```

The governing principle is: **research speed is the speed at which you discover you are wrong without corrupting the evidence.** Optimize the whole loop for informative failure, reproducibility, and cumulative learning.

## Route the work

Choose the lightest mode that protects the claim:

- **Exploration:** map an unfamiliar problem, inspect raw material, compare explanations, and identify the next discriminating observation. Keep hypotheses provisional.
- **Controlled experiment:** compare a candidate against a baseline under a fixed protocol and explicit acceptance gates.
- **Artifact iteration:** edit code, prompts, rules, or configuration through a bounded propose-evaluate-accept loop. Freeze the evaluator before optimizing the candidate.
- **Agent or self-improving harness:** read `references/harness-engineering.md` before designing runtime control flow, persistent memory, context construction, subagents, permissions, or self-edits.
- **Quantitative or trading strategy:** read `references/quant-strategy-iteration.md` before changing a strategy, backtest, scorer, data split, promotion gate, or distributed experiment wrapper.

Do not force exploratory work into fake precision. Increase control as soon as the work makes a comparative, causal, performance, safety, or deployment claim.

## 1. Choose the question backward from the outcome

- State the outcome that should exist if the research succeeds; reason backward to the evidence and experiments needed to produce it.
- Ask Hamming's question: what is the important problem, and why are you not working on it?
- Name the one or two decisive unknowns. Avoid absorbing a fashionable problem without its reasoning chain.
- Define the decision the result will change. If no plausible result changes a decision, narrow or stop the work.
- Predict the result before reading the answer or running the experiment. Record the prediction so hindsight cannot rewrite it.

## 2. Write the research contract

Before a consequential run or edit, record the minimum contract:

```text
Objective and decision:
Hypothesis and mechanism:
Prediction and plausible rival:
Baseline or current champion:
Editable surface:
Frozen evaluator and data:
Splits / holdouts / sample floor:
Primary metric and guardrails:
Artifacts and ledger location:
Acceptance, rejection, and stop rules:
Human or permission checkpoints:
```

Match strictness to risk. A disposable probe may need only a hypothesis, expected observation, and note. A claim that can move capital, production, safety controls, or a benchmark needs the full contract.

Separate two kinds of work:

- **Candidate work** changes the idea being tested while the evaluator stays fixed.
- **Harness work** repairs data, scoring, orchestration, validation, or reproducibility. Label it explicitly, test it against replay anchors, then refreeze the protocol before comparing candidates.

Never optimize the candidate and redefine success in the same round.

## 3. Upgrade inputs and inspect reality first

- Read primary sources, original data, code, traces, and appendices before relying on summaries.
- Diversify beyond the current feed; use old and cross-field work to escape synchronized conclusions.
- Inspect raw samples by hand before building abstractions. Silent data or labeling errors often produce plausible but false theories.
- Shrink the problem until it is cheap: one batch, one trace, one symbol, one regime, one failing case, or one minimal reproduction.
- Tune the strongest honest baseline before claiming improvement.

## 4. Build only the harness the claim requires

Make evidence easy to produce and hard to counterfeit:

- Launch a run reproducibly from a recorded command and configuration.
- Snapshot data range, seed, dependencies, candidate ID, evaluator version, and output paths when they affect the result.
- Store authoritative artifacts, not only optimistic console summaries.
- Validate expected task counts, rows, keys, files, and failed cells before scoring.
- Preserve interruption-safe state in files: contract, run status, traces, diffs, decisions, and rejected attempts.
- Keep safety, permissions, secrets, holdouts, and the evaluator outside any self-editing surface.

Prefer inspectable files and deterministic rules over hidden memory or a large opaque framework.

## 5. Run one informative loop at a time

1. **Baseline:** reproduce the current champion and verify the harness.
2. **Diagnose:** inspect raw failures and identify one concrete weakness or uncertainty.
3. **Propose:** state one mechanism-level hypothesis and its expected observation.
4. **Probe:** make the smallest meaningful change or run the cheapest discriminating experiment.
5. **Observe:** collect the same metrics and inspect representative successes, failures, and tails.
6. **Compare:** evaluate against the baseline, holdout, guardrails, and replay anchors.
7. **Decide:** accept, reject, or revise using the predeclared rules; do not rescue a miss by changing the story after seeing results.
8. **Compress:** remove redundant rules, update the ledger, and state the next constraint or experiment.

Change one meaningful variable or rule family per round when attribution matters. Let most ideas die cheaply.

## 6. Gate claims, not just scores

Require the gates relevant to the claim:

- **Protocol integrity:** evaluator, data, split, costs, seed, and objective remained fixed during candidate comparison.
- **Baseline strength:** the candidate beats a tuned, reproducible baseline rather than a weak straw man.
- **Held-out confirmation:** validation or truth data vetoes promotion; repeated exposure is contamination, not free evidence.
- **Sample and uncertainty:** the effective sample supports the claimed precision; show ranges or sensitivity when it does not.
- **Raw-evidence check:** inspect actual failures, traces, trades, or outputs instead of trusting an aggregate alone.
- **Replay and regression:** preserve known useful behavior and unrelated passing cases.
- **Mechanism and simplicity:** prefer smooth, legible, causal or economic explanations over fragmented exceptions.
- **Anti-Goodhart:** check whether the candidate learned the judge, leakage, artifact format, or benchmark quirks instead of the objective.
- **Operational validity:** account for execution friction, capacity, latency, permissions, maintainability, and downstream ownership.

If a required gate fails, reject the claim even when the headline metric improves.

## 7. Turn every run into durable learning

Use the project's existing research log or control documents. Do not create a competing ledger when one already exists. Record failures immediately because memory preferentially keeps convenient evidence.

```text
run_id / date:
question and hypothesis:
prediction:
protocol and changed surface:
result and raw evidence:
baseline / holdout / guardrails:
decision: accept | reject | revise
failure attribution:
belief update:
reusable finding and next constraint:
```

Maintain three separations:

- Keep observations separate from interpretations.
- Grade process quality separately from outcome luck.
- Keep current context separate from durable memory; promote a lesson only when evidence justifies it.

## 8. Scale and publish after learning survives

- Spend more compute, data, capital, or autonomy only after the small version works and the protocol survives replay.
- Ablate until the component carrying the result is known.
- Re-run the strongest disconfirming test before promotion.
- Explain the work clearly enough that another person can reproduce the setup, understand negative results, and challenge the inference.
- Wander into adjacent fields when the current framing stalls; breadth is insurance against a saturated local optimum.
- Expose provisional ideas to trusted critics early enough that they can kill weak work cheaply.
- Publish useful tools, replications, and explanations when permissions allow; clear writing exposes research debt and attracts better criticism.

## Decision-first handoff

End substantial work with:

```text
Decision and confidence:
Crux / decisive evidence:
Protocol and baseline:
Accepted and rejected changes:
Held-out, sample, replay, and artifact status:
Known failure modes and limits:
Durable findings written:
Next cheapest discriminating experiment:
Required human checkpoint:
```

Do not call work successful when artifacts are missing, the evaluator moved, a holdout was tuned against, or the result cannot change a decision.

## Sources

The general craft draws from Hamming, Schulman, Shannon, Feynman, Karpathy, Ng, Sutton, Olah, and the full Chinese source in `references/how-to-be-good-at-research-zh.md`. The harness adapter distills Lilian Weng's harness-engineering framework. The quantitative adapter combines fixed-evaluator auto-research with observable failure learning and anti-overfitting trading practice.
