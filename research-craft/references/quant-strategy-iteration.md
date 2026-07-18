# Quantitative Strategy Research Adapter

Read this adapter before optimizing, debugging, or auditing a quantitative or trading strategy. Follow the core research loop in `SKILL.md`; apply the stricter controls here because market data is adaptive, noisy, autocorrelated, and unusually easy to overfit.

## Strategy research contract

```text
one declared editable strategy surface
  -> frozen evaluator / backtest orchestrator
  -> authoritative artifacts and fixed score or gate
  -> holdout, replay, sample, cost, and market-rationale checks
  -> accept or reject with an experiment ledger
```

Optimize the strategy, not the scoreboard. Freeze the evaluator wrapper, data window, universe, costs, fill model, score, seed, split protocol, distributed manifest, and artifact collection before candidate search.

If the repository has control documents such as `program.md`, `TASK-*.md`, `memory.md`, run logs, or promotion records, treat them as the contract. Read the active task, locked constraints, escalation rules, and writeback locations. Do not create a parallel ledger.

## Freeze the protocol

Record:

- the only editable file, config arm, parameter family, keep-file, or rule family
- the evaluator command and whether it dispatches distributed jobs
- primary objective, veto metrics, and current champion
- data ranges, symbols, fees, slippage, fill assumptions, seed, and dependencies
- train/validation, screening/verify/truth, walk-forward, or other holdout protocol
- minimum effective trade count or statistical power floor
- replay anchors and prior capability that must remain true
- artifact manifest, expected tasks/rows/keys, and scorer command
- approval gates for truth data, production replacement, or live/sim trading changes

When the evaluator is missing or unstable, repair and verify it as harness work. Refreeze it before strategy comparison.

## Keep the evaluator authoritative

An evaluator such as `backtest.py` may orchestrate distributed jobs, but it must:

- accept only predeclared candidate inputs
- snapshot candidate IDs, worker pool, data, costs, seed, expected tasks, outputs, and scorer
- launch through the project's standard command
- collect authoritative artifacts rather than trusting success logs
- validate task counts, rows, unique keys, parameter snapshots, missing cells, and failed work
- emit machine-readable results plus a concise decision report
- fail visibly when collection or validation fails

Do not silently rescore, widen a grid, remove failed arms, change a split, or reinterpret the objective after results arrive.

## Map the core loop to market research

1. **Baseline:** reproduce champion train, validation, full-sample, trade count, drawdown, cost, and regime diagnostics.
2. **Diagnose:** locate one weakness by regime, symbol, time, entry, exit, cost sensitivity, drawdown cluster, sparse sample, or replay failure.
3. **Hypothesize:** state the market mechanism in one sentence, not merely the code change.
4. **Patch:** change one meaningful variable, config arm, or rule family in the declared surface.
5. **Evaluate:** run the identical evaluator and collect identical metrics and artifacts.
6. **Replay:** check representative trades, regimes, and behaviors that encode prior capability.
7. **Decide:** retain only candidates that pass every predeclared gate; revert rejected candidate edits without disturbing user work.
8. **Compress:** remove redundant exceptions and write the causal lesson to the ledger.

## Mandatory promotion gates

- **Frozen protocol:** no candidate-time changes to evaluator, data, cost model, score, split, or seed.
- **Holdout confirmation:** treat verify/truth as vetoes, not tuning signals. Disclose repeated validation exposure and require fresh out-of-sample evidence when contaminated.
- **Generalization gap:** reject a train jump with flat or worse holdout performance unless new evidence explains it.
- **Market rationale:** require a simple mechanism; code-only patterns are not a thesis.
- **Rule shape:** prefer monotonic, continuous, rounded, and economically smooth rules over jagged sets or false precision.
- **Sample floor:** reject gains created by shrinking effective trade count below the declared minimum.
- **Replay:** reject headline improvement that destroys known useful behavior.
- **Cost and execution:** stress fees, fills, latency, capacity, liquidity, and turnover at the level relevant to deployment.
- **Simplicity:** reject special cases whose only defense is historical fit.

## Ridge HFT project profile

When operating in the Ridge HFT research repository, map the generic gates to its existing contract:

- **EDGE candidates:** use paired held-out simulated `dret` for promotion, `avgnwt` as the second north star, `promotion_gate.py`, four-layer detail, relative deltas, search-count accounting, and regime balance.
- **RISK candidates:** require the offline ledger oracle, adverse-fill stress, and M0 decision metrics before sim/verify. Judge deployable money with the task's `M` proxy rather than headline `dret` alone.
- **Diagnostic or audit tasks:** do not promote. Freeze measurement, validate artifacts, produce the requested map or report, and route high-gradient findings into a new pre-registered task.
- **Truth lockbox:** never use truth for exploration. Pre-register, obtain the required approval, consume the allowed peek once, and record it without iterative retries.

## Strategy experiment record

```text
round / run_id:
champion and candidate:
hypothesis and market mechanism:
changed surface:
protocol snapshot:
train / holdout / gap:
trade count / drawdown / costs:
regime and sensitivity:
replay and artifact validation:
decision: accept | reject
failure attribution:
compression and next constraint:
```

Classify failures precisely: overfit gap, weak mechanism, insufficient sample, cost sensitivity, unstable regime, replay regression, artifact failure, or implementation bug. A failed score with useful attribution is research progress; an unexplained win is not.

End with the decision, champion metrics, holdout behavior, sample size, artifact and replay status, accepted/rejected change, and the ledger's new constraint.

Source: fixed-evaluator auto-research, observable failure learning, and disciplined quantitative validation practice.
