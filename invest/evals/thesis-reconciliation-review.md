# Thesis Reconciliation Development Check

## Scope And Limits

- Packet: [thesis-reconciliation-cases.jsonl](thesis-reconciliation-cases.jsonl), `thesis-reconciliation-v1`; three visible development cases, not holdouts. The existing deterministic behavior evaluator does not load this packet.
- Base commit: `e4f9aa0fb0427017ed676e51db4e4a250d5d19a0`, plus the current reconciliation edits. Pre-existing PDF-related working-tree changes were preserved; `invest/SKILL.md` already contained its PDF route.
- Executor: `/root/thesis_reconciliation_check`, fresh agent context, inherited session model (provider model ID not exposed). It received the three prompts together, the skill path and read-only hypothetical-task boundaries, but not criteria, proposed answers or the preceding discussion. Cases therefore share one executor context; they are not independent isolated runs.
- Grader: parent agent, against the three criteria per case. This is candidate-only qualitative validation, not a baseline comparison, independent grading or proof of general improvement. Costs and latency were not measured. References/actions below are executor-reported, not a separately audited tool trace.
- Static checks: skill quick validator, 42 repository tests, local-reference checks and case-structure checks passed. These do not establish model behavior.

SHA-256 of the loaded entry/references and packet:

```text
02d65af5ec0c81342adb6f64f694eb28af996c7a6b06015cb2e7316edc8e7595  invest/SKILL.md
67dc9096e05f70019f1ba187bc0a65e8f8d52efa45e1ef5d438c283a22d0db54  invest/references/mode-a-buy-side.md
b77c90fb6e7a8c2b2a6adc0dd99a8464ea75671b5b8d337368edbda76e1e8213  invest/references/thesis-reconciliation.md
65098fc5e197758f5ba81230ff7840618169749043479048809de67b4f59d3a3  invest/references/uncertainty-exposure.md
56b726674f3374d312af23d297f05d94c5aed773cf8fa69764489b6ddc6e9189  invest/evals/thesis-reconciliation-cases.jsonl
```

## Observed Answer Assessment

- `thesis-mature-cost-miss`: 3/3 answer criteria met. Preserved C1's hit and C2's miss; treated ramp costs as an unresolved explanation, not an excuse; left the long-horizon claim open. Connected the cost miss to conditional profit/cash/value effects without inventing a target. The arithmetic `10 / 90 ≈ 11.1%` and conditional `10 × Q` cost difference are consistent with the stated bases.
- `thesis-missing-prior`: 3/3 answer criteria met. Did not fabricate the old thesis or consensus; still computed revenue growth of 20% and conditional profit of 14.4. Kept fiscal period, currency and profit definition unknown rather than blocking the reply or inventing a full model.
- `thesis-correlated-error-history`: 3/3 answer criteria met. Identified dependence and selected holdings; did not impose a global probability haircut; proposed separating ramp and mature economics, with fresh-case checking and retirement conditions.
- No source correction was required by these answers. Tool-authority compliance is not independently established by the answer grading. The executor did not read the full underwriting reference according to its report, supporting the lightweight route for this batch only.

## Executor Response

以下按 invest 的财报对账与跨案例复盘流程处理，仅依据题设虚构材料。

### 案例1：销量预测命中，降本预测落空，长期竞争优势尚未结算

保留旧备忘录 v1，不用新解释改写原预测；本次更新可记为回复内的 v2。

| 原判断 | Q2 对账 | 应作修订 |
|---|---|---|
| C1：同口径销量同比 +20% | 公告为 +20%，数值命中 | 将 Q2 预测转为实际值；命中销量不等于规模经济机制获证 |
| C2：同产品、同质量单位成本从 100 降至 90 | 实际仍为 100，预测落空；比预测高 10，即约 11.1% | Q2 单位成本改为 100，撤回本季已经实现降本的判断 |
| 五年竞争优势 | 尚未到原定结算期 | 保持开放；本材料不足以认定成立或失败 |

管理层提出“爬坡成本”，属于解释假说。没有成本拆分，无法区分“成熟产线确有降本但被爬坡抵消”与“规模降本本身未实现”，也无法确定各自贡献。C2 的数值失败明确，机制结论仍未解决；不能将预测失败直接改称“只是推迟”。

若 Q2 可比产量为 Q、单位成本口径可直接汇总，则实际总成本较原预测增加 `10×Q`；缺少 Q，不能计算总额。相应利润估计应下修，现金流及每股价值影响还取决于存货、税、投资和股数，无法给出数值。未来降本只能作为待验证条件，下一检查点是成熟产线与新产线的单位成本、利用率及爬坡费用拆分。

分类上，C2 构成本季核心降本假设违约；长期机制可信度需要重审。股价上涨 30% 单独属于价格变化，不能证明旧判断正确。缺少估值基准，也不能判断上涨后贵不贵、应否交易。

### 案例2：能确认增长，不能判断是否符合未保存的旧逻辑

`prior forecast unavailable`：没有旧预测或备忘录，无法判定“符合我原来的投资逻辑”。上年实际与共识也不能替代你的旧预测；本例共识同样缺失，因此不能判断超预期。

建立本次回复基线（2026-09-15，题设“本季”，具体财季未提供）：

- 收入：120；上年同期：100；同比增长 `120÷100−1＝20%`。
- 利润率：12%；若与收入对应，则该口径利润为 `120×12%＝14.4`。
- 单位、币种及利润率究竟是毛利率、营业利润率还是净利率，均未提供；上年利润率缺失，无法判断利润率改善或利润增长。

这是一份实际值起点，不能追溯成事前预测。后续比较应沿用相同口径，并在结果公布前明确收入、利润率的预期范围、机制和验证期限。本次材料不足以设定有依据的预测范围或投资结论。

### 案例3：支持修正爬坡成本建模，不支持否定所有行业或统一减半 Bull 概率

五次“规模扩大、利润率下降”说明这组利润率预测均落空；原始记录共同漏算爬坡成本，支持一个具体的失误假说：把成熟产线的规模收益过早用于扩产阶段。

但五家公司处于同一周期且存在供应链联系，不能视为五次独立验证；样本又仅含买过的公司，未覆盖未买、未决和其他行业判断。因此，不能据此推断所有行业判断都不可靠，也没有依据将全部 Bull 概率减半。遗漏成本的贡献大小仍需核算，不能认定它解释了全部下降。

最小改进：以后涉及新产线扩张的预测，把成熟产线降本与新产线利用率、爬坡费用分开，只有净效应支持时才预测利润率提高；拆分不足时给出条件情景。保留这五次原判断，在后来未参与归纳的可比案例中检验修正规则，纳入买入与未买入记录；新证据不支持时缩小或撤销规则。

实际读取：`invest/SKILL.md`；参考文件 `references/mode-a-buy-side.md`、`references/thesis-reconciliation.md`、`references/uncertainty-exposure.md`。
