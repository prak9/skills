# Longitudinal Underwriting And Thesis-Change Monitoring

Use this reference for a deep Mode A memo or re-underwriting request that calls for a long historical record, an integrated earnings model, DCF/normalized EPS/reverse DCF reconciliation, forecast-consistency checks, prior-decision review, or ongoing thesis monitoring.

The objective is not to maximize context or produce the longest report. Build the smallest auditable evidence-and-model system that explains the investment, exposes contradictions, and identifies the observation that would change the decision.

## 1. Build A Point-In-Time Evidence Spine

Use a decision-relevant history rather than an undifferentiated document dump. When available and useful, cover 5-10 fiscal years and 12-20 quarters; shorten the window when the business, reporting perimeter, or industry regime changed enough to make older periods incomparable.

Include the relevant parts of:

- annual and quarterly filings, earnings releases, and segment disclosures;
- earnings-call transcripts, prepared remarks, Q&A, and management guidance;
- competitor, customer, and supplier disclosures;
- industry supply, demand, capacity, inventory, pricing, and policy data;
- point-in-time sell-side consensus and estimate revisions;
- the investor's prior theses, forecasts, decisions, and stated falsifiers.

For every important item, preserve the document date, the information-availability date, source type, and whether it is reported fact, management guidance, consensus, third-party estimate, or analyst inference. Material numeric inputs also follow [data-contract.md](data-contract.md); validate linked calculations and historical timestamps with its script. Do not let later restatements, revised consensus, or known outcomes leak into an earlier decision reconstruction.

If a point-in-time consensus snapshot or prior judgment cannot be recovered, mark it missing; never backfill it with a current estimate or a hindsight reconstruction. Use an evidence ledger with citations and retrieve the supporting passages as needed instead of forcing every source document into one context window.

Normalize before comparing periods: fiscal calendars, currencies, acquisitions and disposals, discontinued operations, segment changes, accounting-policy changes, stock splits, GAAP/non-GAAP definitions, and one-time items. State when periods remain incomparable.

### Investigate The Mechanism, Not Just The Metric

Start with competing explanations for the opportunity. Reconstruct the relevant history: what changed in customer behavior, pricing, competition, capital use or reporting; what management previously promised; what actually happened; and why the stock could rationally deserve its current valuation. Select a window that exposes both favorable and adverse episodes, not just the period supporting the thesis. A long time series without an explanation of the turning points is not deep research.

Follow the uncertain links that can move value. Use the following as investigative lenses, not mandatory sector checklists:

| Claim | Mechanism to uncover | Evidence that can distinguish rivals |
|---|---|---|
| Demand or share is accelerating | Replacement vs new demand; customer budgets, inventory, channel loading, mix and price elasticity | Customer purchases/usage, sell-through, cancellations, competitors' response; not bookings or TAM alone |
| Retention or network effects improve economics | Same-cohort survival, monetization, acquisition/subsidy and incremental service cost | Comparable cohort contribution over a mature window; aggregate engagement may hide mix or weaker new cohorts |
| Margin expansion is durable | Price/cost pass-through, utilization, product mix, labor and supplier bargaining, true incremental margins | Unit economics, price lists, capacity and cost evidence; not extrapolation from a peak quarter |
| Growth creates shareholder value | Who captures incremental surplus: customer, creator, distributor, supplier, employee or shareholder | Net cash after required reinvestment and dilution; higher gross volume can reduce retained profit |
| Moat or management protects returns | Concrete switching friction, renewal behavior, capital allocation, incentive and competitor constraints | Actual retained customers, realized project returns and failed promises; labels and founder ownership are not mechanisms |

For the selected crux, preserve enough operating detail to explain outcomes and counterexamples. Define the denominator, population, duration, unit and accounting recognition. Name ratios by what they measure: cash retained is not customer retention, and a threshold for preserving prior profit is not zero-profit break-even. A leading KPI, reported revenue, cash collection and shareholder cash are different objects; trace the lag and bridge rather than interchange them. Decompose before/after or cohort/segment differences, then recombine material interactions. Few variables do not justify discarding a countervailing cost or jointly necessary condition.

### Make Evidence Carry A Specific Claim

Embed a compact argument record in the existing memo/model; do not create a second ledger by default:

```text
Crux and economic mechanism:
Claim / independently forecast range:
Original observation, source date and precise locator:
What the observation establishes, inference added, and what remains unknown:
Source origin / population / selection and reporting limits:
Strongest contrary evidence and rival explanation:
Discriminating observation available now or at a named later point:
Effect on model line, per-share value and verdict:
```

Compare explanations rather than merely collecting confirmation. Company commentary can establish management's intent, not the causal effect of its initiative; a customer case can establish that customer's behavior, not market-wide adoption. A supplier quote may constrain cost but not establish final demand. Reprints, analyst notes citing management and several metrics from the same campaign do not create independent evidence. External origin helps only when measurement, population and incentives fit the claim.

Trace surprising claims to the underlying filing footnote, contract terms, data or call exchange; inspect counterevidence and missing denominators. Check feasible customer, competitor, supplier or regulator evidence where it can discriminate; document inability to obtain it instead of pretending the company narrative was independently confirmed. Never invent an expert interview or assume access to private data. Public-information research does not authorize contacting counterparties or acquiring material nonpublic information.

Allocate effort by potential value impact, uncertainty and whether evidence can resolve it; no numeric composite score is required. Read the accessible primary material that could change the decision before deferring it. Stop a branch when rivals no longer change the action within defensible bounds, or the decisive evidence is unavailable and its consequence is explicitly bounded. A source list is not a substitute for this work.

## 2. Rebuild The Economic Model

Link the operating assumptions to earnings and cash rather than forecasting each line independently. Use only the detail supported by the business and available evidence.

```text
operating drivers
-> revenue
-> gross profit and operating expenses
-> normalized operating earnings
-> taxes, reinvestment, and share count
-> free cash flow and per-share value
```

At minimum, make these bridges explicit when material:

- **Revenue:** units/users/customers x price/ASP/ARPU/take rate, plus mix, churn, acquisition, backlog conversion, and currency where relevant.
- **Gross margin:** price, mix, utilization, input cost, yield, freight, cloud/compute, warranty, and inventory effects.
- **Operating earnings:** R&D and SG&A requirements, operating leverage, restructuring, and recurring versus one-time adjustments.
- **Reinvestment:** capex, depreciation, capitalized costs, working capital, capacity timing, and maintenance versus growth investment.
- **Free cash flow:** normalized after-tax operating profit plus non-cash charges minus capex and working-capital needs; reconcile to reported cash flow.
- **Per-share economics:** debt and cash, SBC, options, convertibles, issuance, buybacks, and fully diluted share count.

Keep reported history, management guidance, consensus, and the analyst model in separate columns or clearly labeled layers. Preserve formulas and assumptions needed for another analyst to reproduce the result.

### Justify The Forecast Before Trusting The Valuation

For load-bearing growth, mature margin, reinvestment, SBC/dilution, discount rate and terminal assumptions, give the evidence anchor, derivation or relevant reference class, plausible range, economic prerequisites and confidence limit. A named `analyst_assumption` or a link to one's own model provides reproducibility, not empirical support. An unobserved parameter is unknown; a scenario value for it is a conditional assumption, not a replacement fact.

Use a useful decomposition rather than independently guessing every financial line. Reconcile the starting run rate, guidance changes, deferred items and operating cohorts; connect near-term milestones to later scale, margins and reinvestment. Explain why a mature peer's economics would transfer before borrowing them. Unsupported long-run parameters may appear in a labeled hurdle/sensitivity calculation, but cannot alone support a central fair value, precise target or high-conviction verdict.

Show the estimated part and the unidentifiable part separately. If cash-flow timing, cohorts or capital needs are missing, use honest bounds, break-even requirements or a suitable alternative method, and disclose which requested model cannot be completed. Do not silently substitute a toy earnings bridge for a fully reconstructed model. A partial model can still decisively reject an implausible price requirement without establishing a precise intrinsic value.

### Capital Allocation And Franchise Fade

For material uses of capital, connect cash committed, timing, incremental cash generated, and the alternative use. Separate maintenance from growth investment, organic expansion from acquisitions, and operating cash generation from financing. Trace dividends, debt reduction, retained cash, and buybacks through the same cash balance; neither financing proceeds nor returned capital create a second source of operating value.

- **Incremental economics:** distinguish legacy average ROIC from prospective incremental returns. ROIC is not a profit margin: on a consistent non-financial operating basis it combines after-tax operating margin and invested-capital turnover. Under stable definitions and investment-driven growth, `NOPAT growth ≈ net reinvestment / NOPAT × incremental ROIC`; separately model efficiency gains on existing assets. Use aligned periods, after-tax amounts, and the applicable capital cost. Financial firms need an equity/regulatory-capital framework rather than a forced industrial ROIC formula.
- **Measurement limits:** explain material intangible capitalization, goodwill, cycle, or investment-lag adjustments. A tiny/negative denominator or incomparable periods makes a mechanical incremental-ROIC ratio unreliable; mark it undefined and use a multi-period investment cohort or project NPV. An acquisition's value depends on the price paid and future incremental cash flows, not EPS accretion alone.
- **Management evidence:** compare promised allocation with realized investment outcomes, dilution, incentives, and responses to failed projects. Founder ownership, culture labels, or an expert's conviction do not substitute for sourced behavior and rival explanations.
- **Buybacks:** reconcile cash spent, repurchase price versus conditional intrinsic value, issuance/SBC, and net diluted shares. A repurchase that offsets employee issuance does not give continuing holders an extra gross-buyback-yield return. Avoid both ignoring and charging the same SBC dilution twice.
- **Three durations:** distinguish the remaining advantage of existing assets, the runway for attractive incremental reinvestment, and the investor's informational edge. Model competitive responses and fade in the ROIC spread/margin where supported; do not convert “strong moat” into indefinite high growth or a second quality premium.

### Investor Return Bridge

Compute returns from the price actually paid, not business growth alone. For comparable positive EPS and matching multiple definitions:

```text
1 + price return = (EPS_H / EPS_0) * (PE_H / PE_0)
holding-period total return = (P_H + sum(cash dividends received) - P_0) / P_0
```

The second identity assumes a continuously held, split-adjusted share, no reinvestment of dividends, no additional contributions, and no taxes/fees; include actual frictions when relevant. EPS already incorporates the modeled net share count, so do not add gross buyback yield again. Use dated investor cash flows for IRR when well-defined; otherwise report NPV or horizon wealth. Keep cumulative and annualized returns distinct, and do not call a probability-weighted scenario IRR the return of the expected cash-flow path. Maintenance, organic growth, and active investment are causal components of value, not automatically disjoint additive shareholder returns.

## 3. Triangulate Valuation

Use multiple methods to reveal assumption risk, not to manufacture agreement.

1. **DCF:** show revenue, margin, reinvestment/ROIC, discount rate, terminal assumptions, dilution, and sensitivity ranges.
2. **Normalized EPS:** estimate mid-cycle or steady-state earnings after removing unsustainable peak/trough conditions and inconsistent adjustments; use a justified multiple and fully diluted shares.
3. **Reverse DCF:** solve for combinations of growth duration, revenue CAGR, steady-state margin, reinvestment/ROIC, discount rate, and terminal value that reconcile the current enterprise value.

Add SOTP, NAV, EV/revenue, EV/EBITDA, P/FCF, or milestone valuation only when the business requires it. Do not average incompatible methods mechanically. Explain why values diverge and which assumption causes the divergence.

The reverse DCF is a market-expectations test, not a unique forecast or an observed consensus series. Report a joint sensitivity with fixed assumptions because the same price can imply several combinations of growth, margin, reinvestment, and duration. Compare these requirements with independently sourced operating scenarios; forward/reverse agreement under shared assumptions is not independent evidence. Calculate each coherent scenario's value and net payoff before probability-weighting, not a valuation of average growth inputs.

### Establish The Variant And Attribute The Price Gap

Maintain three separate columns for each decisive dispute: dated observed expectations, conditional price-implied requirements, and an independently supported forecast. When consensus is unavailable or inconsistent, try an appropriate same-period primary/alternative estimate source if accessible; otherwise mark it missing. Do not replace it with a narrative about what “the market” supposedly believes. A target-price average is neither an operating forecast nor evidence of neglect.

A variant can concern a fact, interpretation, duration, cash conversion, capital allocation or risk—not only a higher revenue forecast. State precisely what is different, what the comparison view already includes, and why the available evidence favors one interpretation. Explain a plausible mispricing mechanism, such as segment aggregation, accounting lag, cycle misclassification or horizon mismatch, only with supporting observations; low coverage or a popular story alone is not proof. Public facts can support an analytical edge, but their availability makes “nobody knows this” an especially demanding claim.

Build a bridge on a consistent valuation date and basis:

```text
observed quote / conditional baseline value
-> supported change in operating assumption or duration
-> incremental net cash flows after offsets, reinvestment and dilution
-> discounted per-share value difference
-> residual gap, estimation uncertainty and realization path
```

Hold common valuation assumptions fixed to expose what the operating variant contributes; then separately stress discount rates, terminal choices and correlated operating changes. One-at-a-time effects are diagnostics and need not add when interactions exist; report the coherent joint result and any residual. Do not imply a smooth spreadsheet from current to optimistic margins is evidence of the transition. Do not project a contract, temporary tax benefit, capacity shortage or subsidy beyond its supported duration.

Ask whether the apparent advantage survives the strongest reasonable rival case and parameter error, not merely whether the bull case exceeds today's price. Report terminal-value dependence and the value requiring unproven businesses or far-future economics. If a small unsupported assumption change reverses the verdict, label it assumption-dependent rather than a demonstrated pricing error. Subjective scenario weights cannot repair weak operating evidence; show unweighted outcomes or probability sensitivity rather than forced 25/50/25 weights.

Finish with a supported positive/negative conditional gap, no demonstrated edge, or an unresolved essential link. The best rebuttal may be that the market is rationally pricing risk, that the good news is already in forecasts, or that the value cannot reach common shareholders. A realization path can be cash distribution or gradual compounding, not necessarily an imminent rerating. Do not demand proof of every investor's beliefs to report a well-bounded conditional opportunity.

## 4. Run A Cross-Forecast Consistency Audit

Before accepting Bull/Base/Bear outputs, check whether all forecasts can be true at the same time.

| Link to test | Typical contradiction |
| --- | --- |
| Demand -> revenue | Growth exceeds capacity, backlog conversion, customer budgets, or market size |
| Revenue -> gross margin | Price/mix assumptions conflict with competition, utilization, or input costs |
| Growth -> opex | Rapid expansion assumes no sales, support, R&D, or compliance burden |
| Earnings -> FCF | EPS rises while capex, working capital, cash taxes, or SBC are ignored |
| Growth -> capital allocation | Legacy high ROIC is used to justify low-return expansion or unfunded growth |
| Cash/earnings -> shareholder return | Buybacks are counted both in net shares/EPS and as an extra payout; multiple contraction is omitted |
| Capacity -> capex/depreciation | Output expands without funding, construction lag, or depreciation |
| TAM/share -> competition | Several firms simultaneously gain more share than the market permits |
| Guidance/consensus -> model | The analyst forecast differs without a named, testable reason |
| Terminal value -> normalized economics | Terminal margins, ROIC, or growth exceed durable competitive conditions |
| Scenarios -> expected value | Marginal growth/margin averages replace coherent joint scenario cash flows |

For every material conflict, show the conflicting assumptions, the financial line affected, and the resolution. If evidence cannot resolve it, lower confidence, widen the scenario range, or label the model `internally inconsistent`; do not hide the contradiction in an average target price.

## 5. Find The Dominant Thesis-Killer

After writing the strongest case for the investment, take the opposing side. Search for the single variable that can invalidate the causal chain rather than listing many generic risks.

```text
candidate variable
-> operating transmission
-> revenue/margin/FCF impact
-> valuation impact
-> observable threshold and deadline
```

State:

- why this variable dominates the other risks;
- the current evidence and strongest rival explanation;
- the threshold, observation, or date that constitutes a breach;
- whether a breach means reduce confidence, rebuild the model, or reject the thesis.

Do not force a false single-variable story when the thesis depends on several jointly necessary conditions. In that case, name the smallest weakest-link set and explain the interaction.

### Make The Falsifier Observable And Decision-Relevant

Design the test from the mechanism before choosing a convenient KPI:

| Field | Requirement |
|---|---|
| Competing predictions | What should be observed if our mechanism is right versus the strongest rival? Include evidence that would overturn a bearish/no-edge view as well as a bullish one. |
| Measurement | Exact metric, denominator, population/cohort, accounting basis, source and sampling limitations. Do not promote a proxy such as DAU into net lifetime contribution. |
| Breakpoint | Economic break-even or valuation/action threshold derived from the model, contract or historical variability. If unsupported, use a qualitative boundary or range, not an invented percentage. |
| Window | When the effect matures, when data is published and when review is due; distinguish all three. |
| Decision consequence | Confidence update, new valuation, reject the causal thesis or re-underwrite. A share-price move alone does not falsify an operating mechanism. |

Keep these updates sequential: new operating evidence may resolve a forecast gap; only the completed per-share valuation compared with the then-current price can establish a pricing advantage. Neither improved business evidence nor a falsified bearish mechanism alone overturns a `no demonstrated edge` verdict.

If the decisive metric is not disclosed, test what can be bounded with accessible components, proxy evidence or a natural comparison. State what that test cannot distinguish. “Wait for a metric nobody publishes” is not an executable verification plan. Missing disclosure or a not-yet-mature cohort is an evidence limitation, not proof of business failure; prolonged unverifiability can still reduce warranted conviction or research priority.

Separate a statistical fluctuation, timing miss, loss of visibility and structural breach. Predeclare economically justified tolerance and lag where possible; do not move the goalposts after contrary results. A source access failure should produce the best available conditional conclusion and named missing evidence, not a fabricated test pass or abandonment of feasible work.

## 6. Preserve A Decision Journal

Version the thesis instead of rewriting history after results are known. Preserve:

- as-of date and available information set;
- forecast horizon and ranges;
- core assumptions and scenario probabilities;
- current price, market-implied assumptions, and decision posture;
- dominant falsifier and expected validation date;
- evidence state of each load-bearing claim, unresolved rival and reason an opportunity was rejected or deferred;
- actual outcome and error attribution when the horizon closes.

Separate data surprise, model error, timing error, valuation/multiple error, and decision/exposure error. A profitable result does not prove the thesis was sound, and a loss does not prove the process was wrong.

## 7. Monitor By Thesis Change, Not News Volume

Create a versioned baseline before monitoring:

| Field | Required content |
| --- | --- |
| Core assumptions | Usually 1-2 decisive causal variables; retain additional jointly necessary conditions when material |
| Expected range | Base range and scenario bounds for each variable |
| Market-implied hurdle | Growth, margin, duration, or return assumptions embedded in price |
| Dominant falsifier | Threshold and deadline from the red-team step |
| Observation route | Source, actual metric, cohort/basis, economic maturity and disclosure lag; proxy limits if direct evidence is unavailable |
| Decision state | Watch / own / add-after-proof / reduce / exit, stated conditionally |
| Next scheduled review | Earnings, filing, catalyst, or explicit calendar date |

Monitor the company, competitors, customers, suppliers, industry supply/demand, relevant macro variables, consensus revisions, and market pricing. Classify each observation as:

- `no thesis change`: already expected, immaterial, or duplicate evidence;
- `confidence update`: changes scenario probabilities but not the causal model;
- `valuation-only change`: price or discount-rate change alters expected return without changing cash flows;
- `core-assumption breach`: a causal driver crosses its threshold;
- `new regime / re-underwrite`: the old model no longer explains the business.

Default to no alert for `no thesis change`. Record a routine no-change item only when a separately authorized persistent log is active and that authorization explicitly includes routine logging; monitoring by itself grants no write permission. Define materiality before monitoring in economic terms tied to the model: a core driver crossing its range, a meaningful change in scenario probability or long-term cash flow, a market-implied hurdle or expected return crossing a decision gate, the dominant falsifier being approached or breached, or the decision state changing. Do not use a universal percentage, a headline, or a stock-price move alone as proof of thesis change.

Every material-change report should answer:

1. What changed, and what is the primary source?
2. Which model line or core assumption changed?
3. Is the evidence independent, overlapping, or contradictory?
4. How did scenarios, valuation, and thesis confidence change?
5. What decision state follows, and what is the next validation point?

Do not claim to monitor continuously, create an external alert, or mutate a watchlist unless the user authorized that action and the required persistent tooling is available. Otherwise deliver the baseline, thresholds, sources, and proposed cadence as a monitoring specification.

## Method Sources

- [Expectations Investing](https://www.expectationsinvesting.com/about): conditional price requirements, value-sensitive research, and net opportunity costs.
- [Damodaran on growth](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/growth.htm): reinvestment-driven growth versus efficiency gains.
- [Return on invested capital](https://www.morganstanley.com/im/publication/insights/articles/article_returnoninvestedcapital.pdf) and [total shareholder returns](https://www.morganstanley.com/im/publication/insights/articles/article_totalshareholderreturns.pdf): capital-return definitions and per-share return attribution.
