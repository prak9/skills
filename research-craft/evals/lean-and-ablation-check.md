# Lean Delivery And Ablation Check — 2026-10-05

## Changed Surface

Standard/deep research now defaults to report + memo with an evidence appendix or existing supporting records. Full audit packaging remains available when requested or justified. Research depth, evidence duties and requested audit acceptance are not reduced. A new ablation guide distinguishes conditional effects, interactions, intervention validity/stage, resources, adaptation and uncertainty.

Inputs inspected during this check:

| File | SHA-256 |
|---|---|
| `research-craft/SKILL.md` | `902a735480176472e4ae7f98f484c436cc352b5e29d587962ccdccd88c267edc` |
| `research-craft/references/ablation-design.md` | `d45dfaa63912f7e51a373e6506d8f660a83bfad2ba188f3826c2ff7bb28313eb` |
| `research-craft/examples/ablation/report.md` | `c147892c119ab721d3b0d19657fdba252587ac247e3f426846a3d256d53ef51b` |

## Source-Based Lean Report

The main agent performed a bounded method investigation using the three NIST pages linked in `examples/ablation/report.md`, composed the complete explainer and memo, and checked them under the writing skill's argument/qualifier guidance. Locators, originating-source limitations, calculations, self-review status and reopening conditions are in the report. No native-package files were needed for this example.

Source-backed methodological statements, software-design inferences and invented arithmetic inputs are distinguished. A direct recomputation from the saved table returned 2, 12, 13, 10 and 15 percentage points for A without B, A with B, B with A, interaction and bundle respectively. No actual Agent success rate, statistical significance or quality improvement was measured.

## Separate-Agent Scenario Execution

Worker: `/root/ablation_forward_check`; fresh task context without this turn's conclusions. The worker was asked to use the Skill and answer in chat only, without network, writes or delegation.

Task: base/A/B/A+B aggregate success rates of 60/62/63/75 percent, no per-task rows or repeated runs; user proposes adding the two removal effects and choosing a component to remove for cost savings. B consumes A's output and crashes if A is directly disabled; only one ablated variant has been retuned. Requested deliverable: judgment and the next minimal experiment.

Observed response excerpts:

> 12 和 13 是不同背景下的条件效应，不是可相加的独立份额。

> 既然直接关闭 A 会导致 B 报错，“只开 B＝63%”究竟用了什么输入、旁路或替代模块？在核清前，它不能被当作干净的 B-only 单元。

> 可以先测试删 B……这是实验实施顺序，不是“B 更没用”的判断。

The response computed bundle gain 15 and interaction contrast 10 percentage points conditionally, flagged the missing observations and unilateral retuning, and declined to select a production deletion without costs/acceptable harm. It proposed valid interfaces first, then comparable configurations, task-level outcomes/costs and confirmation. It separated a fixed-setting contrast from a fairly retuned system comparison and did not demand an arbitrary number of repeats or a full factorial by default.

Main-agent assessment: the returned answer addressed the task's attribution, dependency and adaptation traps and respected chat-only delivery. The worker reported read-only use of the entry point, controlled-research, ablation-design, experiment-reporting and evidence-contract. Its tool activity was not independently audited here.

This was a separate execution, not blinded independent grading or an A/B capability measurement. Its numeric example also appears in the guide; the case is not an untouched holdout. No generalization, latency/cost improvement or causal gain from the new instructions is claimed.

## Mechanical Checks

- `python3 .system/skill-creator/scripts/quick_validate.py research-craft`: valid Skill.
- `python3 -m unittest discover -s tests`: 110 tests passed; no new deterministic tests were added for these documentation changes.
- `python3 research-craft/scripts/validate_research.py research-craft/evals/report-package`: passed with the two pre-existing synthetic evidence limitations. This checks audit-mode compatibility, not the lean report's truth.
- Local-link inspection of the entry point, references and examples: 55 links resolved, zero missing targets (excluding code examples and external URLs).
- `git diff --check`: passed.

Remaining uncertainty: one authored source report and one scenario execution do not establish performance across genres, real model-training ablations or long investigations. No baseline-versus-candidate campaign, formal holdout evaluation or production rollout was performed.
