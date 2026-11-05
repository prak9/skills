# Deep Attribution

只在当前问题需要逐笔、因子、regime、容量或 P&L 归因方法时读取。各节按需应用，不因读取本文件执行全部分析；代码片段中的账户与参数是例子，不是任务默认值。

## 1. 从 detail 建立事实层

`detail_<b>-<e>.json` 常含：

```text
meta: start/end/n_days/sim_account/real_account/locked_syms/recommend/note
cells[]:
  sym/session/locked
  consensus: consensus_pos/consensus_n/sim_trade_n/real_trade_n/real_sim_trade_ratio
  sim: pot/costcov/dret/tn/pot_min/pot_max/avgnwt/wdr/pf/win_r/hitr/
       avgw2l/nwin/dnwin/dwin/avgtn/tvol/fill_rate
  real: 同口径子集或 null
  gap: pot_gap/dret_gap/capture 或 null
  signal_realization/when_daily/exec_review/worst_seg
```

使用 detail 复盘时可从以下维度建立事实；仅单项归因不必生成四张表：

1. SIM 经济性：按 `pot` 排序，辅以 costcov/dret/tn/avgnwt/尾部
2. REAL 实况：单列实际交易 cell
3. 部署差：dret/P&L/交易数/hitr 分栏，原因默认 unresolved
4. 边界：锁仓、SIM-only、身份不明、缺文件

再决定是否读取逐笔或 signals。

## 2. 行情 regime

用三维刻画每个 `sym×session`：

```text
波动：midprice return std / range_bp
趋势：|首尾变化| / Σ|逐 bar 变化|
微结构：spread × 对手盘深度，另看开盘/尾盘成交聚集
```

有 signals 时优先用 midprice 和盘口；只有 trades 时可用进出场价格做降级代理，并明确选择偏差。

```python
tr = pd.read_csv(trades).reset_index(drop=True)
g = tr.groupby(["sym", "dorn"]).agg(
    n=("pnl", "size"),
    px_lo=("enter_price", "min"),
    px_hi=("enter_price", "max"),
)
g["range_bp"] = (g.px_hi - g.px_lo) / g.px_lo * 1e4
```

regime 只改变某类机制的先验，不直接证明模型或执行原因。输出类似 `eb day: 中波·弱趋势·厚盘`，并把 caveat 挂到后续归因。

## 3. P&L 与预测链

保持单位分离：

```text
标签机会质量（dfactor proxy，不是钱）
  -> 全 tick 预测
  -> eligible 选择
  -> SIM 完成交易
  -> SIM dwin - 显式费用 = dnwin      # 可闭合
  -> REAL 结果                         # 未配对时只描述
```

### 标签与预测

```python
import numpy as np
g = signals.groupby(["sym", "dorn"])
label_mass = g.r_dfactor.apply(lambda x: x.abs().sum())
hit = g.apply(lambda x: ((x.dfactor * x.r_dfactor) > 0).mean())
ic = g.apply(lambda x: x.dfactor.corr(x.r_dfactor, method="spearman"))
direction_capture = g.apply(
    lambda x: (x.r_dfactor * np.sign(x.dfactor)).sum() / x.r_dfactor.abs().sum()
)
slope = g.apply(
    lambda x: (x.dfactor * x.r_dfactor).sum() / (x.dfactor * x.dfactor).sum()
)
```

- `label_mass` 含重叠标签与重复 tick，只是同口径 opportunity proxy。
- hit 同时报 target zero rate 与 nonzero-hit。
- Spearman 看排序，direction capture 看幅度加权方向，slope 与 median scale ratio 看校准。
- 全 tick、eligible、completed-trade 三个样本分栏；后两者存在选择偏差。

### 收益结构与费用

```python
t = tr[tr.account == "dce_t1"].copy()
t["win"] = t.pnl > 0
tail = t.groupby(["sym", "dorn"]).agg(
    n=("pnl", "size"), pnl=("pnl", "sum"),
    win_r=("win", "mean"), median=("pnl", "median"),
    p10=("pnl", lambda x: x.quantile(.1)),
    p90=("pnl", lambda x: x.quantile(.9)),
)

w = pd.read_csv(winress).reset_index(drop=True)
fee = w[w.account == "dce_t1"].groupby(["s", "t"]).agg(
    dwin=("dwin", "sum"), dnwin=("dnwin", "sum")
)
fee["fee"] = fee.dwin - fee.dnwin
```

高预测 hit 但 `pot/avgnwt≤0` 时先查 gate、持有、退出和成本，不直接重训。费用比例在毛利近零/反号时不稳定，必须同时报金额。

## 4. 策略行为

```python
t["hold_s"] = (
    pd.to_datetime(t.exit_time) - pd.to_datetime(t.enter_time)
).dt.total_seconds()

behavior = t.groupby(["account", "sym", "dorn"]).agg(
    hold_med=("hold_s", "median"),
    vol_med=("vol", "median"),
    vol_max=("vol", "max"),
    turnover=("vol", "sum"),
)
```

检查：

- 持仓时长与 target/horizon 的 realization curve 是否错配
- 高换手薄边是否被费用吞噬
- size 是否撞盘口深度
- 开盘/尾盘成交聚集
- 止盈/止损/超时结构
- REAL 与 SIM 的持仓、size、时机差

这些只解释行为差，不能替代逐决策配对。

## 5. 部署传导证据梯

证据强度可分为：

1. **活动量差**：完成交易数、成交手数、hitr；只描述活动
2. **结果质量差**：P&L/trade、持有、胜率、盈亏比、尾部；选择与执行仍混合
3. **近邻 cohort**：同品种/session/date/方向/窄时间桶；不是同一信号配对
4. **逐决策配对**：稳定 decision/order id、同一可见时点、目标方向/数量、委托/改撤/成交生命周期

只有第 4 层才拆 missed opportunity、queue/fill selection、latency、entry/exit markout，并要求 SIM 与 REAL 两侧金额桥闭合。

若 `enter_d/enter_reald` 是 as-of join 回填，只报告 tolerance、匹配率和“成交时点附近 SIM 信号环境”；不能冒充真实决策输入。

### 动态执行路径：只在它改变结论时展开

门槛、延迟或执行改动同时可能提高单笔优势、减少机会、改变成交选择和库存占用，不必强选一个解释。沿同一 decision/order 身份核对 signal → decision → arrival → partial/full fill → inventory → exit，保留未成交、部分成交及期末未平仓；固定价格基准、方向、单位、收益区间和实际可见时间。没有对应遥测只给可辨认的分段或界限，不把预测 alpha 当作已实现现金，也不凭成交样本恢复全体机会。

在固定时间窗、每机会至多一个等规模完整交易、无未成交费用且期末无库存的简化账中，`总净收益 = eligible机会数 × 完成比例 × 完成交易平均净收益`。这是口径一致时的汇总关系，不是可独立调整三个参数的因果模型。其他情形回到实际数量加权的逐笔账，包含部分成交、未完成库存估值和相关费用；机会数、订单数、成交笔数不能互换。

`signal alpha - pre-fill decay` 若已定义为成交后剩余 alpha，就不能再加一次 post-fill alpha；成交价收益已体现的 spread/impact 也不重复扣除。把不重叠的价格区间和显式费用与原账核对，预测值另列。若要解释门槛峰值或其移动，区分状态组成、信号筛选、成交选择、延迟衰减和成本的共同变化；只有有依据时才给翻转边界，并在 fresh 比较中检验，不预设倒 U 型或因漂亮解释放宽晋级规则。

## 6. 因子归因

有 `signals` 时用 `usecols + chunksize`，只载目标 account。

`top_fc` 是每个信号的签名贡献。观察性 P&L 分摊使用：

```text
factor_share = signed_weight / Σ|signed_weight|
factor_pnl = signal_pnl × factor_share
```

必须：

- 同时做全局与 per-symbol/session，但品种异质只生成假设
- 报 top family、符号稳定性、日期集中度和负贡献
- 明确 top_fc 是观察归因，不是 ablation 因果

要生成 keep/cut 候选，使用项目 FEE 框架：

```text
E1 观察贡献 × E2 leave-group-out 边际 × E3 孤立 IC
```

三角一致仍只够进入预注册 ablation；最终由 fresh 多窗 fixed evaluator 的经济增量裁决。

## 7. 科学容量

废弃只看 `capacity_replay.best_M` 的旧 `rec_M`：没有 size impact 时 net(M) 单调，常撞网格上限，不能说明可扩量。

当前项目的容量诊断示例（实际参数与晋级门槛须核对项目合同）：

```python
import analyze.capacity_replay as cr
sim = tr[tr.account.str.contains("_t") & ~tr.account.str.contains("ht")]
lots = cr.recommend_lots(
    sim, p=1.0, imp=0.5, ms=range(1, 26), n_boot=150
)
```

三道约束：

1. `M_edge`：impact-adjusted net(M) 的内部最优
2. `M_depth = p × P25(对手 L1 深度)`
3. 按交易日 bootstrap 的 M* 取保守 25 分位

`M_rec = min(edge_lo, M_depth)`，同时报 binding、日期数和当前部署手数。少于 3 天标低可靠。只有非锁仓、`M_rec` 明显高于当前量且经济性跨日稳定时，才形成扩量候选。

### 容量反事实边界

上述结果依赖冲击函数、可比样本和历史路径假设，不是已经验证的真实扩量反事实。自己的订单可能改变盘口、成交选择和后续价格；在固定历史行情中把手数改小，不能证明真实市场会恢复到原先状态。模型系数不变、无冲击 SIM 稳定，也不能排除这种反馈。

只有扩量后退化或自身冲击是当前 crux 时，补最小辨别证据：同一决策 cohort 的事前流动性/信号状态、自有委托/子单/改撤/成交时序、订单规模相对可见深度或同期流量，以及到场和成交后的方向对齐收益。保留未成交/部分成交，按既有配对规则处理。可比低参与率样本或缩量回放可用于挑战假设，但历史前后对比有状态混杂，回放依赖冲击模型，都不是自动确证；成交价格已包含的冲击不重复扣费。

不能区分自己与外部交易造成的变化时标 `unresolved`，提出最便宜的补证据动作，不把回测容量上限当作扩大真实资金、强制减量试验或重训的授权。

## 8. Action 排序

按“闭合金额影响 × 可控性 × 证据等级 ÷ 过拟合风险/实现范围”排序：

1. unresolved 最大：先补 pairing、订单生命周期、模型身份或跨日样本
2. 全 tick 与 SIM 预测都弱：模型/标签候选
3. 预测健康、SIM 经济性弱：策略/gate/持有/退出/成本
4. SIM 健康、REAL 弱：部署 telemetry/配对回放
5. 因子：观察归因 → FEE/ablation → fresh evaluator

只有需要正式实验交接时才补齐下列字段；普通归因只说明证据、边界及必要的辨别检查：

```text
evidence_scope / mechanism / editable_surface / fixed_fields
predicted_signature / falsifier / screen_split / verify_split
sample_floor / overfit_risk
```

单日收益不支持策略晋级；确定性故障可以凭可复现证据诊断。可实验的机制假设应有反证条件，普通算术或已验证操作无需制造实验。
