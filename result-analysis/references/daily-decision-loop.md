# Daily Decision & Research Loop

用于“深化日报图片、给出实盘运行建议、形成研究方向或把复盘接入研究循环”。先遵循通用 analysis contract；本文件补充日报的视觉、决策和研究接力合同。

## 1. 目标与边界

日报不是成绩单，而是一次受约束的决策循环。它必须依次回答：

1. 今天的数据与身份是否可信？
2. 相对同身份历史，什么真正发生了变化？
3. 当前实盘单元下一交易时段应保持、观察、诊断还是触发风控复核？
4. 最大且可修的损失位于预测、策略经济性还是部署传导？
5. 哪个最小实验最可能推翻当前解释？

默认只输出建议，不修改实盘配置、模型、手数、任务队列或研究日志，也不自动推送。日报不能凭单日 SIM 盈利新增实盘品种、切换模型、提高仓位或写 `PROMOTE`。

日报是盘后治理器，不是新的 alpha 源。它只建议 `symbol × session` 的运行状态；多空方向、价格、订单和手数继续服从已经验证并在盘前冻结的实时策略。

把三个时间尺度分开：

```text
下一交易时段：运行建议与风险触发器
未来 3–20 个同身份交易日：确认稳定性与机制
frozen evaluator × fresh split：研究候选的正式晋级或淘汰
```

## 2. 冻结当日与比较基线

先确定最新完整一日 bundle，记为 `D0`；再寻找最近 20 个交易日报，按最小受影响粒度拆成同身份 cohort。图中同时给：

- `D0` 点值、来源与样本数；
- 同身份 cohort 的日级中位数、P10–P90、正日率、最差日和 leave-one-date-out；
- 有效日期 cluster 数 `D`、累计交易/信号数 `n`、最大日贡献；
- 当前实盘状态、锁仓、SIM-only、回放和缺失标记。

不要用整段历史均值掩盖身份变化，也不要把单日交易笔数当独立样本数。比较基线不足时保留 `D0` 事实，但把结论降为 `OBSERVE`。

### 冻结品种角色

先恢复盘前已经批准的实盘运行卡或部署配置，再观察当天 REAL，最后读取 `detail.meta.recommend`。三者分别标记，不能并成一个“实盘推荐”集合：

| 角色 | 可信来源 | 能说明什么 |
|---|---|---|
| `PREAPPROVED_LIVE` | 盘前部署配置或上次人工批准的周运行卡 | 当前被批准运行的品种/session |
| `REAL_OBSERVED` | 当日 REAL 交易与订单事实 | 当天实际活动；不能反推盘前批准状态 |
| `POSTHOC_CANDIDATE` | `meta.recommend` 或盘后排名 | 报告候选；只能进入影子/周审 |

同一品种可有多个角色，图中都要保留。禁止把盘后赢家改写成盘前推荐，也禁止用当天实际交易集合替代全体已批准实盘集合。

### 数据就绪门

| 状态 | 条件 | 允许输出 |
|---|---|---|
| `READY` | 核心结构化文件、身份和关键口径完整；需要实盘建议时可恢复盘前运行卡 | 运行卡、归因与研究候选 |
| `DEGRADED` | 非关键字段缺失，主要事实仍可复算 | 带缺口的 `KEEP_CURRENT/WATCH/DIAGNOSE`；不新增实盘 |
| `BLOCKED` | bundle 不完整、身份混杂、会计桥异常或关键单位冲突 | 只给风险提示和修复测量的下一步 |

当 `BLOCKED` 时，首页标题直接写“证据不可用于调整实盘”，不要用空值、旧值或 PDF 视觉趋势补结论。

## 3. 每日图片包

每张图只回答一个决策问题。标题写结论，不写“指标概览”；副标题固定包含 `日期｜账户/模型身份｜session｜D/n｜证据标签`。图下保留 evidence strip：

```text
source / aggregation / identity / missing / causal boundary
```

默认生成以下逻辑图片；渠道受限时按顺序保留首页、实盘推荐品种卡和研究卡。渲染器可改变尺寸，但不得删减证据边界。先生成可复算的 card data，再渲染图片；图片不能成为新的事实源。

### 图 1：每日决策首页

一屏包含：

- 一句话决策：首要瓶颈、证据等级、现在做什么与不做什么；
- 数据就绪与身份 cohort；
- SIM 毛利−费用−净利的闭合桥，REAL 结果另栏；
- top-1 风险/机会及其金额影响；
- 下一交易时段的调整触发器和最小监控项。

首页不能用综合分数隐藏原始分量。若使用高/中/低优先级，旁边列出金额、样本、证据和干预风险。

### 图 2：品种 × session 运行矩阵

日盘、夜盘分开。每行一个 `symbol × session`，至少显示：

```text
current_live / locked / identity
SIM: pot, costcov, dret, tn, stability
REAL: pnl or dret, trades, hitr, evidence level
deployment gap status
recommendation / trigger / next check
```

按“当前实盘 → 风控异常 → 研究候选 → 其它”排序，不按当日收益榜排序。SIM 与 REAL 分栏；单位不一致时禁止共用轴或计算伪 capture。

### 图 3：逐品种深度复盘卡

对 `PREAPPROVED_LIVE ∪ REAL_OBSERVED` 的每个品种生成卡片；每个 session 再加入最多一个通过基础过滤的 `POSTHOC_CANDIDATE`。推荐候选不能只出现在总表，未入选的合法 universe 也要在附表列出过滤原因，防止只展示赢家。卡片用六个区域回答：

1. **结论与状态**：当前运行状态、建议、有效期和人工门禁；
2. **跨日经济性**：`D0` 对比同身份 cohort 的 pot/costcov/dret/tn；
3. **毛利与尾部**：gross−fee=net、P10/P50/P90、最差日与集中度；
4. **预测到交易**：L1 全 tick → L2 eligible → L3 SIM 完成交易，只画当前可得层级；
5. **REAL 传导**：活动、结果、近邻 cohort 或逐决策配对的实际证据梯级；
6. **下一步**：首要机制、预期签名、falsifier 和下个日报要收集的字段。

无 REAL 的候选显著标 `SIM-only`；没有 decision/order id 时，REAL 区写 `deployment gap unresolved`，不能画成可归因的漏斗。

### 图 4：SIM 与 REAL 双瀑布归因

生成两张独立的移动端卡，不得把 SIM→REAL 画成一条连续瀑布。两张图的 universe、单位和证据等级必须各自完整显示，柱长不得跨图比较：

1. **SIM 会计桥**：汇总实盘对标 SIM 账户的合法 cell，显示 `gross - modeled fee/rebate drag = net`、账户、日期、cell 数和 evidence level。`legacy_partial` 只能解释毛收益、模型化费损与净收益；latency、queue、markout、inventory、hedge、system 等不可观测项写 `N/A`。逐 cell 长图留在 PDF/审计附件，不进入 Telegram。
2. **REAL 结果与代理传导**：先单列全实盘观测桥 `gross - modeled cost = net`（`fact`），再单列 matched-cell 的 aggregate proxy（`diagnostic`）。明确 matched cells、SIM-only unmatched 数、ordered/filled/unfilled 聚合数量和代理假设；`execution/selection residual` 固定标 `UNRESOLVED`，不得改名为延迟、滑点、漏单或逆向选择。

两张卡均不得产生新增、减仓、扩量、切模或 promotion。若没有 REAL 观测，REAL 卡保留 `NO_LIVE_DATA` 与原因，不把缺失画成零。

### 图 5：研究方向与循环卡

只展示一个首要瓶颈和最多 3 个方向：top-1 在门槛允许时标 `MEASURE/TEST`，其余 `OBSERVE/PARK`。每个方向显示：

```text
evidence -> mechanism -> one editable surface
predicted L1/L2/L3/L4 signature -> falsifier
screen split -> fresh verify split -> human gate
expected impact / information value / effort / overfit risk
```

若测量、身份或配对未闭合，top-1 必须是补证据，不得用模型调参绕过不可观测性。

### 视觉证据规则

- 结论句带 `fact/diagnostic/hypothesis/unresolved/decision` 标签，并能从随图数据表复算；保留原始/派生列及单位。
- 当日点与历史分布并列，不只画累计曲线；零线、样本数、缺失和身份切点可见。
- 不用双 Y 轴制造相关性，不截断轴夸大变化，不用面积或颜色代表未经校准的概率。
- SIM 与 REAL 瀑布分图发送并标 `1/2`、`2/2`；不要合图暗示同 universe、逐决策配对或因果闭合。
- 颜色不是唯一编码；同时使用文字状态或形状。SIM、REAL、回放固定使用不同样式。
- 一页放不下就按 session/品种拆页，不缩小字号或删除边界说明。
- 漂亮但不能改变决策的图不进入推送包，可留在 PDF 附录。

## 4. 实盘运行建议状态机

日报给的是“当前单元如何运行”的受限建议，不是方向性买卖指令。每个建议必须包含：

```text
symbol_session / current_state / recommendation / evidence_tier
facts / uncertainty / why_now / valid_until
exposure_boundary / change_trigger / next_check / human_gate
```

允许状态：

| 建议 | 含义 | 日报门槛 |
|---|---|---|
| `KEEP_CURRENT` | 保持已批准配置与风险上限 | 无预声明触发器命中；不表示 edge 被再次确认或可以加仓 |
| `WATCH` | 当日异常或改善待跨日确认 | 单日、样本薄、身份未完全确认或证据冲突 |
| `DIAGNOSE` | 不扩量，优先查指定的预测/策略/部署层 | 跨日签名指向同一层，或 REAL/SIM 差异尚未配对 |
| `SHADOW_ONLY` | 仅 SIM/影子跟踪，不进入实盘 | 新候选、无 REAL、锁仓或未过周级资格门 |
| `RISK_REVIEW` | 建议人工复核暂停新开仓或降低风险 | 已命中预声明的数据完整性、会计、风险或运行故障硬触发器 |
| `WEEKLY_REVIEW` | 提交跨日周审，不改变当前部署 | 已满足周级候选检查的前置条件 |

以下状态不能由单日报告独立产生：

- `ADD_LIVE`：至少通过 weekly contract 的同身份、稳定性、样本、结构和 REAL 门槛，并经人工批准；
- `SCALE_UP`：还需 fixed evaluator、科学容量、现有风险限额和人工批准；
- `MODEL_SWITCH/PROMOTE/DISCARD`：只服从预注册 fresh evaluator 与项目验收门。

单日盈利最多维持 `KEEP_CURRENT` 或提升观察优先级；单日亏损通常是 `WATCH`，只有预声明硬触发器命中才进入 `RISK_REVIEW`。不得因一天亏损在盘后发明暂停阈值。报告不得建议具体手数，除非用户明确要求且容量、深度和风险证据已齐备。

### 新实盘候选

新候选先走 `SHADOW_ONLY → weekly eligible → 最小风险灰度 → monitored live`。周级资格沿用 weekly contract：同身份有效日、pot-first、稳定覆盖、累计 `tn`、非锁仓和 REAL 证据都必须披露。日报只更新状态和触发器，不重写门槛。

## 5. 从首要瓶颈生成研究方向

先按以下顺序路由，不把所有问题都解释成模型问题：

1. **Measurement**：身份、时间对齐、会计桥、decision/order 生命周期；
2. **Deployment**：同一决策的漏失、队列、成交选择、延迟与退出传导；
3. **Policy**：eligibility、fee gate、方向映射、持有、退出和显式成本；
4. **Model/Data**：标签、horizon、训练漂移、校准、特征族；
5. **Capacity/Risk**：深度、impact、集中度和尾部约束。

只有更高层证据已闭合，才向下一层提出改动。比如没有逐决策配对时，先补 telemetry，不用重训解释 REAL−SIM。

方向排序采用可解释的序数判断，不制造小数精度：

```text
优先级上升：可闭合损失金额大、证据强、可控、可逆、信息增益高
优先级下降：实现/算力大、搜索暴露多、后验切片强、干扰面多
```

同级时优先选择“最便宜且最可能推翻当前机制”的实验，而不是预期最好看的实验。研究并行只用于共享同一冻结 evaluator、但 editable surface 相互独立且预算已声明的 arms；一个 arm 内仍只改一个 surface。

每个研究方向输出：

```text
question / crux / evidence_scope / observations
mechanism / strongest_rival / editable_surface / fixed_fields
predicted_signature / falsifier
screen_split / verify_split / sample_floor
primary_metric / guardrails / search_exposure
expected_information_value / expected_deployable_impact
effort / reversibility / overfit_risk / stop_rule / history_check
status: MEASURE | TEST | OBSERVE | PARK | CLOSE
```

`expected_information_value` 和 `expected_deployable_impact` 默认用高/中/低及理由，不用未经校准的收益概率。命中项目关闭轴时写 `CLOSE/PARK`，除非新证据明确推翻旧前提。

研究状态受证据门槛约束：

- 1 个同身份日：只能 `OBSERVE/MEASURE`；
- 3–4 个同身份日且完成交易 `n≥100`：可形成 `TEST` 提案，但不自动启动；
- 至少 5 个同身份日期 cluster：可进入 Explore Opportunity，仍须预注册 fresh verify；
- `PROMOTE/REJECT`：只由 frozen evaluator、fresh split 与人工 gate 产生，不属于日报状态。

## 6. 闭环与写回提案

日报闭环固定为：

```text
D0 bundle + identity
  -> 可复算事实与历史偏离
  -> 受限实盘运行卡
  -> 唯一首要瓶颈
  -> top-1 可证伪假设
  -> cheap falsification / historical screen
  -> preregistered fresh verification
  -> human PROMOTE / REJECT / PARK
  -> 灰度部署与事后监控
  -> 新日报
```

日报建议若改变 universe、gate、size 或其它策略政策，变更后的数据必须标为新的 policy-conditional cohort，不能与旧政策直接合并后“自证”有效。若日报生成器、指标定义或 evaluator 本身改变，先做 A/A 与历史 replay，重新冻结 harness 后再比较研究 arms。

日报最后生成一个不自动落盘的 research handoff：

```text
observation_id / date / cohort / evidence_links
old_belief / new_evidence / updated_belief
next_experiment / owner_or_gate / due_condition
result_needed_to_advance / result_that_closes
```

只有用户明确要求持续跟踪时，才按项目已有格式写入 program、memory、TASK 或 review log；写前读取现有记录，链接原始 artifact，并保留失败与阴性结果。

## 7. 每日报告固定交付

按以下顺序交付：

1. 一句话决策与数据就绪状态；
2. 每日决策首页；
3. 品种 × session 运行矩阵；
4. 当前实盘与推荐候选的逐品种深度卡；
5. SIM 会计瀑布卡与 REAL 结果/代理瀑布卡；
6. REAL/SIM 的事实、边界和唯一首要瓶颈；
7. 实盘运行建议表；
8. top-1 研究方向与最多 2 个备选；
9. research handoff 与下个日报的调整触发器。

若用户只要推送图片，图片仍必须携带结论、身份、D/n、证据标签、触发器和边界；PDF 可保留完整数据表与附录。不得因为渠道简短而删掉 `SIM-only`、`unresolved` 或人工门禁。
