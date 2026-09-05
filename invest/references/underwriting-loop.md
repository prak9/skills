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

## 3. Triangulate Valuation

Use multiple methods to reveal assumption risk, not to manufacture agreement.

1. **DCF:** show revenue, margin, reinvestment/ROIC, discount rate, terminal assumptions, dilution, and sensitivity ranges.
2. **Normalized EPS:** estimate mid-cycle or steady-state earnings after removing unsustainable peak/trough conditions and inconsistent adjustments; use a justified multiple and fully diluted shares.
3. **Reverse DCF:** solve for combinations of growth duration, revenue CAGR, steady-state margin, reinvestment/ROIC, discount rate, and terminal value that reconcile the current enterprise value.

Add SOTP, NAV, EV/revenue, EV/EBITDA, P/FCF, or milestone valuation only when the business requires it. Do not average incompatible methods mechanically. Explain why values diverge and which assumption causes the divergence.

The reverse DCF is a market-expectations test, not a unique forecast. Report a joint sensitivity because the same price can imply several combinations of growth, margin, reinvestment, and duration.

## 4. Run A Cross-Forecast Consistency Audit

Before accepting Bull/Base/Bear outputs, check whether all forecasts can be true at the same time.

| Link to test | Typical contradiction |
| --- | --- |
| Demand -> revenue | Growth exceeds capacity, backlog conversion, customer budgets, or market size |
| Revenue -> gross margin | Price/mix assumptions conflict with competition, utilization, or input costs |
| Growth -> opex | Rapid expansion assumes no sales, support, R&D, or compliance burden |
| Earnings -> FCF | EPS rises while capex, working capital, cash taxes, or SBC are ignored |
| Capacity -> capex/depreciation | Output expands without funding, construction lag, or depreciation |
| TAM/share -> competition | Several firms simultaneously gain more share than the market permits |
| Guidance/consensus -> model | The analyst forecast differs without a named, testable reason |
| Terminal value -> normalized economics | Terminal margins, ROIC, or growth exceed durable competitive conditions |

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

## 6. Preserve A Decision Journal

Version the thesis instead of rewriting history after results are known. Preserve:

- as-of date and available information set;
- forecast horizon and ranges;
- core assumptions and scenario probabilities;
- current price, market-implied assumptions, and decision posture;
- dominant falsifier and expected validation date;
- actual outcome and error attribution when the horizon closes.

Separate data surprise, model error, timing error, valuation/multiple error, and decision/exposure error. A profitable result does not prove the thesis was sound, and a loss does not prove the process was wrong.

## 7. Monitor By Thesis Change, Not News Volume

Create a versioned baseline before monitoring:

| Field | Required content |
| --- | --- |
| Core assumptions | 3-7 causal variables that drive long-term cash flow |
| Expected range | Base range and scenario bounds for each variable |
| Market-implied hurdle | Growth, margin, duration, or return assumptions embedded in price |
| Dominant falsifier | Threshold and deadline from the red-team step |
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
