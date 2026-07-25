# Result Analysis Contract

所有 Quick、Standard、Deep、Tuning 分析都遵守本合同。

## 1. 输入与优先级

默认目录：`/home/x/www/results/YYYYMM/`。

| 文件 | 粒度 | 用途 | 优先级 |
|---|---|---|---|
| `detail_<b>-<e>.json` | 品种×session 结构化明细 | Standard/Deep 入口；含 sim/real/gap/consensus/when_daily | 1 |
| `winress_<b>-<e>.csv` | s/t/account/y 聚合 | Quick 入口与聚合口径校验 | 1 |
| `winresd_<b>-<e>.csv` | s/t/account/y/date | 跨日中位数、正日率、尾部与集中度 | 2 |
| `trades_<b>-<e>.csv` | SIM+REAL 逐笔 | P&L、持仓、方向、size、成交时机 | 2 |
| `signals_<b>-<e>.csv` | 逐信号 | 全 tick/eligible 预测、margin、因子 | 按需 |
| `capacity_<b>-<e>.csv` | 容量网格 | 仅作辅助；核对生成方法 | 按需 |
| `res_<b>-<e>.pdf` | 图表 | 定位指定页或结构化数据缺失 | 最后 |
| `/data/logs/result/cron_YYMMDD.log` | 运行日志 | 判断实盘比对/数据生成是否跳过 | 异常时 |

先读 `detail.meta.note`。它对代理量、回填和配对边界的声明优先于本参考。字段不存在时降级，不凭空补值。

## 2. Bundle 与身份检查

每次记录：

```text
date_range / daily_or_weekly / files / account / symbol / session
code_commit_dirty / account×y / fg / sg / target / horizon / feature_version
model_path / params_mtime / SHA256 / missing_or_backfilled_fields
```

- 日报通常是相邻日期的一日窗；排除周报和 `_trade` 重复文件，防止重复计权。
- 不硬编码 t0/t1/t2 的 feature/target 映射。用当前日报的 `account×y`、params 和 artifact hash 确认。
- 模型、标签、horizon、feature、gate 或状态机不同的日期拆成不同 cohort。
- 报告时模型身份无法恢复，写 `identity_unverified`，跨日结论降一级。
- 若实盘字段缺失或 bundle 不完整，检查对应 `/data/logs/result/cron_YYMMDD.log` 中的 `未拿到`、跳过和回填告警，并把生成失败与真实零值分开。

## 3. 指标层级

### 研究与经济裁决

- 存在项目冻结的 held-out `pot` 时，以它作为正式 edge 北极星。
- `costcov/dret/tn` 是核心辅助；`avgnwt/pot_min/pot_max` 解释单位质量和尾部。
- 旧 bundle 没有 `pot` 时，可用 `dret/dnwin/avgnwt/wdr/tn` 做运营复盘，但不能据此正式 PROMOTE。
- `prec/ic/R²/hit` 只诊断预测层，不能替代成本后经济裁决。

### 跨日稳定性

优先报告：

```text
日级中位数 / 正日率 / P10-P90 / 最差日
最大日贡献 / 去掉最大日后的结论 / leave-one-date-out
模型身份 cohort 数 / 有效日期 cluster 数 / 样本数
```

不要让交易笔数最多的一天吞掉其它日期。相邻日与重叠标签并非独立样本，披露这一点。

### 重尾

P&L、盘口深度、`avgnwt`、持仓时长和 size 使用 median/P25/P75/P90，不仅报 mean。比例分母接近零或反号时，报告 numerator、denominator 和差值，不强调 ratio。

## 4. Quick 聚合

先执行：

```python
import pandas as pd
w = pd.read_csv(path).reset_index(drop=True)
w["ex"] = w["account"].str.split("_").str[0]
```

### 交易所与账户

```python
summary = w.groupby("ex").agg(
    n=("dret", "count"),
    dret_sum=("dret", "sum"),
    pos=("dret", lambda x: (x > 0).sum()),
    dnwin_sum=("dnwin", "sum"),
    avgnwt_median=("avgnwt", "median"),
    ic_median=("ic", "median"),
)

account = w.groupby(["ex", "account"]).agg(
    n=("dret", "count"),
    dret_sum=("dret", "sum"),
    dnwin_sum=("dnwin", "sum"),
    avgnwt_median=("avgnwt", "median"),
)
```

账户前缀通常映射交易所：`dce_*`、`shfe_*`、`gfex_*`。先查看 `pd.crosstab(w.account, w.y)`；不同账户常是不同 feature/target 合同，不是同一策略复刻。

### 品种与 session

```python
symbol = w.pivot_table(
    index="s", columns="account", values="dret", aggfunc="sum"
)
symbol["SUM"] = symbol.sum(axis=1)

session = w.pivot_table(
    index="s", columns="t", values="dret", aggfunc="sum"
)
```

同时列 top/bottom、样本数、日夜分歧、锁仓和 SIM-only 标记。`win_r=100%` 但样本极少、`sharpe=NaN` 或高 dd/低 |dret| 都属于边界样本。

相关性只作诊断：

```python
for col in ["avgnwt", "win_r", "prec", "ic"]:
    print(col, w[col].corr(w["dret"]))
```

披露样本数和选择范围。IC 与 dret 相关性弱或反向不等于模型无信息；它仍需在对应证据层解释。

### 跨账户同号

```python
consensus = w.groupby(["s", "t"]).agg(
    n_account=("account", "nunique"),
    n_pos=("dret", lambda x: (x > 0).sum()),
    n_neg=("dret", lambda x: (x < 0).sum()),
    dret_sum=("dret", "sum"),
)
```

只称“结果同号/稳定性先验”。在账户的 target、feature、gate、训练窗不可比时，不把它解释成独立重复验证，更不能称“真信号”。单账户交易所不输出 consensus 结论。

## 5. SIM、REAL 与部署口径

- SIM 账户通常为 `*_t*` 且不含 `ht`；REAL 示例为 `dce_ht1028`。实际账户以 bundle meta 为准。
- REAL `dret` 可能由报告代码回填；原始 REAL 没有可认证模型预测时，`prec/ic` 应为空。
- 锁仓品种是结构上限，必须单列；低 REAL 量不自动解释成执行故障。
- `meta.recommend` 中 `has_real=false` 只可写 “SIM-only 候选”。

必须分开：

```text
dret_capture = REAL dret / SIM dret       # 归一化结果比
pnl_capture  = REAL pnl  / SIM pnl        # 原始金额比
trade_ratio  = REAL完成交易数 / SIM完成交易数
hitr         = 成交量 / 委托量
```

- `trade_ratio` 不是机会 coverage、漏单率或 fill rate。
- `hitr<1` 只说明未全量成交，不能区分撤单、排队、风控、行情离场或锁仓。
- 没有稳定 decision/order id 时，capture 只描述结果差；不要计算 `capture/trade_ratio` 并称为 adverse selection。
- `enter_reald-enter_d` 的单位是 dfactor 预测兑现差，不是 tick、价格或滑点。

## 6. 证据标签

给每个结论标一个等级：

| 标签 | 含义 |
|---|---|
| `fact` | 直接字段、可复算聚合或闭合会计关系 |
| `diagnostic` | 有选择条件的预测/策略代理 |
| `hypothesis` | 有机制与 falsifier，但尚未 fresh 验证 |
| `unresolved` | 当前数据不能区分原因 |
| `decision` | 已通过项目指定 fixed evaluator/人工验收 |

严格使用以下句式：

```text
观察：REAL 完成交易数低于 SIM（fact）
边界：两个样本未逐决策配对
假设：排队或风控可能减少执行（hypothesis）
需要：decision id + 委托/改撤/成交生命周期
```

## 7. 最低输出

即使是 Quick，也输出：

1. 日期、输入、身份和缺失
2. 账户/品种/session 表
3. 首要观察与证据等级
4. 因果边界
5. 下一步最小验证

纯 review 不落盘。只有用户明确要求持续追踪时，才更新 review log；写入前先读现有格式。
