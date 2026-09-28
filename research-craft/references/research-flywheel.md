# Evaluation And Data-Driven Research Flywheel

Use for an authorized continuing research program, evaluation infrastructure or feedback-driven improvement. Reuse its goal, budget, storage and release authority. A single answer or ordinary fix can finish without a registry, experiment ladder or long-term monitoring.

## Optimize The Complete Learning Cycle

Treat lower cost and higher stability as capacity to test more discriminating hypotheses, including uncertain alternatives. Observe the path from question through data preparation, execution, verification and interpretation to a changed research decision. Diagnose the slowest consequential link before adding workers or reducing model size. Record fees, elapsed time and human effort separately; combine them only with a stated conversion.

Useful views are time to a supported decision, valid experiments versus execution/data/grading failures, total cost including rejected attempts, and best confirmed quality against cumulative budget/time. A valid negative can eliminate an important route; a timeout alone leaves its mechanism unresolved. Summed parallel run durations are resource consumption, not campaign wall time. Experiment count and hypothesis count are diagnostics, not standalone rewards.

Evaluate reusable infrastructure by construction/maintenance cost, plausible reuse, savings and evidence fidelity. Small deterministic checkers, replay fixtures, cached immutable inputs and interruption-safe execution can reduce repeated effort. Reuse a result only when its candidate, data, evaluator and material environment remain applicable. Fresh source discovery and live integrations need their own checks. Keep optional infrastructure out of unrelated delivery gates.

## Spend In Stages

| Stage | Question | Evidence and budget |
|---|---|---|
| Probe | Could this distinguish the leading explanations? | Cheap trace, counterexample, reduced dataset or replay; scope its limits |
| Comparison | Does the intervention help the target task? | Fixed protocol and comparable arms; use ablation or repetition when needed |
| Confirmation | Does the gain survive beyond selection? | Fresh cases, relevant regressions and appropriate uncertainty/cost checks |
| Field feedback | Does it help actual use? | Authorized sampling or shadow use, drift and delayed outcomes |

These are evidence levels, not mandatory approval stages. Check proxy-to-full ranking reversals and missed failure classes before using a cheap probe to discard whole directions. A short task cannot settle long-horizon reliability. Preserve capacity for exploration, independent replication and evaluator audits as trials become cheaper; adjust allocation from observed bottlenecks rather than universal percentages. More trials create more opportunities for a lucky winner, so keep search results separate from independent confirmation.

## Connect Existing Records

Use stable links at the grain the claim needs:

- **Case:** ID, source/provenance, task family, dataset version, sampling origin, exposure and applicable split. Keep original information cutoffs and outcomes hidden until their intended stage.
- **Run:** unique attempt ID, candidate/configuration and baseline links, case ID, stage, effective model/harness/input/evaluator versions, raw artifacts, execution status and captured costs. Retain unsuccessful attempts and exact versions, including relevant uncommitted changes.
- **Grade:** run/artifact identity, criterion and evaluator version, pass/fail/unresolved, evidence and grader scope. Independent process execution does not by itself establish calibrated semantic judgment.
- **Finding/change:** source runs and grades, supported mechanism or unresolved rival, intervention layer, applicability, confirmation and retirement/reopening conditions. Link to existing findings or commits rather than duplicating them.

This is a join contract, not five mandatory files. A compact JSONL index plus existing artifacts is sufficient; richer tables can evolve from demonstrated access needs. Plans own task state, packets own observations, and summaries are derived. Reconcile expected versus observed cases/attempts before any suite-wide claim. Inventory prose fixtures as designed but unrun until execution exists; keep static, artifact-replay and model-behavior coverage distinct. The command manifest accepts an optional `links` object for existing finding/change/baseline references; the packet supplies a run-linked grade ID and candidate fingerprint even if a display name is reused.

## Curate Data Without Teaching The Test

- Mine authorized product/user feedback, representative successes, failures, disagreements and clean negatives. Record how samples entered the collection; complaints alone do not describe the workload.
- Improvement data can oversample rare weaknesses. Keep representative evaluation weights fixed, and report challenge-set results separately. Split related task families, entities and time windows together when leakage is plausible.
- Track development, regression, confirmation, exposed and retired cases. Once a confirmation case or its outcome informs tuning, preserve it as development/regression and obtain fresh confirmation. A manifest's `unseen` label is a declaration, not access control.
- Keep holdouts and authoritative grades outside candidate-editable scope. Remove version/path identity hints from comparative judging where feasible, randomize answer order and retain ties/disagreement. Record residual exposure or order effects.
- Preserve source rights, retention boundaries and necessary redactions. Store observable actions and source evidence, not private reasoning, credentials or indiscriminate transcripts. A study request does not authorize external data export or publication.

## Validate The Evaluator

Separate deterministic correctness/integrity checks, rubric-bound semantic judgments and delayed external outcomes. Calibrate graders on known positive, negative and unresolved examples, including polished wrong answers and self-approval attempts. Inspect false acceptance, false rejection and affected task groups; agreement between models is not an oracle. Use expert adjudication where the criteria require it, without making every routine check a new human gate.

Freeze the judge before candidate comparison. Repair evaluator defects in a separate version, replay anchors and rescore both arms. Costs and tool actions should come from the harness or provider when available; label self-report and unknowns explicitly. A packet hash checks bytes and identity, not truth, semantic coverage or complete side-effect absence.

## Close The Loop At The Right Layer

Trace failure -> competing causes -> cheapest discriminating intervention -> preserved regression -> later comparable confirmation. Fix data, tests, tools, retrieval or state where those caused the failure; add a Skill rule when contextual judgment is the right enforcement point. Keep prior failures intact. An independently checked improvement can be useful within scope with its mechanism still unresolved; broader promotion needs transfer evidence.

Measure memory by whether a relevant finding improves a later decision at acceptable retrieval cost. Compare against an appropriate no-memory/current-memory baseline when claiming benefit; test counterexamples, stale dependencies and unrelated tasks. Retire or narrow lessons that mislead. Documentation clarity can justify a maintenance change without claiming measured capability uplift.

Keep fast process feedback separate from slow world feedback. Record a forecast's original claim, information set, horizon and resolution rule; append outcomes when due. Not-yet-due, unresolvable and missed are distinct. Changed operating or deployment policies define new cohorts. A skill's process checks, a model's prediction quality and a strategy's realized payoff need different evidence. Post-training/RL or automatic deployment are additional interventions only when explicitly in scope, not implied by a flywheel request.

## Captured Command Experiments

The standard-library [runner](../scripts/run_experiment.py) provides a small executable path for local, bounded, trusted commands. Prefer an existing capable harness. It captures stdout/stderr, exit/timeout and elapsed time, snapshots declared inputs and invokes a separate artifact grader. It does **not** launch a model service, audit nested tool calls, authenticate packet writers, enforce filesystem/network isolation, manage sealed holdouts or decide promotion. Run untrusted candidates in an externally isolated environment with controller-owned evidence and a protected grader. Declare all material files; undeclared dependencies remain an evidence gap.

Run the replay pilot from the repository root:

```bash
python3 research-craft/evals/flywheel/run_pilot.py --output /tmp/research-flywheel-pilot
```

Use a fresh output path. The pilot exercises archived pipeline failures/controls and synthetic forecast reconciliation; it is not a new model run or untouched holdout.

For another command, supply a JSON manifest:

```json
{
  "schema_version": 1,
  "run_id": "attempt-001",
  "candidate_id": "candidate-revision",
  "stage": "probe",
  "case": {
    "id": "case-001", "family": "task-family", "dataset_version": "v1",
    "split": "development", "exposure": "visible", "source": "authorized source or fixture"
  },
  "context": {"model": "not-applicable", "environment": "declared environment revision"},
  "cwd": "/absolute/workspace",
  "candidate_command": ["python3", "candidate.py"],
  "grader_command": ["python3", "grader.py", "{artifact}"],
  "criteria": ["answer-correct"],
  "files": [
    {"path": "candidate.py", "role": "candidate"},
    {"path": "grader.py", "role": "evaluator"},
    {"path": "data.json", "role": "input"}
  ],
  "timeout_seconds": {"candidate": 30, "grader": 10}
}
```

Commands are argv arrays, executed without a shell; file paths resolve against `cwd`. `{artifact}` is an exact grader argument replaced with the captured candidate stdout path. The grader reads it and emits JSON with one unique entry per declared criterion:

```json
{"criteria":[{"id":"answer-correct","status":"pass","evidence":"Specific observation in captured artifact"}]}
```

Allowed statuses are `pass`, `fail`, `unresolved`. Use exit zero for a valid grade, including negative/uncertain judgments; a grader crash is a grading failure. Candidate exit zero permits grading; nonzero/timeout records execution failure without assigning its root cause. Candidate self-reported verdicts are just output. Avoid detached background jobs: the runner bounds its child process group on timeout/interruption, not independently escaped jobs.

```bash
python3 research-craft/scripts/run_experiment.py run manifest.json --output /tmp/attempt-001
python3 research-craft/scripts/run_experiment.py summarize /tmp/attempt-001 /tmp/attempt-002
```

`run` exits 0 for completed artifact pass, 1 for a captured non-pass, 2 for invalid setup. `summarize` exits 0 for internally valid provided packets, including failed experiments; 1 for missing/inconsistent packets; 2 for invalid arguments or duplicate run IDs. Its exit code is not a suite pass. It groups comparable fixed identities, preserves failure counts and sums measured run time; fees, tokens, nested tool calls and human effort stay unknown. It does not check unlisted expected runs or choose a winner. Preserve all attempts and reconcile the expected run inventory separately.

Packets contain `manifest.json`, the exact `runner.py`, source snapshots, process stdout/stderr and `record.json`. Interrupted/incomplete packets remain visible. Verification checks archived evidence, so later source edits do not erase historical results. Copied files and hashes are reproducibility aids, not an adversarial security boundary. Use the existing experiment ledger to link these packets to findings, changes and subsequent confirmation.
