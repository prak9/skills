---
name: research-craft
description: 设计和审查可证伪实验、消融、预测验证，以及模型迁移、Prompt/Skill 和 Agent Harness 的对照评测；按需提供专业研究方法与验证脚本。不用于普通事实检索、泛化深入调研、资料总结或日常实现优化。
---

# Research Methods

Use when the experiment or its validity is the task—not as a mandatory wrapper around research, explanations or implementation. Ordinary source-led investigation proceeds directly. This bundle retains specialist methods, executable checks and historical evidence; their presence does not require a report package or experiment ledger.

## Select The Method

Read only the reference that resolves the current methodological question:

| Question | Reference |
|---|---|
| Baseline/candidate comparison, controls or measurement validity | [Controlled research](references/controlled-research.md) |
| Removing components, attributing gains or testing interactions | [Ablation design](references/ablation-design.md) |
| A new model or tool surface motivates changing instructions | [Instruction migration](references/instruction-migration.md) |
| Timing, leakage, probabilities, prediction or simulator validity | [Prediction validation](references/prediction-validation.md) |
| Competing mechanisms, causal identification or falsifiable hypotheses | [Hypothesis formation](references/hypothesis-formation.md) |
| Verification closure, agent memory, permissions or self-edits | [Harness engineering](references/harness-engineering.md) |
| Feedback sampling, adaptive search or repeated evaluation | [Research flywheel](references/research-flywheel.md) |
| Backtest, scorer and research-to-runtime consistency | [Quant strategy iteration](references/quant-strategy-iteration.md) |
| Assisted task performance versus independent learning/transfer | [Human-learning evaluation](references/human-learning.md) |
| Failure attribution or diminishing returns | [Trace attribution](references/trace-attribution.md) |
| Parallel experimental ownership or discovery infrastructure | [Automated discovery](references/automated-discovery.md) |

For substantive experimental results, use [experiment reporting](references/experiment-reporting.md). A user-requested source-research package can use [report design](references/research-reporting.md), [evidence contract](references/evidence-contract.md) and `scripts/validate_research.py`; these are optional artifact formats, not the default research workflow. [Source discovery](references/source-discovery.md), [perspective discovery](references/perspective-discovery.md), [deep research](references/deep-research.md) and [updates](references/research-updates.md) remain available for a specific collection, coverage or maintenance problem.

## Validity That Changes The Answer

- **Argument integrity:** separate observation, mechanism and causal claim. Name the competing explanation and the observation that would distinguish it. Check the latent construct / model boundary: a measurable proxy may not be the requested property.
- Freeze the comparison's outcome, cases, evaluator and material environment. Change one factor or related family for attribution; use interaction tests when effects are not separable. Fix a defective evaluator separately and rerun both arms under the corrected protocol.
- Count independent originating observations, not URLs, repeated model agreement or files from one run. Preserve negative and unresolved results, disclosure timing, units and consequential qualifiers.
- Adaptive selection, repeated testing and reused data can inflate apparent gains. Keep untouched cases where feasible, distinguish development from acceptance, and include the search/verification cost when claiming efficiency.
- State what was actually executed. Structural checks, deterministic fixture replay and forward agent behavior are different evidence. Missing telemetry is unknown; a green validator does not prove semantic correctness or improved model performance.

## Execute And Deliver

Reuse the accepted goal, permissions, resource bounds and existing records. Prefer the cheapest discriminating test; do not create new files just to satisfy a workflow. `scripts/run_experiment.py` can capture bounded command experiments when appropriate. Research does not authorize external publication, trading, evaluator changes or expanded resource use.

Deliver the comparison or supported finding, raw evidence locations, surviving alternatives, validity limits and what would change the conclusion. A negative or unidentifiable result can answer the question. Preserve the best verified candidate when a new attempt fails; distinguish accepted improvement, convergence, budget exhaustion and blockage without claiming global optimality.
