# 概率、模拟过程与运行一致性

仅在概率输出可信度、模拟过程失真或研究/运行路径差异是当前 crux 时读取。沿用现有 bundle、身份、成本与授权合同；本参考只补诊断，不启动训练、交易或生产变更。

- **概率输出：**读取 [概率预测验证](../../research-craft/references/prediction-validation.md)。先确认目标事件、预测时点、全量/eligible/已成交条件与实际概率字段。回归的预测收益、IC 或 calibration slope 不是事件概率，不能直接套 Brier 或概率校准，也不能未经验证加 sigmoid 后当概率。
- **过程模拟：**同一参考中按用途检查次数、持有时间、尾部与亏损聚集。总收益或均值吻合不代表过程可信；Monte Carlo 精度不等于经济优势。没有足够样本或过程数据时标 `insufficient`，不能用图表制造模型失败结论。
- **研究到运行：**读取 [量化研究的一致性检查](../../research-craft/references/quant-strategy-iteration.md#preserve-research-to-runtime-semantics)。用同输入、初始状态、可获得时间和版本配对，定位特征、中间值及决策差异；总 P&L 接近不代替差分证据，没有配对时保留 `unresolved`。
- **系统性残差：**先核对时间对齐、标签、cohort、样本选择、实现与随机波动。仍有结构时，用 [竞争假设](../../research-craft/references/hypothesis-formation.md) 比较候选机制与其差异预测，在 fresh 数据检验；不得凭后验切片新增专用参数或重开关闭轴。

只交付当前首要瓶颈的证据、能区分解释的最低成本检查、保持不变项及反证条件。预测有所改善但未证明经济价值，可以完成预测分析；沿用 fixed evaluator 才能作正式策略裁决。
