# Edge And Portfolio Controls

只在比较新信号的边际价值、组合因子暴露、仓位上限、信号衰减或 regime 风险时读取。继续遵守主技能的只读、fresh split、人工门禁和单 editable surface 合同。

## 1. 边际信号价值

不要问“新信号本身是否准确”，先问“当前 baseline 已经知道的内容之外，它是否增加成本后经济价值”。

按以下顺序检查：

1. 冻结 baseline、训练身份、费用、gate、退出、split 和主指标。
2. 标出候选与现有特征、信号、数据源和市场机制的重叠。
3. 在旧数据上用 ablation、nested model、baseline residual 或条件分层提出增量假设；不要把样本内正交化当成证明。
4. 在 fresh OOS 上比较 `candidate - baseline` 的 pot、costcov、dret、tn、尾部、集中度、turnover 和容量。
5. 只有增量跨 date cluster 稳定、未由单日/单品种驱动且护栏未恶化，才称为 marginal edge。

将证据分类为 `incremental / overlapping corroboration / redundant / contradictory`。同一事件产生的订单、涨价、管理层评论和分析师上修只能形成一个证据簇，不能按四次独立确认累计置信度。

## 2. 组合因子与真实分散

不要用策略数、品种数或交易所数代替独立风险下注数。根据策略实际机制选择暴露，包括但不限于：

- 市场方向、趋势/反转、波动率、流动性和拥挤；
- 商品板块、期限曲线、跨品种价差、session 和交易所；
- 持有期、成交速度、相同模型/特征族、相同数据源和相同退出机制；
- 保证金、容量、涨跌停、夜盘缺口和共同清算风险。

至少报告普通期与压力期的相关性、风险贡献、最大集中来源和可能同时失效的机制。正常期低相关不等于危机期分散。样本不足时标 `factor_overlap_unverified`，不要声称已经分散。

## 3. 稳健仓位上限

先区分 edge 是否存在，再讨论仓位。只有在 payoff、概率、相关性、费用、容量和尾部已有稳定 OOS 估计时，才把 Kelly 风格结果作为诊断上限；不要把 full Kelly 或 `mu / variance` 当成生产仓位。

对均值向下收缩，对方差、相关性、费用和冲击成本做压力上调，再取多个约束中的最小值：

```text
position_cap = min(
  robust_fractional_edge_cap,
  max_loss_and_drawdown_cap,
  liquidity_and_capacity_cap,
  margin_and_limit_cap,
  factor_and_concentration_cap
)
```

明确报告哪个约束绑定、参数来自哪里、估计误差多大。缺少关键输入时只给 `KEEP_CURRENT / SHADOW_ONLY / RISK_REVIEW / WEEKLY_REVIEW` 等受限动作，不生成仓位比例或自动扩量建议。

## 4. 信号衰减

用固定身份的 rolling fresh OOS 序列跟踪 edge，不凭最近几天或后验赢家切片判断衰减。至少观察：

- pot、costcov、dret、tn 和尾部的跨日中位数、正日率、LOO 与集中度；
- 预测 IC、direction capture、slope/scale 到成本后经济性的传导是否断裂；
- turnover、冲击成本、容量和参与率是否侵蚀原优势；
- 数据覆盖、目标定义、市场机制和竞争/拥挤是否发生结构变化。

将衰减候选原因分为过拟合、数据漂移、市场结构变化、竞争/拥挤、费用或容量、执行传导和测量错误。没有区分机制前，不要用“alpha 被套利掉”结束诊断。

## 5. Regime 只更新先验与风险预算

使用事前可观测的波动、趋势、流动性、盘口和信息流状态描述 regime。Regime 证据只能改变某类机制有效性的先验、预期 payoff 和风险预算，不能直接证明模型失效或执行出错。

默认渐进调低或提高风险预算，不做硬切换。只有状态定义、切换规则、滞后、误切成本和全链路经济性都在独立 fresh 数据上预注册验证后，才考虑自动状态切换；不得因后验 HMM 标签或某个状态切片漂亮而推进生产。

## 6. 输出补充字段

需要本参考时，在正常输出后增加：

```text
marginal_edge: 相对哪个 baseline、fresh 增量与证据等级
evidence_overlap: 独立证据簇与重复证据
factor_overlap: 普通/压力相关性、最大风险贡献、未核验项
position_cap: 绑定约束、参数来源、是否仅为诊断上限
decay_state: stable / watch / decaying / insufficient，及候选机制
regime_use: 只调整了什么先验或风险预算，禁止推断了什么
next_fresh_test: 时间、身份、主指标、护栏和 falsifier
```
