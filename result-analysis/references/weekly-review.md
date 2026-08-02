# Weekly Review Contract

用于周报、周复盘、下周模型/品种建议和定时周简报。先遵循通用 analysis contract；本文件只补充跨日报决策规则。

## 1. 冻结周级证据

- 每个日期先读 `READY manifest`，再读 `detail`、`winress`，仅在首要判断需要时按列读取 `trades`。PDF 只用于展示。
- 列出周一至周五实际找到的日报、缺失工作日、`phase`、bundle hash、REAL 账户和 `real_sim_account`。同一天只计一个一日窗。
- 用 manifest 的账户 `model_identity_hash`、`y_types`、配置身份和 benchmark 划分 `benchmark cohort`。身份或 benchmark 变化时拆组，不跨组聚合；无法恢复则标 `identity_unverified` 并降低结论等级。
- cohort 必须采用最小影响粒度：账户级模型身份变化才拆该账户；某一 `symbol × session` 的 fg/sg 或 gate 变化只拆该 cell，不得整日剔除未受影响的账户和单元。
- `final`、`sim_only` 和 `replay` 分栏。REAL 缺失不等于零；回放数据不能伪装成当日实盘。
- 有效完整日 `D` 是通过 manifest 校验且关键结构化文件齐全的独立一日 bundle 数。`D<3` 时只给观察，不给实盘主选。

## 2. Pot-first 模型选择

日盘、夜盘分别执行，不能把 session 合并：

1. 对每个 `account × session` 先确定跨日身份一致的共同稳定单元；再对每个日期取这些“品种×y_type”日内单元 `pot` 中位数。局部变更单元从模型总分的共同支持中排除，但其它单元仍计入该日。
2. 对同一 `account × session` 的日级中位数再取跨日中位数，作为周模型分数。
3. 用 `pot` 周分数选择主模型；同时报告正日率、最差日、`dnwin/dret/costcov/tn`，但不得用它们替换 pot 排名。
4. 完整列出每个 account 的 `y_type`。`t1_m`、影子或容量账户必须单列，不并入基础模型。
5. 日级并非独立同分布样本；披露有效日期数和身份 cohort 数。并列或身份不明时保持现有模型，不强行切换。

`pot` 缺失时只做运营回顾，禁止给出模型切换结论。

## 3. 品种资格与过滤

只在该 session 的主模型 cohort 内比较 `symbol × session`：

- 主排序：跨日 `pot` 中位数。
- 候选按自身当前 cell 身份计算；参数发生变化时，新旧 cell cohort 分开，不能把旧参数的 4 日与新参数的 1 日拼成 5 日。
- 稳定性：以全部 `D` 日为分母；`pot>0` 且 `dnwin>0` 至少 80% 完整日通过。某日缺行计为未通过，不缩小分母。
- 样本：累计 `tn<100` 只能观察。
- 结构：`locked` 不进入实盘主选。
- REAL：同期 REAL 成本后为负则降为“诊断”；无 REAL 明确写 `SIM-only`，最多给最小风险灰度或影子。
- 每个 session 最多一个新增实盘灰度和一个影子候选。不引用旧 `rec_M`，不建议具体手数。

单列“纯 pot 虚高项”：高 pot 但因低样本、锁仓、缺日、跨日不稳、REAL 为负或身份混杂被过滤的候选。

## 4. 归因与调整信号

- 先给 REAL、SIM 各自事实，再描述差额；无 decision/order id 和完整订单生命周期时写 `deployment gap unresolved`。
- 全周只选一个首要瓶颈。它必须同时满足：金额影响最大、可控、且证据等级最高；否则写 `mixed/insufficient`。
- 最多给 3 条动作。每条必须包含：机制、唯一 editable surface、保持不变项、下周可观察的预期信号、验证窗口和 `falsifier`。
- 调整只由预先声明的信号触发。例如：主模型周 pot 中位数转负、稳定覆盖跌破 80%、累计 tn 达标后 REAL 成本后仍为负。未触发则保持当前方案。
- 周简报是运行建议，不等于研究 `PROMOTE`。正式模型晋升仍需 fixed evaluator 和 fresh split。

## 5. 固定交付

按以下顺序输出，适合 Notion 与 Telegram：

1. 一句话决策
2. 数据覆盖与身份 cohort
3. T0/T1/T2 的日盘、夜盘 pot-first 对比，含完整 y_type
4. 下周运行卡：主模型、实盘灰度、影子、诊断/排除
5. 纯 pot 虚高项
6. REAL/SIM 事实与唯一首要瓶颈
7. 最多 3 条动作、预期信号和 falsifier
8. 证据边界

总长受渠道限制时，优先保留结论、关键数字、过滤原因和调整触发器，删背景说明，不删证据边界。
