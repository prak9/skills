---
name: invest
description: Generate source-backed buy-side equity research memos from a ticker — investment view, SEC/IR-backed financial analysis, industry chain, competition, SOTP/relative valuation, Bull/Base/Bear scenarios, catalysts, risks, and monitoring dashboard — with built-in specialist lenses for Bayesian intrinsic-vs-implied growth valuation, GF-DMA trend-health scoring, Serenity-style news-to-alpha translation, and TAM-Adj-PEG growth-adjusted valuation. Use when the user asks to analyze a stock or ticker, create a buy-side memo, investment committee note, or fund-manager-style company analysis, or explicitly asks for Bayesian valuation / intrinsic vs implied growth, GF-DMA / DMA-ATR trend health, news-to-alpha / small-cap beneficiaries, or TAM-Adj-PEG.
---

# Invest

## Core Principle

Start with the investment decision, not company background or news summary. Every mode in this skill converts an input (ticker, news item, or explicit framework request) into a decision-useful artifact: a thesis, a probability, a score, or a valuation band — always with the evidence that could prove it wrong.

Treat every output as research analysis, not personalized investment advice. Verify current prices, market cap, filings, estimates, valuation multiples, earnings calls, investor presentations, and catalysts from reliable current sources before making time-sensitive claims. Do not invent unavailable data — mark it `未核验` (unverified) and say what source would confirm it.

## Which Mode To Use

| Trigger | Mode |
| --- | --- |
| "analyze this ticker", "buy-side memo", "investment committee note", or any bare ticker/company request | **Mode A — Buy-Side Equity Research Memo** (default) |
| explicit ask for Bayesian valuation, intrinsic vs implied growth, growth-hypothesis probabilities, posterior updates, FOMO vs fundamentals | **Mode B — Bayesian Intrinsic Growth Valuation** |
| explicit ask for GF-DMA, DMA/ATR trend health, price-to-DMA divergence, escape risk | **Mode C — GF-DMA Health Index** |
| user shares news, a product launch, a procurement/supply-chain signal, or asks for alpha hypotheses / small-cap beneficiaries / "news to financial statement" translation | **Mode D — Serenity Alpha (News → Alpha)** |
| explicit ask for TAM-Adj-PEG, TAM-supported valuation, runway-adjusted PEG, quality-adjusted growth valuation | **Mode E — TAM-Adj-PEG** |

Do not trigger Modes B, C, or E from a bare ticker or a generic "analyze this stock" request — those default to Mode A. Mode A may pull in B, C, D, or E as sub-sections when they sharpen the decision (see "Cross-Mode Use" under Mode A); do not force all four into every memo.

## Shared Source Discipline

Applies to every mode.

Prioritize primary and current sources, in order: SEC filings or local exchange filings; company IR website, earnings releases, investor presentations; earnings call transcripts and official guidance; exchange announcements and regulatory filings; industry associations and credible third-party data; reputable financial data providers and mainstream financial media.

For every important figure or claim, cite the source, document type, filing/document date, access date, and section/page when available. Distinguish reported facts, management guidance/commentary, market consensus or third-party estimates, and analyst inference. If a number cannot be verified, mark it `未核验` and state what would confirm it.

```text
Source: FY2025 Form 10-K, Item 7, filed 2026-02-21, accessed 2026-06-12.
Source: Q1 FY2026 Form 10-Q, Note 15 Segment Information, filed 2026-05-03, accessed 2026-06-12.
```

If filings cannot be retrieved, say: `未能核验原始 SEC filing，本部分基于可获得资料，需后续人工复核。`

**Optional SEC data assist** (U.S.-listed companies only): use SEC filings as the factual baseline for reported fundamentals and management disclosure when available — prioritize the latest `10-K`, `10-Q`, `8-K`, and for foreign private issuers `20-F`/`6-K`, using XBRL data when available. Use current browser/SEC access first; use `edgartools` only when already available, and only install packages or configure SEC identity when the user explicitly authorizes it with a real identity. Use SEC data to anchor revenue, segment revenue, margins, EPS, free cash flow, capex, debt, cash, share count, dilution, buybacks, SBC, customer concentration, backlog/order language, pricing, capacity, inventory, MD&A, and risk-factor language. Never substitute SEC data for current market data, forward multiples, consensus revisions, TAM estimates, market share, technical/price data, option activity, or catalyst calendars — keep reported facts separate from forecasts and market estimates, and cite the filing form and date.

## Mode A — Buy-Side Equity Research Memo (default)

### Defaults

Required input: a ticker or clearly identifiable listed company. If ambiguous, identify the most likely company and state the assumption; ask only when multiple candidates are genuinely plausible and the wrong choice would change the analysis.

Unless the user specifies otherwise: language Chinese; depth deep version; horizon 12-month primary view with 3-6 month catalyst tracking; style buy-side fundamental research memo; valuation SOTP when segment structure matters, otherwise relative valuation/DCF/P-E/EV-EBITDA/P-FCF/industry-specific methods; scenarios Bull/Base/Bear with probability weights and implied upside/downside.

### Workflow

**1. Define company and research boundary.** Company name, exchange, ticker, fiscal year, reporting currency, primary business, segment structure, latest filings, latest earnings release/call, latest investor presentation, key disclosure limits.

**2. Write the executive investment view first.** Open with: rating bias (Buy/Hold/Sell/Avoid/Watchlist); 12-month target-price range (Base/Bull/Bear); current price and implied upside/downside when available; core thesis in 3-5 sentences; key debate and variant perception; what the market may be missing; the thesis breakpoint that would force downgrade, exit, or re-underwriting. If price/target inputs are unavailable, state the gap and give a qualitative view instead of false precision.

**3. Map industry chain and profit pool.** Value-chain position, suppliers, customers, pricing power, where the profit pool sits, scarce resources, and whether the company sits in a strong or weak value-chain position.

**4. Analyze competition and moat direction.** Direct competitors, substitutes, potential entrants, bargaining power, market-share direction, margin differences, brand/channel/scale/network/data/R&D advantages, and whether the moat is widening or narrowing.

**5. Read financial statements like a buy-side analyst.** Revenue mix, segment profitability, gross/operating margin, R&D, SG&A, operating and free cash flow, capex, inventory, receivables, deferred revenue, debt, cash, SBC, buybacks, dilution, guidance. Focus on what changes the thesis: acceleration/deceleration, margin quality, working-capital stress, capital intensity, accounting quality, and whether guidance confirms or contradicts the story.

**6. Identify 3-7 key value drivers.** Pick the variables that truly drive valuation (units, ASP, ARPU, NRR, users, backlog, book-to-bill, utilization, gross margin, take rate, inventory cycle, customer concentration, capex intensity, credit quality, regulatory cost). For each: why it matters, past trend, market expectation, management guidance, valuation sensitivity, and the metric that would confirm or falsify the thesis.

**7. Build valuation and scenarios.** Use SOTP when segments deserve different multiples/growth (per segment: revenue, growth, margin, comparables, multiple, value range, premium/discount rationale). Otherwise use the method that fits the business model: EV/Revenue, EV/EBITDA, P/E, P/FCF, DCF, NAV, normalized earnings, or milestone/option-style valuation. Always include Bull/Base/Bear scenarios with assumptions, probability, revenue growth, margin, multiple, target price, implied return, and trigger conditions; report probability-weighted target value and risk/reward when data allows.

**8. Challenge the thesis.** Actively argue against the conclusion: where the thesis can be wrong, what consensus may be too optimistic about, what risks are unpriced, which metrics would break the thesis, and what would force a downgrade or removal from the watchlist.

Apply this investment-adapter check directly: classify the asset as *mean-reverting* (price oscillates around a fundamental anchor — fade extremes), *paradigm-shifting* (the anchor itself is moving — extrapolation can still be too conservative), or *mixed*. State what consensus believes and what the current price already embeds. Then require a divergent view that is (a) more accurate than consensus on a checkable dimension, (b) not already priced in, (c) executable given available instruments and liquidity, and (d) bounded by an explicit **edge half-life** (how long the mispricing plausibly persists before it closes or the informational edge decays) and an explicit **falsifier** (the observation that proves the divergent view wrong). Cover fundamental, valuation, competition, cycle, regulation, technology-substitution, management-execution, accounting-quality, liquidity, FX, and macro risk where relevant.

**9. Track catalysts and build the monitoring dashboard.** List next 3-6 month catalysts (earnings dates, investor days, product launches, regulatory nodes, industry conferences, major contracts, M&A progress, capacity ramps, price changes, guidance updates, index changes, capital-return policy changes) with time window, event, market expectation, likely impact direction, and tracking metrics. End with a dashboard of the most important filings, operating metrics, management comments, and falsification points.

### Cross-Mode Use

Pull in another mode as a sub-section only when it sharpens the decision — do not force all of them into every memo:

- **Mode D (Serenity Alpha)** when the thesis depends on news, product launches, procurement signals, supply-chain changes, or market misclassification — translate the news into observable demand and financial-statement impact.
- **Mode B (Bayesian Intrinsic Growth Valuation)** when the key question is whether intrinsic 3-5 year growth probability is above or below market-implied growth.
- **Mode E (TAM-Adj-PEG)** when valuation depends on high growth, TAM runway, growth duration, and business quality rather than a simple PEG.
- **Mode C (GF-DMA Health Index)** when the user asks whether the current trend or entry point is healthy, or when price/DMA/ATR and estimate-revision data are available.

### Output Template

```markdown
# [Company / Ticker] Buy-Side Equity Research Memo

## 0. Executive Investment View
- Rating Bias:
- 12M Target Price Range:
- Current Price:
- Implied Upside / Downside:
- Base / Bull / Bear Case:
- Core Thesis:
- Key Debate:
- What the Market May Be Missing:
- Thesis Breakpoint:

## 1. Company Snapshot
- Business Overview
- Revenue / Segment / Geography Mix
- Customer Profile
- Reporting Currency And Fiscal Year
- Latest Source Set

## 2. Industry Chain Position
- Value Chain Map
- Profit Pool
- Bargaining Power
- Secular Drivers
- Cyclical / Structural Risks

## 3. Competitive Landscape
- Key Competitors
- Market Share Direction
- Moat Assessment
- Margin Comparison
- Threats And Substitutes

## 4. Financial Statement Deep Dive
- Revenue And Segment Trends
- Gross Margin And Operating Margin
- Cash Flow, Capex, And Working Capital
- Balance Sheet, Debt, Cash, Dilution, SBC
- Guidance And Management Commentary

## 5. Key Value Drivers
- Driver 1
- Driver 2
- Driver 3
- Valuation Sensitivity

## 6. SOTP / Valuation
- Segment Or Business-Line Valuation
- Comparable Companies And Multiple Assumptions
- Net Cash / Debt And Dilution Adjustment
- Implied Equity Value And Target Price

## 7. Bull / Base / Bear Scenarios
| Scenario | Probability | Core Assumptions | Target Price | Implied Return |
| --- | ---: | --- | ---: | ---: |
| Bull | | | | |
| Base | | | | |
| Bear | | | | |

## 8. Variant Perception
- Where Consensus May Be Wrong
- What Is Underappreciated
- What Would Break The Thesis
- Edge Half-Life And Falsifier

## 9. Catalysts: Next 3-6 Months
- Event
- Timing
- Market Expectation
- Tracking Metrics

## 10. Key Risks
- Fundamental Risks
- Valuation Risks
- Competitive Risks
- Regulatory Risks
- Thesis Breakpoints

## 11. Monitoring Dashboard
- Metrics To Track
- Filing Items To Review
- Management Commentary To Watch

## 12. Source List
- SEC / Exchange Filings
- Earnings Calls And IR Materials
- Industry And Market Sources
- Access Dates
```

### Quality Bar

Lead with the investment conclusion. Support each core judgment with data, source documents, or explicit reasoning. Do not replace analysis with news summaries. Do not extrapolate historical growth mechanically. Show valuation assumptions, not only a target price. Include Bull/Base/Bear scenarios and reverse thesis testing. Make all unverifiable data and missing inputs explicit. Keep the memo decision-useful, professional, and concise enough for buy-side discussion.

## Mode B — Bayesian Intrinsic Growth Valuation

Use when the user explicitly asks for Bayesian valuation, intrinsic vs implied growth, growth-hypothesis probabilities, posterior updates, or FOMO vs fundamentals. For a generic ticker or broad stock memo, use Mode A instead.

Do not classify company news as simply bullish or bearish. Translate every company-specific data point into a probability update for future 3-5 year revenue growth, margin, TAM, market share, valuation multiple, and market sentiment — then compare the resulting intrinsic growth speed with the growth already implied by current market value.

### Required Inputs

Use whatever the user provides and clearly mark missing variables: company fundamentals (revenue scale, margins, FCF, ROIC, balance sheet, customers, moat, pricing power); industry cycle (demand growth, supply-demand gap, inventory/order cycle, price trends, policy, downstream capex); revenue and growth (historical growth, guidance, backlog, book-to-bill, organic growth, ASP, shipment volume); TAM and TAM growth (current TAM, future TAM CAGR, penetration, market share, new-market expansion); valuation (EV/Sales, EV/EBITDA, P/E, FCF yield, PEG, historical/peer percentile, implied growth); share-price trend (1M/3M/6M/12M and post-earnings returns, drawdown/rebound, volatility, volume, relative performance vs sector/index); market FOMO (share-price move, options activity, social heat, analyst revisions, theme crowding, narrative strength); new information (orders, customers, products, pricing, policy, competition, capacity, earnings, guidance).

### Growth Hypotheses

| Hypothesis | Label | 3-5Y revenue CAGR | Suggested midpoint |
| --- | --- | --- | ---: |
| H0 | contraction | <0% | -5% |
| H1 | mature slow growth | 0%-5% | 2.5% |
| H2 | steady growth | 5%-12% | 8.5% |
| H3 | high-cycle growth | 12%-25% | 18.5% |
| H4 | structural breakout | 25%-50% | 37.5% |
| H5 | platform expansion | >50% | 60% or scenario-specific |

### Workflow

**1. Establish the prior.** Assign initial probabilities to H0-H5 using fundamentals, industry cycle, TAM, historical growth, competitive position. Prefer a conservative prior when evidence is incomplete — market excitement alone does not justify H4 or H5.

**2. Classify new information by variable.** Which of revenue growth, margin, TAM, market share, competitive structure, cash flow, valuation multiple, or FOMO sentiment does it affect? If it mainly affects market attention, update multiple and FOMO, not intrinsic growth.

**3. Bayesian update.** Write the update chain as `observed signal -> latent growth variable -> rival explanation -> disclosure or measurement lag` before changing probabilities. Cluster observations sharing one underlying cause (orders, supplier backlog, management commentary, and analyst revisions triggered by the same demand event are not independent confirmations). Raise H3/H4/H5 if the information is genuinely consistent with them; avoid over-updating long-term growth on cyclical, one-off, or backlog-timing signals; if it only strengthens narrative or trading enthusiasm, raise FOMO/multiple risk instead. If competition, regulation, structure, or regime change breaks the old mechanism, rebuild the prior and likelihood interpretation while keeping H0-H5 as CAGR bins; if 3-5 year revenue CAGR stops being a meaningful target (entity or reporting basis changed), mark the framework inapplicable rather than forcing an update. Show prior -> likelihood interpretation -> posterior with ranges, not decimal-level false precision.

**4. Calculate weighted intrinsic growth.** Use the posterior probabilities and midpoint table above; report a range.

**5. Reverse-engineer market-implied growth.** Infer the growth embedded in current valuation from market cap/EV, revenue, margin, FCF margin, multiple, and discount-rate assumptions. Treat implied growth as an inverse problem, not a unique observable — the same price is consistent with different combinations of growth duration, margins, discount rates, dilution, and terminal multiples; show the joint sensitivity. If exact data is unavailable, state the missing inputs and give a qualitative bracket instead of inventing numbers.

**6. Compare intrinsic vs implied growth.**

| Comparison | Valuation state |
| --- | --- |
| intrinsic growth > implied growth | undervalued |
| intrinsic growth roughly equals implied growth | fair value |
| implied growth > intrinsic growth, but cycle still accelerating | expensive but tradable |
| implied growth far above intrinsic growth and FOMO is extreme | bubble-like |

**7. Measure price-growth divergence.** Compare recent share-price return, market-cap expansion, and multiple expansion with changes in revenue CAGR, guidance, backlog, margins, and posterior probabilities. Separate fundamentals-driven rerating from liquidity/theme-crowding/short-squeeze/index-flow/FOMO-driven rerating.

| Price move vs intrinsic-growth update | Divergence signal |
| --- | --- |
| price return materially below improved posterior growth / implied growth still below intrinsic growth | price lagging fundamentals |
| price return and multiple expansion roughly match posterior growth improvement | aligned |
| price return or multiple expansion exceeds posterior growth improvement | price ahead of fundamentals |
| rapid price rise, multiple rerating, little/no posterior intrinsic-growth improvement | severe divergence / FOMO risk |

When price is ahead of intrinsic growth, reduce confidence in long-term margin of safety even for a high-quality company. When price lags intrinsic growth, identify the catalyst needed to close the gap.

**8. Build a verification path.** Define the time window and concrete indicators that validate or falsify the model: revenue growth/guidance revisions, backlog/book-to-bill/orders/lead times, ASP/shipment volume/utilization/capacity expansion, gross margin/operating leverage/FCF conversion, TAM expansion evidence, market-share gain or loss, peer/customer/supplier corroboration, analyst revision breadth and narrative crowding.

### Output Template

```markdown
## 1. 公司一句话定位
说明公司到底是什么，以及增长由什么驱动。

## 2. 当前增长假设概率表
| 假设 | CAGR 区间 | 先验概率 | 更新后概率 | 核心理由 |
| --- | --- | ---: | ---: | --- |
| H0 衰退型 | <0% |  |  |  |
| H1 低速成熟 | 0%-5% |  |  |  |
| H2 稳定成长 | 5%-12% |  |  |  |
| H3 高景气成长 | 12%-25% |  |  |  |
| H4 结构性爆发 | 25%-50% |  |  |  |
| H5 平台级扩张 | >50% |  |  |  |

## 3. 加权内在增长速度
给出未来 3-5 年收入 CAGR 的加权区间和关键假设。

## 4. 市场隐含增长速度
反推当前市值/估值倍数隐含的增长率；若数据不足，列出需要补齐的数据。

## 5. 股价走势与内在增速背离
比较 1M/3M/6M/12M 股价、相对行业/指数表现、市值和估值倍数变化，与收入增速、指引、订单、利润率和 posterior 增长概率变化是否匹配。
给出结论：股价落后基本面 / 股价基本匹配基本面 / 股价领先基本面 / 严重背离且 FOMO 风险上升。

## 6. 新信息的贝叶斯更新
说明信息影响的变量、在各增长假设下的相容性，以及 posterior 变化。

## 7. 估值状态
在 低估 / 合理 / 高估但可交易 / 泡沫化 中选择一个，并解释为什么。

## 8. 上行空间
说明需要哪些收入、利润率、TAM、市占率或倍数条件才有上行。

## 9. 下行风险
列出增长、利润率、竞争、周期、估值、FOMO 和流动性风险。

## 10. 验证周期
说明应在几个季度内验证，以及每个阶段看什么。

## 11. 关键跟踪指标
列出最重要的财报、订单、价格、产能、客户、股价相对表现、成交量、波动率、估值分位和情绪指标。

## 12. 仓位建议
用观察 / 小仓试错 / 验证后加仓 / 只交易不投资 / 降级或退出 等条件化表述，避免个性化投资指令。

## 13. 一句话结论
用一句话总结内在增长、市场隐含增长与股价走势之间的差异。
```

### Style Rules

Start from observable demand changes, not surface narrative. Translate demand into revenue, profit, TAM, and valuation impact. Look for underpriced shovels, bottlenecks, second-position winners, hard manufacturing, and critical supply-chain nodes. Separate intrinsic growth updates from FOMO and multiple expansion. Explicitly measure whether price movement is leading, matching, or lagging the intrinsic-growth update. Distinguish structural growth from cyclical rebound or one-time order timing. State uncertainty, missing data, and falsification conditions clearly.

## Mode C — GF-DMA Health Index

Use when the user explicitly asks for GF-DMA, DMA/ATR trend health, price-to-DMA divergence, escape risk, or whether a price trend is fundamentally supported. Do not trigger from a bare ticker or generic stock-analysis request.

Evaluate whether a stock's current price trend is supported by fundamental speed and moving-average structure: is the trend supported by revenue growth, profit growth, estimate revisions, and the 20/50/100/200DMA system?

### Required Inputs

Price/technical: latest price, 20/50/100/200DMA, ATR20, 5-day price change, and 20/50/100/200-day price changes or historical prices. Fundamental: latest quarterly revenue, EPS, gross margin/gross profit, next-quarter guidance, consensus revenue/EPS estimates, 30-day estimate revisions. Preferred sources: company IR releases/presentations, earnings calls, Yahoo Finance historical prices/analysis, TradingView technicals/estimates, Barchart technical analysis, Seeking Alpha estimates, Koyfin, FactSet, Bloomberg, TIKR, or Visible Alpha. SEC filings can improve the fundamental side (see Shared Source Discipline) but never the technical or revision modules — price, DMA, ATR20, 5-day slope, consensus estimates, and 30-day revisions still require market-data/estimate sources. If a required field is missing, name it and use the simplified formula only when appropriate.

### Calculation Workflow

**1. Fundamental speed.**

```text
G_f = 0.35*G_Revenue + 0.25*G_GrossProfit + 0.30*G_EPS + 0.10*G_Revision
```

`G_Revenue = next-quarter revenue guidance / latest-quarter revenue - 1`; `G_GrossProfit` and `G_EPS` analogous; `G_Revision = 30-day consensus estimate revision`.

Fallbacks: gross profit missing → `G_f = 0.5*G_Revenue + 0.5*G_EPS`; EPS missing → `G_f = 0.5*G_Revenue + 0.5*G_GrossProfit`; only revenue guidance available → `G_f = G_Revenue`.

**2. DMA speed.** Quarterly annualized-equivalent moving-average speed per DMA:

```text
G_DMAx = ((SMA_x(t) - SMA_x(t-k)) / SMA_x(t-k)) * (63 / k)
```

Default `k = 5` or `10` trading days. If only price-change data is available, approximate: `DailySlope_x ≈ (P_t - P_t-x) / x`, `G_DMAx ≈ DailySlope_x * 63 / P_t`. Compute for x = 20, 50, 100, 200.

**3. Fundamental-DMA match.** Before computing `R_x`, apply gates: if `G_f` is near zero relative to guidance/estimate uncertainty, changes sign, uses EPS/gross profit crossing zero, or compares incompatible horizons — mark GrowthMatch `N/A` and report components instead of forcing a ratio. Treat GF-DMA as a conditional heuristic, not a return probability or causal model — a similar DMA shape can arise from different liquidity, crowding, leverage, event, and fundamental states. If a plausible change in `k`, weights, or thresholds flips the decision category, report the sensitivity and label the result `model-sensitive`.

```text
R_x = G_DMAx / G_f
```

Interpret `R_50` and `R_100` first:

| R_x | Status |
| ---: | --- |
| < 0.5 | Trend clearly below fundamental speed |
| 0.5-0.8 | Under-reflected or cheap versus trend |
| 0.8-1.3 | Healthy match |
| 1.3-2.0 | Hot but potentially explainable |
| > 2.0 | Overheated / FOMO escape risk |

Core DMA emphasis by stock type: mega-cap growth leaders (NVDA, AVGO, MSFT) → 50DMA; memory/cyclical semis (MU, SNDK) → 100DMA; high-elasticity optical names (LITE, AAOI) → 20DMA+50DMA; industrial AI/power names (ETN, VRT, TEL) → 100DMA+200DMA; small-cap hard-manufacturing names → 20DMA + ATR divergence; semiconductor ETFs (SOXX, SMH) → 50DMA+100DMA.

**4. Price-DMA divergence.**

```text
D_x = P_t / SMA_x(t) - 1
Z_x = (P_t - SMA_x) / ATR20
```

| Signal | Status |
| --- | --- |
| 0%-5% above 20DMA | Healthy close-to-line trend |
| 5%-12% above 20DMA | Strong trend, mild valuation stretch |
| 12%-20% above 20DMA | Hot; divergence score should fall |
| >20% above 20DMA | Short-term escape; divergence score falls sharply |
| >30% above 50DMA | Medium-term overheat |
| >50% above 100DMA | Major repricing |
| >100% above 200DMA | Extreme long-cycle repricing |
| 0%-5% below 20/50DMA with stable fundamentals | Healthy pullback; divergence score can rise |
| 5%-15% below 50DMA with stable/improving fundamentals | Better valuation entry — verify trend damage separately |
| Below 100/200DMA with deteriorating fundamentals | Trend damage; do not treat as cheap automatically |

ATR divergence (asymmetric):

| Z_x | Status |
| ---: | --- |
| 0 to 2 | Healthy |
| 2 to 3 | Hot |
| 3 to 4 | Very hot |
| >4 | Escape; reduce divergence score sharply |
| -1 to 0 with stable fundamentals | Mild pullback; can improve score |
| -3 to -1 with stable/improving fundamentals | Discounted pullback; score can be high, check trend parallelism |
| < -3 or below key long DMA with estimate cuts | Possible breakdown; score should fall |

`S_Divergence` is a valuation-health score, not a pure momentum score: upward price-DMA divergence lowers it (stretched); downward divergence raises it only when fundamental speed and revisions are stable/improving — otherwise it is trend damage, not opportunity.

**5. Trend parallelism / escape ratio.**

```text
EscapeRatio = 5-day price slope / 50DMA daily slope
```

| EscapeRatio | Status |
| ---: | --- |
| 0.8-1.2 | Price and 50DMA parallel; healthy |
| 1.2-1.8 | Short-term acceleration; acceptable |
| 1.8-2.5 | Clearly hot |
| >2.5 | FOMO escape |
| 0-0.5 | Momentum decay |
| <0 | Short-term reversal; trend damage |

**6. Revision confirmation.**

| Revision state | Score |
| --- | ---: |
| Revenue and EPS estimates rising; guide above consensus | 85-100 |
| Mild upward revisions; guide slightly above consensus | 70-85 |
| Stable expectations; limited upward revision | 55-70 |
| Revisions starting to fall | 35-55 |
| Guide below consensus; analysts cutting estimates | <35 |

### Divergence Module Scoring

| State | Score |
| --- | ---: |
| Price close to 20/50DMA, above 100/200DMA | 80-95 |
| Stable/improving fundamentals; price below 20DMA but near 50DMA | 85-100 |
| Stable/improving fundamentals; price 5%-15% below 50DMA while long DMAs remain healthy | 75-95 |
| Price 5%-12% above 20DMA | 65-80 |
| Price 12%-20% above 20DMA | 50-70 |
| Price >20% above 20DMA or >30% above 50DMA | 25-55 |
| Price below 50DMA with weakening fundamentals or estimate cuts | 35-60 |
| Price below 100DMA with estimate cuts | 15-45 |
| Price below 200DMA with fundamental deterioration | 0-30 |

When price is below key DMAs, explicitly state whether the lower price is a healthy pullback or a breakdown — the deciding gate is fundamental speed plus revision confirmation.

### Final Scoring

```text
HealthScore = 0.40*S_GrowthMatch + 0.25*S_Divergence + 0.20*S_Parallel + 0.15*S_Revision
```

| Module | Weight |
| --- | ---: |
| Fundamental speed match | 40% |
| Price-DMA divergence / pullback opportunity | 25% |
| Trend parallelism | 20% |
| Revision confirmation | 15% |

Do not renormalize around a failed GrowthMatch gate or publish a full HealthScore as if all modules were valid — report the remaining modules and mark the total `N/A` unless the user explicitly requests a clearly labeled partial score.

| Score | State | Meaning |
| ---: | --- | --- |
| 85-100 | Healthy Momentum | Healthy main uptrend |
| 75-85 | Strong but Watch | Strong trend; continue monitoring |
| 65-75 | Hot but Supported | Hot, but fundamentals can still support it |
| 55-65 | Damaged / Overheated | Trend damage or local overheat |
| 40-55 | High Risk | Risk clearly rising |
| <40 | Broken / Escaping | Broken trend or post-escape pullback |

### Output Format

When a required gate fails, use the unscorable branch instead of the numeric template:

```text
# TICKER: GF-DMA Health Index 评分

最终评分：N/A / 100
状态：Unscorable
失效原因：
仍有效的模块观察：
模型敏感性：
恢复评分需要的数据：
```

Otherwise:

```text
# TICKER: GF-DMA Health Index 评分

最终评分：XX / 100
状态：Healthy Momentum / Strong but Watch / Hot but Supported / Damaged / High Risk / Broken

一句话判断：
...

1. 基本面速度
- 最新季度营收：
- 下一季度营收指引：
- 营收 QoQ：
- EPS QoQ：
- 毛利润 QoQ：
- Fundamental Speed：

2. 均线速度匹配
| 均线 | 季度化斜率 | 相对基本面速度 | 判断 |
|---|---:|---:|---|
| 20DMA | | | |
| 50DMA | | | |
| 100DMA | | | |
| 200DMA | | | |

3. 股价-均线背离
| 指标 | 当前背离 | 判断 |
|---|---:|---|
| P / 20DMA - 1 | | |
| P / 50DMA - 1 | | |
| P / 100DMA - 1 | | |
| P / 200DMA - 1 | | |

4. 趋势平行度
- Escape Ratio：
- 判断：

5. 预期上修确认
- 公司指引 vs 市场预期：
- 过去 30 天预期变化：
- 判断：

6. 综合评分
| 模块 | 权重 | 分数 |
|---|---:|---:|
| 基本面速度匹配 | 40% | |
| 股价-均线背离 | 25% | |
| 趋势平行度 | 20% | |
| 预期上修确认 | 15% | |

结论：
...
```

## Mode D — Serenity Alpha (News → Alpha)

Use when the user shares news, a product launch, a technology breakthrough, a procurement/supply-chain signal, an earnings-call clue, or asks for Serenity-style alpha analysis, small-cap beneficiaries, or "news to financial statement" translation.

Do not ask only whether the news is impressive. Ask whether an already-observable demand change can rewrite a smaller company's financial statements:

```text
news -> observed demand change -> revenue/profit transmission -> small-cap elasticity -> validation path
```

### Answer Shape

Start and end with the company that best fits the alpha hypothesis. Open with a direct one-sentence call: `最值得优先验证的是：Company / ticker，原因是...`. If several names appear, choose a primary candidate and label others alternatives or supply-chain comparables. If no company is investable yet, say so at the top: `暂时没有足够明确的公司，先观察...`. Close by repeating the primary company and the single validation condition that would confirm or kill the thesis.

### Workflow

**1. Separate talk from demand.** Prioritize evidence that has already happened: users adopting or paying, enterprises buying or expanding deployments, suppliers shipping/backlogged/raising prices, production schedules tightening, earnings calls or filings mentioning the demand, a niche ecosystem getting crowded. If demand is not observable, classify the idea as watchlist-only. Before calling demand real, write `observed signal -> latent demand hypothesis -> rival explanations -> independent corroboration`; cluster signals sharing one cause (orders, price increases, shortages, and supplier backlog may be projections of the same event, not four independent confirmations).

**2. Translate phenomenon into financial lines.**

```text
Because X is happening, demand for Y is increasing.
That demand can flow to A/B/C companies through revenue line Z.
Company N may matter because its market cap, revenue base, or business purity is small enough for the demand shock to change reported results.
```

For each candidate map the mechanism to income-statement/balance-sheet items: revenue (units, ASP, customer count, usage, take rate, backlog conversion), gross margin (mix shift, pricing power, utilization, input costs), operating leverage (fixed-cost absorption, sales efficiency, R&D leverage), cash flow (working capital, capex needs, inventory turns, prepayments). Do not assume demand transmits linearly into revenue or profit — check capacity, competition, substitution, pricing, delivery, qualification, working-capital, and reporting lags; distinguish volume, price, mix, acquisition, currency, and accounting effects that could produce the same reported growth.

**3. Prefer small, pure, misclassified picks.** Rank candidates higher when they have small market cap or low revenue base versus the size of the demand shock, high business purity to the specific demand vector, key supply-chain position or scarcity value, low current investor attention, a stale market label that misses the new role, and financial verification likely within 1-4 quarters.

```text
alpha elasticity ~= incremental demand impact / current company scale
```

**4. Test market misclassification.** What does the market currently think this company is? What could it become if the demand change persists? Is the new label large enough, durable enough, and close enough to reported numbers to matter? Misclassification only creates alpha when the relabeling is validated by numbers, not just story.

**5. Build a verification chain.** Use the most relevant of: revenue growth/guidance revisions, backlog/book-to-bill/lead times/order commentary, inventory drawdown or channel checks, utilization/capacity expansion/capex plans, ASP changes/pricing commentary, customer concentration changes, management mentioning the demand driver unprompted, competitor/supplier/customer corroboration. Define what would confirm, weaken, or falsify the thesis.

**6. Score alpha strength** qualitatively or 1-5 across: demand certainty (already occurring or imagined?), transmission clarity (can demand clearly flow to named companies?), business purity (directly exposed?), market-cap elasticity (small enough for impact to matter?), market neglect (missing or mislabeling it?), verification speed (1-4 quarters?), downside risk (what if wrong?). Prioritize high certainty, clear transmission, high purity, high elasticity, and near-term verification.

**7. Size by evidence** as conditional research guidance, not a personalized recommendation:

| Thesis state | Posture |
| --- | --- |
| Demand seems real, transmission unclear | observe / very small exploratory size |
| Demand real, transmission clear, no financial proof yet | small test position if risk fits |
| Financials begin validating and market still underprices | consider adding |
| Thesis becomes consensus and valuation stretches | lower return expectations / trade only |
| Key assumptions are falsified | exit or remove from watchlist |

### Output Template

```markdown
## 结论先行：优先验证的公司
点名最值得优先验证的一家公司 / ticker，并用一句话说明为什么它是本次新闻里最有弹性的候选。

## A. 表层新闻
简述新闻表面信息。

## B. 已发生的需求变化
说明已经可观察的需求、采购、使用、价格、排产或供应链变化；如果没有，明确说只是谈资。

## C. 财务翻译
把需求映射到收入项、成本项、利润项、现金流或资产负债表项目。

## D. 受益链条
列出一阶、二阶、三阶受益者，并说明传导距离。

## E. 小市值高弹性标的
列出可能的小盘/高纯度/低关注候选；标注需要核实的市值、收入基数和业务占比。

## F. 市场误分类
说明市场现在把公司当什么，它可能正在变成什么。

## G. 验证指标
列出未来 1-4 个季度要看的财报、电话会、供应链和价格指标。

## H. 下行风险
列出需求、传导、竞争、估值、时点和流动性风险。

## I. 仓位建议
给出观察、小仓、加仓、放弃的条件；避免承诺收益或给出个性化投资指令。

## 最后一句
再次点名这家公司，并给出最关键的财报验证条件；如果条件不成立，明确说应放弃或降级为观察。
```

### Quality Bar

Anchor the analysis in observable demand, not vibes. Prefer named revenue mechanisms over broad themes. Distinguish first-order beneficiaries from distant second- or third-order stories. Use current sourced data for market caps, financials, prices, and recent filings. State uncertainty and falsification conditions clearly.

## Mode E — TAM-Adj-PEG

Use when the user explicitly asks for TAM-Adj-PEG, TAM-supported valuation, runway-adjusted PEG, quality-adjusted growth valuation, or position-type framing based on those factors. Do not trigger from a bare ticker or generic stock-analysis request.

Traditional PEG asks whether the current valuation is expensive relative to future EPS growth. TAM-Adj-PEG asks the broader question: how long can this growth last, is the TAM large enough, and can the company convert TAM growth into durable profits? Use it for AI infrastructure, semiconductors, healthcare, SaaS, payment networks, high-growth manufacturers, bottleneck suppliers, early turnarounds, and option-like equities.

### Required Inputs

Valuation: current/TTM PE, forward PE, traditional PEG if available. Growth: expected 2-3 year EPS CAGR, revenue CAGR, TAM CAGR, current revenue/TAM penetration. Profit quality: gross margin, EBIT margin, FCF profile, capex intensity, dilution risk. Business quality: competitive position, pricing power, customer concentration, technology iteration risk, cyclicality, key milestones. If PE or EPS CAGR is not meaningful (loss-making or highly volatile earnings), mark PE/PEG as distorted and use normalized earnings, EV/Sales, milestone scenarios, or an option-style framework instead.

### Core Formula

```text
TAM-Adj-PEG = Forward PE / (EPS CAGR x TAM Runway Factor x Quality Factor)
Adjusted Growth = EPS CAGR x TAM Runway Factor x Quality Factor
```

Use EPS CAGR as a percentage number in the denominator (forward PE 40, adjusted growth 50% → TAM-Adj-PEG = 40/50 = 0.8). Do not directly add TAM CAGR to EPS CAGR — EPS CAGR usually already reflects part of TAM expansion; TAM should mainly adjust growth duration and certainty. Treat EPS CAGR, TAM Runway Factor, and Quality Factor as interacting assumptions, not independent measurements — state what incremental information each adds beyond the others, and do not double-count TAM/moat/cyclicality/margin durability that is already embedded in the EPS forecast. Report Low/Base/High factor combinations and the resulting range; if a small plausible change in either factor moves the result across more than one valuation band, label the conclusion `model-sensitive` and avoid a strong point estimate.

### TAM Runway Factor

```text
TAM Runway Factor = sqrt(Growth Duration / 5)
```

| High-growth duration | Factor | Interpretation |
| ---: | ---: | --- |
| 2 years | 0.6 | Short-cycle growth |
| 3 years | 0.75 | Growth exists, but runway is short |
| 5 years | 1.0 | Standard growth stock |
| 8 years | 1.25 | Long-runway compounder |
| 10 years | 1.4 | High-quality long runway |
| 15 years | 1.7 | Super long-cycle opportunity |
| 20+ years | 2.0 cap | Rare supercycle, platform, or monopoly-like asset |

Do not assign runway by sector label alone. AI-driven semiconductor bottlenecks can deserve a 15-20+ year runway when demand is structurally expanding, the company controls a hard-to-replicate choke point, and each technology generation reinforces its position. Conversely, SaaS/platform companies should not automatically get a long runway if frontier AI models can compress workflow value, commoditize features, weaken seat-based pricing, or shift the profit pool to model/infrastructure providers.

### Quality Factor

| Quality Factor | Company Type |
| ---: | --- |
| 0.3-0.5 | Early-stage, loss-making, unproven orders, or high dilution risk |
| 0.5-0.7 | Cyclical, customer-concentrated, or high execution risk |
| 0.7-0.9 | High growth but competitive, with unstable margins |
| 0.9-1.1 | Normal high-quality growth company |
| 1.1-1.3 | Strong moat, pricing power, and customer stickiness |
| 1.3-1.5 | Monopoly-like, platform, or ecosystem asset |
| 1.5+ | Rare super-platform or AI-era bottleneck asset; use cautiously |

Evaluate: (1) can TAM growth actually accrue to this company; (2) pricing power; (3) customer concentration; (4) does frequent technology iteration require repeated requalification; (5) are gross/EBIT margin sustainable; (6) does growth require heavy capex; (7) can competitors quickly become second/third sources; (8) does growth depend on financing or share issuance; (9) can frontier AI models erode the product's workflow value, pricing model, or distribution moat.

### Result Interpretation

| TAM-Adj-PEG | Valuation View |
| ---: | --- |
| < 0.5 | Very cheap, but verify forecasts are not overly optimistic |
| 0.5-0.8 | Clearly attractive |
| 0.8-1.2 | Reasonable to slightly cheap |
| 1.2-1.8 | Reasonable to slightly expensive; execution must continue |
| 1.8-2.5 | Expensive unless the company has a super-long runway |
| > 2.5 | Very expensive, or EPS/PE inputs are distorted |
| Not applicable | Loss-making, early-stage, or earnings too volatile; use option framework |

### Special Cases

**Loss-making companies:** do not use PE directly; mark PE/PEG distorted; use normalized EPS, EV/Sales, milestone scenarios, or option-style analysis; focus on milestones and financing/dilution risk.

**Cyclical companies:** do not use peak-cycle EPS mechanically; use normalized EPS; discount Quality Factor for cyclicality; TAM runway can add support but supply/demand cycle risk must be deducted. For AI semiconductor supercycles, separate structural demand runway from inventory/capacity/margin-cycle risk — a durable bottleneck leader can keep a long TAM Runway Factor, with the cyclical penalty flowing mainly through normalized EPS and Quality Factor rather than an automatic short-runway cap.

**Turnarounds:** show both a base case (score current earnings power) and a turnaround-success case (score normalized profit 2-3 years out) to avoid misclassifying a turnaround as a normal growth stock.

### Position-Type Framework

| Type | TAM-PEG Traits | Position Framing |
| --- | --- | --- |
| Core compounder | TAM-PEG 0.5-1.2 with high Quality Factor | Candidate for long-term core exposure |
| High-beta growth | TAM-PEG 0.8-1.5 with high growth and volatility | Medium exposure, track results closely |
| Turnaround | Current TAM-PEG high, success-case TAM-PEG lower | Small to medium exposure, milestone-driven |
| Option-like | PE/PEG distorted, large TAM, early execution | Small exposure, accept binary outcomes |
| Cyclical | Low PEG but discounted Quality Factor | Trade supply/demand cycle, avoid linear extrapolation |

### Output Format

```text
# TICKER: TAM-Adj-PEG 估值分析

公司：XXX
股票代码：XXX

1. 当前估值
- 当前 PE：
- Forward PE：
- 传统 PEG：

2. 增长拆解
- 未来 EPS CAGR：
- Revenue CAGR：
- TAM CAGR：
- 当前收入 / TAM：
- 高速增长 runway：

3. TAM Runway Factor
- 估计值：
- 原因：

4. Quality Factor
- 估计值：
- 加分项：
- 扣分项：

5. TAM-Adj-PEG
公式：
TAM-Adj-PEG = Forward PE / (EPS CAGR x TAM Runway Factor x Quality Factor)

计算：
- 修正后增长率：
- TAM-Adj-PEG：
- Low / Base / High 敏感性：

6. 结论
- 估值档位：
- 主要上行驱动：
- 主要下行风险：
- 适合的仓位类型：
```

## Notion Delivery

**Mode A (full memo):** archive to the Notion page or database named `Invest` unless the user names another destination or explicitly opts out. Title it `[YYYY-MM-DD] [TICKER] — Buy-Side Memo`; preserve the as-of date, decision, crux, scenarios, citations, and falsifiers.

**Modes B, C, D, E:** archive only when the user explicitly asks. Resolve the exact Notion page or database the user names — do not assume `Invest`. Title as `[YYYY-MM-DD] [TICKER] — Bayesian Growth Valuation`, `— GF-DMA Health`, `— Alpha Note`, or `— TAM-Adj-PEG` respectively; preserve the as-of date, key tables/decision, citations, and falsifiers.

For every mode: write only when authenticated Notion access is available and exactly one target is resolved — do not guess among multiple matches. Do not claim success without a returned Notion page URL or page ID; include that link in the final response. If archiving is requested/defaulted but Notion is unavailable, unauthenticated, or ambiguous, do not block delivery — return the complete Markdown and state `Notion archive pending`.
