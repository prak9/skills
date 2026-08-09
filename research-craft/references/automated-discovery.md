# Automated Discovery Loops

Use this adapter when agents or ML systems will decompose a scientific or engineering problem, run experiments, compare results, and improve the candidate system. Automation is useful only when it increases trustworthy learning throughput; a fast loop around a weak objective is an automated way to become confidently wrong.

```text
important, partly tractable problem
  -> explicit decomposition and fixed evaluator
  -> smallest informative experiments
  -> parallel runs with isolated ownership
  -> evidence reconciliation
  -> accept / reject / revise
  -> narrow-domain result, then tested generalization
```

## Choose A Foundational, Partly Solvable Problem

- Track many research directions lightly enough to notice recurring constraints and ideas that have not yet been connected. Skim broadly; read deeply only after a candidate survives the first filter.
- Separate the enduring outcome from today's fashionable implementation. Ask what would still matter if the current model, framework, or benchmark disappeared.
- Prefer long-horizon problems with several proven footholds and a small number of decisive unresolved cruxes. “Everything is unknown” is not ambition; it is an unbounded research contract.
- Estimate orders of magnitude for data, compute, experiment duration, cost, coordination, and likely improvement. Use first-principles estimates to reject impossible shapes before expensive execution.
- Record why the problem may be neglected and what evidence would show that the apparent opening is illusory.

Do not confuse broad scanning with broad execution. Commit resources narrowly after the crux is explicit.

## Design Around The Load-Bearing Abstraction

- Define the representation that lets researchers express the problem while the system handles incidental hardware, scheduling, and distribution details.
- Preserve an explicit escape hatch when backend details change semantics, performance, observability, or correctness. An abstraction should remove accidental complexity, not hide decisive constraints.
- When the territory is inherently multimodal, make the modalities part of the core data and evaluation design from the start. Do not bolt image, video, audio, spatial data, or code onto a text-only evaluator after the architecture has hardened.
- Treat code as executable reasoning: it makes decompositions, tests, simulations, and comparisons inspectable and reproducible. Improving code competence can improve problem decomposition, not just implementation speed.
- Offer a direct path for the common case before advanced graph, configuration, or distributed machinery. Promote an abstraction only after repeated tasks show the same stable boundary.

## Optimize Learning Throughput, Not Activity

1. Reproduce the baseline and validate the evaluator.
2. Decompose the problem into subproblems with explicit inputs, outputs, evidence, and ownership.
3. Run the cheapest experiment that can discriminate the leading explanations.
4. Shorten single-experiment latency before multiplying parallel runs.
5. Parallelize only independent or deliberately replicated experiments; isolate state, seeds, data, and artifacts.
6. Compare every candidate under the same frozen protocol and reconcile evidence, not agent summaries.
7. Integrate only improvements that survive guardrails, holdouts, and independent reproduction.

Measure useful learning per unit time. Experiment count, agent count, and GPU utilization are activity metrics unless they reduce a decision-relevant uncertainty.

Treat discovery throughput as a diagnostic product, not a literal formula:

```text
discriminating experiments x evidence validity x independence x integration rate
-------------------------------------------------------------------------  per unit time
```

Increasing parallelism amplifies error when validity, independence, or integration falls.

## Coordinate Coupled Improvement Loops

Treat problem decomposition, data selection, evaluator design, candidate architecture or algorithm, training procedure, and portfolio scheduling as separate, versioned loops.

- Keep the objective, target construct, permissions, acceptance gates, and irreversible promotion human-approved.
- Change one loop or layer per comparison when attribution matters. Freeze the dependent data, evaluator, training protocol, and candidate versions.
- Treat data, evaluator, or harness improvement as its own loop. Validate it against replay anchors, record the new version, and refreeze it before candidate comparison resumes.
- Run candidate loops under the frozen harness. Do not infer which change caused an improvement when several layers moved together.
- Let the portfolio loop schedule declared experiments; do not let it silently redefine the objective, judge, or evidence needed for promotion.
- When loops must interact, stage them on different timescales and record their dependency graph and version tuple.

The goal is end-to-end automation with attributable evidence, not simultaneous co-adaptation of every layer.

## Allocate Compute By Expected Learning Value

Rank experiments with an explicit, revisable heuristic:

```text
priority ~= (expected reduction in decision-relevant uncertainty
             x impact on the crux or downstream decision)
            / (compute + elapsed time + coordination cost)
```

- Stage cheap falsifiers before expensive confirmations, and expand a run only through predeclared evidence gates.
- Maintain separate capacity for exploitation, exploration, independent replication, and evaluator or leakage audits. Do not let the current leader consume the whole budget.
- Treat the priority as a forecast to calibrate after resolution, not as ground truth. Record expected and realized learning value in the ledger.
- Do not rely only on an experiment-proposing model's estimate of its own value. Use replay performance, independent checks, or a separately governed scheduler.
- Count repeated exposure to the same evaluator or holdout as an adaptation cost even when wall-clock execution is cheap.

## Automate Without Self-Deception

The system may propose data selections, architectures, transformations, hypotheses, and follow-up experiments. Keep these outside its editable surface unless the research contract explicitly says otherwise:

- primary objective and guardrails
- holdout and anti-leakage boundaries
- evaluator implementation and version
- permission and safety limits
- acceptance, rollback, and stop rules
- authoritative experiment ledger

Never let a candidate edit the test that promotes it in the same round. Persist rejected runs and negative results. Stop on budget exhaustion, evaluator instability, repeated non-informative failures, or evidence that the decomposition is wrong.

## Start Narrow, Generalize Through Transfer

- Begin in a bounded domain with measurable outcomes, accessible experiments, and enough expert knowledge to recognize evaluator failure.
- Extract infrastructure only from repeated, evidenced needs. Name each extension by purpose, owner, stability, and promotion or deletion rule; avoid a generic contribution bucket that becomes a second public API.
- Test a supposedly reusable interface on a materially different second domain before calling it general.
- Publish or preserve the implementation, protocol, baselines, environment, and negative results needed for reproduction. Open artifacts are part of the evidence, not merely distribution.

The sequence is: solve one real problem, expose the stable boundary, prove transfer, then generalize.

## Reconcile A Multi-Agent Experiment

For each subproblem, require:

```text
Question and local hypothesis:
Inputs, frozen evidence, and exclusions:
Editable surface:
Expected observation and falsifier:
Command, environment, seed, and artifacts:
Result with uncertainty and failure cases:
Integration dependency or conflict:
Loop or layer under change / frozen dependency versions:
Expected learning value / crux impact / total cost:
Scheduler rule / exploration floor / replication and evaluator-audit budget:
```

The coordinator resolves incompatible assumptions and duplicated evidence before combining results. Do not “average” incompatible claims into consensus.

## Failure Modes

- **Fashion anchoring:** optimizing the dominant implementation without asking whether the underlying constraint admits a different formulation.
- **Parallel noise:** launching many coupled experiments whose results cannot be attributed or reproduced.
- **Coupled-loop confounding:** changing data, evaluator, training, and candidate layers together, then assigning the gain to a preferred explanation.
- **Greedy scheduling:** allocating everything to early leaders, suppressing exploration, replication, and discovery of evaluator failure.
- **Evaluator co-adaptation:** improving the score by weakening, leaking, or rewriting the judge.
- **Premature platform:** building cross-domain infrastructure before one domain has produced a repeatable learning loop.
- **API fragmentation:** allowing experimental extensions to create multiple competing ways to express the same core operation.
- **Self-grading:** accepting an agent's completion claim without raw artifacts and an independent checker.
- **Speed without learning:** reducing runtime while the decisive uncertainty remains unchanged.

Source: distilled from the supplied discussions of Jeff Dean's TensorFlow and Gemini lessons, first-principles problem selection, automated ML, and automated scientific discovery loops.
