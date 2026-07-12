---
name: iterate-trading-strategy
description: Run disciplined quant/trading strategy iteration with one declared editable strategy surface and one fixed evaluator/orchestrator. Use when optimizing, debugging, or auditing trading strategies with files such as strategy.py/backtest.py, exp/distributed evaluation wrappers, fixed scalar or gate-based scores such as Sortino or held-out simulated dret, pre-registered train/validation/verify/truth splits, replay checks, experiment ledgers, anti-overfitting gates, market-rationale filters, sample-size thresholds, and strict accept/reject decisions.
---

# Iterate Trading Strategy

Use this skill to turn strategy improvement into a controlled experiment loop. The core contract is:

```
declared strategy surface (one variable, rule family, config arm, or strategy.py)
  -> backtest.py (fixed evaluator/orchestrator: data, fills, costs, scoring, collection)
      -> may call the project's distributed runner, such as python -m exp
  -> fixed score/report (project score, e.g. Sortino or held-out simulated dret gate)
```

Optimize the strategy, not the scoreboard. Once the evaluator wrapper, data slice, cost model, score, random seed, split protocol, distributed manifest, and artifact collection logic are fixed, treat them as immutable unless the user explicitly asks to design or repair the evaluation harness.

## Method Roots

- **Karpathy auto-research:** freeze the evaluator and allow edits only to the single program being optimized.
- **Learning Beyond Gradients / heuristic learning:** keep failures observable; let the agent absorb failed experiments, patch code, rerun tests, replay history, and compress redundant rules into a maintainable evolving system.

The synthesis: make every strategy edit a small, ledgered experiment against a fixed evaluator.

## Project Control Docs

If the repo has research control docs such as `docs/research/program.md`, `docs/research/tasks/TASK-*.md`, and `docs/research/memory.md`, they are the experiment contract. Before running or editing anything:

- Read the current program status, active node, locked constraints, and task package.
- Use the task's experiment category, verification matrix, escalation rules, and writeback requirements.
- Do not invent a parallel ledger. Write run freezes, findings, failures, and task status where the project says they belong.
- User-owned gates such as truth lockboxes, production replacement, trading-mode changes, or RISK candidates entering sim must stop at the task checkpoint for approval.

## Freeze The Protocol

Before modifying code, identify and write down:

- The only editable strategy surface: a file, config arm, parameter family, keep-file, or offline rule family. Use the project's task package when it declares this.
- The fixed evaluator command, commonly `python backtest.py ...`. In distributed projects, `backtest.py` may be a wrapper that launches `python -m exp`, waits for completion, collects registry/artifacts, runs the scorer, and emits the final report.
- The fixed objective or gate. If the project already uses a score or promotion gate, keep it.
- The fixed data range, symbols, transaction costs, slippage/fill assumptions, and random seed.
- The split protocol: train/validation, screening/verify/truth, or the repo's named holdouts.
- The minimum effective trade count, power floor, or sample-size rule.
- The replay checks, artifact validators, and old behaviors that protect existing capability.
- The current champion metrics and commit/diff state.

If any part of the evaluator is missing or unstable, first make the evaluation protocol explicit. Do not start parameter search while the score can still move because the harness moved.

## Fixed Evaluator Wrapper

`backtest.py` is allowed to be an orchestrator, not only a local backtest. It may dispatch distributed jobs and summarize their outputs, but it must behave as a frozen evaluator:

- Accept only predeclared candidate/config inputs. Do not let it change data ranges, costs, scoring formulas, split definitions, or search spaces per candidate.
- Write a manifest/config snapshot before launch: candidate ids, worker pool, data window, cost model, seed, expected task count, output paths, and scorer command.
- Launch the distributed runner in the project's standard way, for example `python -m exp`, and keep all artifacts under a task-specific namespace.
- Collect results from authoritative artifacts, not from optimistic logs alone. Verify expected task counts, row counts, unique keys, parameter snapshots, and missing/failed cells.
- Run the fixed scorer, such as `analyze/promotion_gate.py`, and emit both machine-readable output and a concise human report.
- If collection or validation fails, return failure and preserve logs. Do not silently rescore, widen the grid, drop arms, or reinterpret the split.

Changing `backtest.py`, scorer code, distributed config generation, or artifact validators is harness work. It is allowed only when the task is explicitly harness/diagnostic work or the evaluator is broken; label it as such and verify it with focused tests or replay anchors before using it for optimization.

## Iteration Loop

Run each round as one disciplined experiment:

1. **Probe:** run the frozen evaluator on the current champion and record baseline train, validation, full-sample, trade count, and drawdown diagnostics.
2. **Diagnose:** locate a concrete weakness: regime, symbol, time window, entry condition, exit condition, cost sensitivity, drawdown cluster, low trade count, or replay regression.
3. **Propose:** state one economic hypothesis in one sentence. It must name the market mechanism, not just the code change.
4. **Patch:** edit only the declared strategy surface. Change one meaningful variable, config arm, or rule family per round.
5. **Evaluate:** run the same fixed evaluator and collect the same metrics.
6. **Replay:** confirm important old behaviors were not broken. Check representative trades, regimes, or tests that define prior capability.
7. **Decide:** keep only candidates that pass all acceptance gates. Revert rejected candidates cleanly.
8. **Compress:** remove redundant special cases introduced by accepted work and record the result in the experiment ledger.

Do not bundle multiple unproven ideas in one patch. If the result improves, you need to know why. If it fails, you need the failure to teach something reusable.

## Acceptance Gates

Accept a candidate only when all gates pass:

- **Fixed-evaluator gate:** no changes to evaluator, data source, costs, scoring formula, split, or seed.
- **Split-confirmation gate:** the repo's declared holdout protocol must confirm the result. If the project uses train/validation, both must avoid deterioration. If it uses screening/verify/truth, treat verify/truth as vetoes, not tuning signals.
- **Gap gate:** reject large in-sample vs out-of-sample divergence. If no project threshold exists, treat a train jump with flat or worse holdout performance as overfit until proven otherwise.
- **Market-rationale gate:** every accepted rule must have a simple market explanation. Reject fragmented exceptions that only fit history.
- **Shape gate:** prefer monotonic, continuous, and economically smooth rules over jagged discrete sets. For example, "avoid chasing after more than N consecutive up days" is admissible; "skip exactly {2, 5} up days but allow 3 and 4" is curve fitting.
- **Sample-size gate:** reject candidates whose effective trade count falls below the predeclared minimum.
- **Replay gate:** reject candidates that improve the headline score by breaking known useful behavior.
- **Simplicity gate:** reject precision that has no market reason, such as a threshold tuned to 8.2% when a robust band or rounded level has the same logic.

If the validation set has been consulted across many rounds, say so. Repeated validation exposure contaminates it; require a fresh out-of-sample check before making strong claims.

For the Ridge HFT research repo specifically, map these gates to the project contract:

- **EDGE candidates:** promotion is paired held-out simulated `dret`, with `avgnwt` as the second north star; use `promotion_gate.py`, four-layer detail, relative deltas, search-count accounting, and regime balance.
- **RISK candidates:** do not enter sim/verify until offline ledger oracle, adverse-fill stress, and M0 decision metrics are ready. Judge deployable money with the task's `M` proxy, not headline `dret` alone.
- **Diagnostic/audit tasks:** do not promote. Freeze the measurement contract, validate artifacts, produce the map/report, and route high-gradient findings into a new pre-registered task.
- **Truth lockbox:** never use truth for exploration or tuning. Pre-register first, get required approval, consume the one allowed peek, then record the result without iterative retries.

## Ledger

Record every round, including failures. Use or create the repo's existing experiment log; otherwise add a compact section to the working notes requested by the user. Each entry should include:

```
round:
  champion:
  task_or_run_id:
  hypothesis:
  market_rationale:
  changed_variable:
  patch_summary:
  train_score:
  validation_score:
  train_validation_gap:
  trade_count:
  replay_result:
  artifact_validation:
  decision: accept | reject
  failure_attribution:
  compression:
  next_constraint:
```

Failure attribution matters more than the failed score. Preserve why a candidate failed: overfit gap, no market rationale, too few trades, replay breakage, costs sensitivity, unstable regime, or implementation bug.

## Operating Rules For Codex

- Inspect the repo first; discover the strategy file, evaluator command, tests, and prior logs before editing.
- State the frozen protocol before the first patch.
- Use existing project commands and style. Do not invent new infrastructure unless the evaluator is absent or unreproducible.
- Touch only the declared editable strategy surface during optimization. If a support file must change to fix a bug or make evaluation reproducible, call that out as harness work, not strategy optimization.
- Prefer small diffs with clear economic meaning.
- Revert rejected candidates without disturbing user changes or unrelated files.
- End with a decision-first summary: accepted/rejected, champion metrics, holdout behavior, trade count, artifact validation, replay result, and what the ledger learned.

## Source

Distilled from a methodology combining Andrej Karpathy's auto-research constraint (fixed evaluator + single editable program) with Jiayi Weng's heuristic-learning view from _Learning Beyond Gradients_: observable failures, code edits, experiments, replay, history, and rule compression can turn heuristics into an evolving system.
