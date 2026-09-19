---
name: result-analysis
description: 解释 py 期货仓库 result.py 的日报、周报及 winress/detail/trades/signals/capacity 数据，诊断交易结果、SIM/REAL 差异与相关研究问题。仅在需要这些项目数据或指标口径时使用；不用于泛指的结果分析、软件测试结果、普通统计、论文实验或无关模型调优。
---

# Result Analysis

提供 py 期货项目的指标语义与证据边界。分析什么、检查多深、如何表达，由当前问题和证据决定，不默认生成完整复盘。

## 按问题工作

- 已提供的数据足以回答时直接回答；算术核对、单字段解释或已有结论的追问不要求完整 bundle、模型 hash、图表或研究建议。不为补模板索取无关信息。
- 需要找数据时，用 `rg --files /home/x/www/results` 定位对应日期的结构化文件。用户没有指定日期且需要新报告时才选最新完整 bundle；缺失与真实零值分开。PDF 只查看有关页面，不默认读取整本。
- 有多个问题时按影响和可验证性排序，可以保留多个独立问题或 `mixed/unresolved`，不强行选唯一原因。仅当更深检查可能改变当前答案时下钻；一条链的证据缺口不阻止另一条独立证据链的研究。
- 回答有依据且已覆盖请求即可结束。不默认增加监控、实验、运行卡或下一步；提出因果假设时才补最有辨别力的验证与反证。

## 不随流程简化的边界

- 关键结论可追溯到题内数据或文件/字段及聚合口径。明确事实、代理与假设；不要求每句话加标签或套固定句式。
- SIM、REAL、回放、全 tick、eligible 与已成交样本不能混作同一总体；跨期比较核对与该结论相关的身份和时间，局部变化只影响相应 cohort。
- `dwin - fee = dnwin` 是同口径会计关系。`real_sim_trade_ratio` 不是 coverage；`enter_reald-enter_d` 是预测兑现差，不是价格滑点。未逐决策配对的 REAL−SIM 差额原因保持 `deployment gap unresolved`；成交价已反映的成本不重复扣除。
- IC、hit 或单日收益不能独立证明成本后 edge。策略晋级遵循项目的 frozen evaluator、fresh 数据与风险约束；分析或研究提案本身不等于晋级。
- 分析默认只读；实验、落盘、外部写入及生产操作遵循当前明确授权和项目保留的批准边界。既有实盘约束不因精简而放宽，也不因 Skill 触发而要求重复审批。

## 按需参考

只选当前问题必需的参考；选中后完整读取，不要求每次读取通用合同。已经在当前上下文读过且版本未变的参考可直接沿用。读取参考不等于执行其中全部检查或生成全部交付物。

| 需要解决的问题 | 参考 |
|---|---|
| bundle/字段含义、聚合或身份比较不清楚 | [数据与指标](references/analysis-contract.md) |
| 逐笔、部署传导、因子、容量或 P&L 归因 | [深度归因](references/deep-attribution.md) |
| 标签、模型、训练或参数的专业诊断 | [训练诊断](references/model-training-tuning.md)；只提出相关假设，不自动跑脚本 |
| 新信号边际价值、组合、仓位、衰减或 regime | [经济与风险边界](references/edge-portfolio-controls.md) |
| 概率、模拟过程或研究/运行一致性 | [预测有效性](references/prediction-validity.md) |
| 用户明确要求日报图包或下一时段运行建议 | [日报交付](references/daily-decision-loop.md)；图表与运行建议分别按请求选用 |
| 跨日周报或下周运行选择 | [周复盘](references/weekly-review.md)；运营回顾不自动进行模型选择 |
| 实盘候选筛选、研究晋级或运行政策 | [py 项目政策](references/project-policy.md)；数字门槛不是通用统计定律 |

`scripts/model_tuning_diagnostics.py` 可辅助跨日报候选路由；仅在需要跨日诊断且输入可用时运行，用法见训练诊断参考。脚本输出不代替项目裁决。
