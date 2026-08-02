---
name: result-analysis
description: 统一分析 py 期货仓库的 result.py 日报、周报与 winress/detail/trades/signals/capacity 数据，从交易所/账户/品种聚合概览逐级下钻到 SIM、REAL、部署传导、信号兑现、P&L 瀑布、逐笔尾部、因子、容量及模型训练调优，并把证据路由成可证伪的下一步。用于“分析报告/PDF/winress”“日报/周报复盘”“分品种/逐笔归因”“SIM 与实盘差距”“模型为什么不准”“训练优化/参数调优/下一轮实验”等请求。
---

# Result Analysis

把原始 result bundle 转成一个决策优先、证据分层的复盘。先回答“当前最大且可修的损失在哪一层”，再决定是否下钻；不要用更多图表掩盖证据不足。

## 核心合同

- 默认只读。用户只要求分析、诊断或建议时，不修改仓库、配置、模型、生产状态或 review log。
- 每个关键数字都注明 `来源文件/列或代码位置 + 聚合方法 + 口径边界`。
- 用户未指定日期时，选择最新的完整 bundle，并在开头写明日期范围、账户、文件和缺失项。
- 单日只给 `观察/假设`；跨日证据不足时不写 `PROMOTE/DISCARD` 或具体参数裁决。
- 只选择一个首要瓶颈。最多给 3 条 action，每条包含机制、验证方法和 falsifier。

每次分析先完整读取 [references/analysis-contract.md](references/analysis-contract.md)。分析周报、周复盘或下周运行建议时再读 [references/weekly-review.md](references/weekly-review.md)；只有进入深度归因时再读 [references/deep-attribution.md](references/deep-attribution.md)；只有用户要求模型、标签、训练或参数优化时再读 [references/model-training-tuning.md](references/model-training-tuning.md)。

## 深度路由

| 模式 | 触发 | 最小输入 | 交付 |
|---|---|---|---|
| Quick | “看下日报/周报、按账户或品种汇总” | `winress`，可选 `detail` | 交易所/账户/品种/session 概览、稳定性与异常 |
| Standard（默认） | “复盘、为什么赚/亏、SIM/REAL 差距” | `detail + winress + trades` | 经济性、预测、策略、部署四层路由与首要瓶颈 |
| Weekly | “本周复盘、模型比较、下周运行建议” | 至少 3 个 READY 日报 bundle | pot-first 模型选择、稳定性过滤、日夜运行卡和调整信号 |
| Deep | “逐笔/因子/regime/容量/P&L 瀑布” | Standard + 按需 `signals/capacity` | 重尾、行为、因子、容量和证据缺口 |
| Tuning | “训练优化/标签/正则/gate/参数/实验方向” | 至少 3 个同身份日报束；优先 5+ | 单 editable surface 的可证伪假设包 |

从用户要求的最浅模式开始；如果当前证据无法区分模型、策略与部署层，自动加深一层并说明原因。不要默认读取超大 `signals` 或整本 PDF。

## 工作流

### 1. 定位完整 bundle

优先用 `rg --files`：

```bash
rg --files /home/x/www/results \
  | rg '/(detail|winress|winresd|trades|signals|capacity)_[0-9]{8}-[0-9]{8}\.(json|csv)$' \
  | sort
```

同一个 `<begin>-<end>` 至少要有 `winress`；Standard 还要核对 `detail` 与 `trades`。用户只给 PDF 时，先找同范围的 CSV/JSON；只有图表本身是问题或结构化数据缺失时才查看具体 PDF 页。

### 2. 冻结分析身份

记录：

- 日期范围、日报/周报、代码 commit/dirty 状态
- SIM/REAL 账户、品种、session、锁仓标记
- `account × y`、`fg/sg`、模型 params/hash；拿不到则标 `identity_unverified`
- 数据缺失、回填列和 schema caveat

模型、target、horizon、feature、gate 或状态机不同的日报不能直接合并；先拆 cohort。

### 3. 先读 detail，再按问题下钻

存在 `detail_<b>-<e>.json` 时先读 `meta.note`、`meta.recommend` 和 `cells`，建立：

1. SIM 经济性排序
2. REAL 实况
3. 描述性的部署传导差
4. SIM-only、锁仓和数据缺口标记

用 `winress` 校验聚合口径，用 `winresd` 检查逐日稳定性，用 `trades` 看逐笔尾部与行为；仅在因子、全 tick 预测或 margin 问题仍是 crux 时分块读取 `signals`。

### 4. 建立四层事实，禁止越级

| 层 | 问题 | 主要证据 |
|---|---|---|
| 数据/身份 | bundle 是否可比、是否泄漏或缺失 | schema、时间、params/hash、回填说明 |
| 预测/选择 | 全 tick、eligible、完成交易的预测是否健康 | hit/IC/direction capture/slope/scale、margin curve |
| SIM 经济性 | 信号经 gate、进出场和费用后是否赚钱 | held-out `pot`；辅以 costcov/dret/tn/avgnwt、gross-fee-net |
| REAL/部署 | 实际结果和 SIM 差多少、能否解释原因 | REAL pot/dret/PnL/hitr、订单生命周期、paired telemetry |

只有 `dwin - fee = dnwin` 是可闭合会计桥。没有稳定 decision/order id 和完整生命周期时，REAL−SIM 原因必须写 `deployment gap unresolved`。

### 5. 路由首要瓶颈

| 证据组合 | 首要路由 |
|---|---|
| 全 tick 与 SIM 完成交易预测跨日都弱 | 数据/标签/模型候选 |
| 全 tick 健康，SIM 经济性弱 | eligibility、gate、方向映射、持有、退出或显式成本 |
| SIM 预测与经济性健康，REAL 明显弱 | 部署传导；先补订单 telemetry/配对回放 |
| REAL 与 SIM 都健康 | 不改模型；监控漂移、集中度与容量 |
| 身份不明、样本薄或证据冲突 | `insufficient/mixed`；先补证据 |

金额影响、可控性和证据等级相同前，不要同时建议改模型、特征、gate 和退出。

### 6. 需要调优时运行诊断

完整读取模型调优参考，然后在至少 3 个独立日报束上运行：

```bash
python <result-analysis>/scripts/model_tuning_diagnostics.py \
  --results-root /home/x/www/results \
  --account dce_t1 --real-account dce_ht1028 \
  --lookback 20 --include-signals \
  --model-root /home/x/shared_16/models/latest_models_t1 \
  --output /tmp/model_tuning_diagnostics.json
```

脚本只生成候选路由，不选择参数。结合 `/home/x/py/docs/research/program.md`、`memory.md` 和 active TASK 检查关闭轴、固定 evaluator 与 fresh split；不得自动启动实验或修改 production。

## 输出合同

按实际深度裁剪，保留以下顺序：

1. **决策摘要**：首要瓶颈、证据等级、现在该做与不该做
2. **范围与数据健康**：bundle、身份、样本、缺失和 caveat
3. **聚合概览**：账户/品种/session，SIM 与 REAL 分栏
4. **Crux 归因**：预测、策略经济性、部署传导中损失最大的层
5. **证据缺口**：哪些只可描述、哪些已闭合
6. **Action**：最多 3 条；每条写机制、editable surface、固定项、验证 split、falsifier
7. **监控项**：下个日报最少需要观察的指标

Quick 模式可省略深层章节，但仍要给证据边界。Tuning 模式最后给 top-1 主候选和最多 2 个备选，不用日报替代 fixed evaluator 的正式裁决。

## 禁止事项

- 不整本读取数百页 PDF；优先结构化数据。
- 不把跨账户同号称为“真信号”；它最多提高稳定性先验，且要求合同可比。
- 不把 `real_sim_trade_ratio` 当 coverage，不把 `enter_reald-enter_d` 当滑点。
- 不把 REAL−SIM 差额自动归因于执行，不混用 dret capture 与原始 P&L capture。
- 不把 IC、R²、hit 或漂亮图表当作成本后 edge。
- 不凭单日、单品种、top_fc 或后验 regime 直接改参数。
- 不使用旧的无 size-impact、经常顶到网格上限的 `rec_M` 作为扩量依据。
- 不重开研究计划中的关闭轴，不做 per-symbol/per-cell 硬特化，除非新证据明确推翻旧前提。
- 只有用户明确要求落盘/持续跟踪时，才更新 `/home/x/py/analyze/review_log.md`。

## 资源

- `references/analysis-contract.md`：所有模式必读的数据、指标、聚合和证据边界
- `references/weekly-review.md`：Weekly 模式的 cohort、pot-first、资格门槛和运行卡合同
- `references/deep-attribution.md`：Deep 模式的 regime、P&L、行为、部署、因子和容量方法
- `references/model-training-tuning.md`：Tuning 模式的身份冻结、证据梯和实验合同
- `scripts/model_tuning_diagnostics.py`：跨日报、跨证据层的候选路由脚本；先运行 `--self-test`
