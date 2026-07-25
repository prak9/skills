# 从日报归因到模型训练与参数调优

## 目标

把日报异常转成**少量、可证伪、可由 fixed evaluator 裁决**的候选。不要把日报本身当训练集，不要用单日后验切片选参数，不要把预测指标改善等同于经济改善。

最终回答四个问题：

1. 弱点在标签/模型、策略选择、显式成本，还是部署传导？
2. 证据来自全 tick、eligible 信号、SIM 完成交易还是 REAL？选择条件是什么？
3. 只允许改哪个 surface，其余哪些身份冻结？
4. 什么观察会推翻假设，在哪个 fresh split 上裁决？

## 0. 先冻结身份和研究边界

在比较日期或生成候选前记录：

- 日报文件 start/end、账户、品种、session、代码 commit/dirty 状态。
- 模型文件真实路径、mtime、SHA256；params 中的 feature version、target type、horizon、model type、alpha/CV selector、sg/fg、训练日期和样本窗。
- 数据源/合约选择、wintest、费用真值、交易状态机、evaluator、split 和 seed。
- `/home/x/py/docs/research/program.md` 的 Locked Constraints、关闭/挂起轴、当前 active surface；`memory.md` 的最新结论和 active TASK。

按模型身份分组。若日报之间模型、目标、horizon、feature、gate 或状态机变化，禁止直接汇总；先拆成同身份 cohort。身份拿不到时写 `identity_unverified`，跨日结论降一级。

项目当前边界优先于本参考。通常遵守：held-out `pot` 为 EDGE 北极星；`costcov/dret/tn` 为核心辅助；`precision/IC/R²` 只诊断；默认 Ridge 主范式；session 是最细合法粒度；禁止 per-symbol/per-cell 硬特化；truth lockbox 不用于探索；AI 不自动 launch/stop/promotion/改 production。

## 1. 建立证据梯，禁止越级

| 层 | 样本集合 | 回答什么 | 主要指标 | 不能证明什么 |
|---|---|---|---|---|
| L0 数据/标签 | 决策时点可见的全量行 | 标签是否可用、是否泄漏/漂移 | 缺失、时间对齐、分布、重叠、realization curve | 交易赚钱 |
| L1 全 tick 预测 | 未经交易 gate 的 signals | 排序、方向、幅度、残差 | Spearman IC、R²、NRMSE、DAR、slope、scale ratio | 可交易性/成本后 edge |
| L2 eligible 信号 | fee/state gate 后 | 门槛是否筛出更高质量边际 | fee-aware precision/recall、分位单调性、margin curve、coverage | 完成交易收益 |
| L3 SIM 完成交易 | trades, account=dce_t1 | 预测进入状态机后的经济结果 | hit/corr、pnl\|hit/miss、pot/costcov/dret/tn/avgnwt、尾部 | REAL 执行因果 |
| L4 REAL 部署 | 实盘订单/成交 | 实际结果与部署差 | pot/dret/PnL、hitr、订单生命周期、paired markout | 未配对时的漏单/滑点原因 |

每个结论写清层级。L3 hit 高只能说明“已完成 SIM 交易子集方向兑现高”；它可能由 gate 选择造成，不能称为全模型准确率。L4 没有稳定 decision id 时只能写 deployment gap `unresolved`。

## 2. 统一指标口径

### 预测层

- `hit = mean(pred*real > 0)`：方向命中；零乘积按当前日报实现计 miss。必须同时报 `target_zero_rate` 和只在 `pred≠0,real≠0` 上计算的 `nonzero_hit`；零标签密集时原始 hit 主要反映标签稀疏度，不能判模型弱。
- `IC = Spearman(pred, real)`：排序能力，重尾下优先于 Pearson；同时报告 Pearson 作线性校准参考。
- `R²`：幅度拟合。高频噪声下可为负，不能单独否决有排序价值的模型。
- `NRMSE/RMSE/MAE`：误差尺度。只有标签尺度相同才可横比；MAE/one-tick 可解释“误差相对最小价格变化”。
- `DAR/dir_acc`：全样本方向准确率，常被接近零的噪声目标稀释。
- `prec`：fee-aware 正类中真正方向/收益达标的比例；配合预测数/交易数比 accuracy 更适合作交易相关准确率。
- `recall/F1`：召回与精确率权衡。若目标是不交易区很大，accuracy 会被 TN 支配，通常不用于选模型。
- `calibration slope = Σ(pred·real)/Σ(pred²)`：`>1` 常提示预测幅度偏小，`<1` 常提示幅度偏大；必须结合 intercept、分位图和 OOS 稳定性。
- `scale ratio = median(|pred|)/median(|real|)`：抗重尾的幅度比；标签或 horizon 改变后不可直接比较。
- `direction capture = Σ(sign(pred)·real)/Σ|real|`：幅度加权方向质量，范围约 [-1,1]；分母是标签质量，不是美元 oracle。

### 经济层

- EDGE 正式选择使用 fixed evaluator 的 paired held-out `pot`。
- `costcov` 判断毛利对成本的覆盖/侵蚀，`dret` 看规模收益，`tn` 看活跃度和样本量，`avgnwt` 看每手质量。
- 同时报中位数、正日率、最差日/窗、LOO、最大日/窗贡献。总和为正但去掉一日反号，标 concentration risk。
- 不用更高 hit/IC/R² 替代 `pot`。合理候选必须预言“预测层变化如何传导到 eligible margin、交易结构和 held-out pot”。

## 3. 跨日证据包

发现最新完整的 daily bundle；排除周报和 `_trade` 重复文件，避免同一天重复计权。默认查看最近 20 个交易日报：

```bash
python <result-analysis>/scripts/model_tuning_diagnostics.py \
  --results-root /home/x/www/results --account dce_t1 --real-account dce_ht1028 \
  --lookback 20 --include-signals \
  --model-root /home/x/shared_16/models/latest_models_t1 \
  --output /tmp/model_tuning_diagnostics.json
```

使用以下证据等级：

- 1 日：异常观察，只列待确认项。
- 3–4 个同身份交易日且完成交易 `n≥100`：早期候选路由，不给具体参数裁决。
- ≥5 个同身份日期 cluster：可形成 Explore Opportunity；仍需 fresh、预注册 fixed evaluator。
- 正式 PROMOTE/REJECT：只服从项目 frozen WFA/gate，日报统计不得代替。

日不是绝对独立样本；相邻日、同模型和重叠标签存在相关性。把 date/model identity 作为 cluster，披露有效独立单元数。优先报告日级中位数、正日率和 concentration，不让交易笔数多的单日吞掉其他日期。

## 4. 诊断路由

按以下顺序裁决首要层：

1. **L1 全 tick 与 L3 完成交易都跨日弱**：模型/标签/训练候选。
2. **L1 弱、L3 强**：gate 选择可能掩盖基础模型弱；先看可交易覆盖和容量，不直接重训或宣称健康。
3. **L1 强、L3 弱**：模型有预测信息，但 eligibility、方向映射、持有/退出或费用未将其货币化。
4. **L1/L3 与 SIM 经济性都强，REAL 弱**：部署传导问题；先补 paired telemetry，不改模型。
5. **预测与经济指标方向冲突**：检查标签尺度、样本选择、费用、尾部集中和实现 bug；标 `mixed`。
6. **证据薄或身份混合**：标 `insufficient`；只说明下一步需补什么。

只选择金额影响最大、可控、证据等级最高的一个瓶颈。不要同时把模型、gate、特征和退出都列为“共同优化”。

## 5. 参数/训练 surface 的症状—机制—反证

下表只生成候选，不是自动改参规则。

| Surface | 支持该方向的跨日签名 | 最小候选 | 关键反证 |
|---|---|---|---|
| target/horizon | 当前 horizon 的全 tick IC/dir capture 弱；realization curve 在相邻预设 horizon 稳定峰值；持有尺度与峰值一致 | 固定 `h3/h5/h8` 中一个对称对照，其他全冻 | 峰值不稳定、只单品种出现、经济指标不随预测改善 |
| Ridge alpha/正则 | 高 alpha：pred 过度收缩、slope>1、IC尚存但 eligible 太少；低 alpha：scale ratio 高、slope<1、系数/日级表现不稳、train→OOS gap 大 | 预注册相邻少量 alpha 或让现有对称 CV 选择 | 改善只在训练/CV 内，fresh pot 无改善；命中已关闭 alpha 轴 |
| CV selector | 被选 alpha 的预测指标好但 OOS pot/成本边际长期不一致；selector 常撞边界或 tie | 仅比较当前允许的固定 selector，保持 alpha grid/数据完全一致 | 同窗 A/A 漂移、selector 只改变 tn 或成本暴露 |
| scaling/gate policy | 低门槛：tn 高、margin 底部分位 precision/pot 负、costcov 恶化；高门槛：precision 上升但 tn/dret 塌、上分位仍单调 | 固定模型做预注册窄 response surface | 改的是费用真值 `cost_fee_gate`；或只靠砍交易抬 avgnwt、pot 不升 |
| train span/decay | 新旧 regime 分层漂移；老样本残差系统偏；短窗系数方差过大或长窗滞后 | 固定特征/标签/alpha 只改一个预设训练窗 | split 泄漏/重叠；效果由一个 date cluster 驱动 |
| prediction calibration | IC/方向健康但 slope/scale 持续偏，fee margin 排序不单调 | 固定排序模型，只校准 OOS scale/intercept | 现有 sg 已表达同一语义；pot 不升或 tn/costcov 恶化 |
| feature family | E1 贡献、E2 边际、E3 孤立 IC 跨日/跨 session 同向，且负贡献不是单日尾部 | 一次只 ablate/add 一个机制族 | top_fc 仅观察归因；fresh economics 不支持；触及 v2p/深剪枝关闭轴 |
| label/data alignment | 不可能的高指标、边界跳变、目标时间戳晚于决策、重叠/缺失异常 | 先修数据真相并重建同身份 baseline | 修复前后 A/A 不可比；不能把 bug fix 当 alpha 提升 |

额外判读：

- `hit` 高、IC 低：大量小幅方向正确但排序不了大机会；查幅度/置信度，不为 hit 再优化。
- IC 高、precision 低：全样本有排序信息，但 fee-aware 边际或方向阈值错；先看 margin curve。
- precision 高、pot 低：正确交易的金额不足、退出/费用/错单尾部吞噬；看 `pnl|hit/miss` 和 P10。
- R² 上升、pot 不升：幅度拟合没有转化为决策质量；不推进。
- pred/real scale 漂移而 IC 稳：优先校准或训练漂移诊断，不先加特征。
- 某 cell 极差但全局稳定：只登记 attribution；禁止从后验 cell 直接生成专用模型。

## 6. 防止后验过拟合

- 在看 fresh 结果前冻结 hypothesis、唯一主指标、候选值、split、样本地板、falsifier 和停止规则。
- 每次只改一个 candidate surface；不把标签、特征、alpha、sg、gate 和退出捆成一臂。
- 所有看过的日期和参数计入 search exposure。旧日报只 Explore，fresh 独立窗才 Exploit。
- 报告所有合法 cell、LOO、负窗数和集中度；不只展示赢家切片。
- 后验 regime/symbol/session 切片只能解释机制或生成下一轮预注册假设。
- 检查 `program.md` 关闭轴：当前已知 per-cell/per-symbol 硬特化、若干 alpha/标签/剪枝方向有历史反证。无“旧前提失效”的新证据不得重开。
- 不因日报建议自动修改 conf、模型、champion、production；不自动启动或停止实验。

## 7. 产出一个可执行的假设包

最多给 top-3，明确推荐 top-1。每个候选用以下字段：

```text
diagnosis: 哪一层、哪个瓶颈
evidence_scope: 模型身份、日期 cluster、cell、n、全 tick/eligible/trade/REAL
observations: 中位数、正日率、最差日、LOO、集中度及数据源
mechanism: 为什么该参数会影响该瓶颈
editable_surface: 只允许一个
fixed_fields: model/data/feature/target/horizon/evaluator/cost/split/seed 中冻结项
candidate_values: 少量、预注册、对称
predicted_signature: L1→L2→L3 应出现的联动
falsifier: 哪个结果直接否定机制
screen_split / verify_split: 旧数据探索与 fresh 裁决分开
sample_floor: 日期 cluster、交易/信号数与完整 cell 要求
decision_metrics: primary pot；costcov/dret/tn 护栏；诊断指标
overfit_risk: search count、后验切片、身份混合、尾部集中
history_check: program/memory 中新轴、开放轴或关闭轴依据
verdict: TEST / PARK / CLOSE；不能写 PROMOTE，除非 fixed evaluator 已裁决
```

按“预期经济影响 × 证据等级 × 可逆性 ÷ 过拟合风险/实现范围”排序。若最佳候选仍 `identity_unverified`、`insufficient` 或命中关闭轴，输出“先补证据”，不要硬凑参数值。
