# Uncertainty, Marginal Information, And Exposure

Use this reference when the request concerns opportunity/risk, entry price, position sizing, portfolio fit, evidence overlap, or whether new information changes an investment thesis.

## 1. Frame The Decision Correctly

Do not claim to abandon prediction. Replace a point forecast with a conditional distribution over outcomes, then choose an exposure that remains survivable when the estimate is wrong.

Keep three judgments separate:

- **Thesis quality:** Is the causal mechanism supported and falsifiable?
- **Price attractiveness:** Does the market price offer positive net expected value under conservative scenarios?
- **Exposure posture:** What commitment is justified after estimation error, tail loss, correlation, liquidity, and opportunity cost?

A strong company can be a poor price; a good price can still deserve a small position; a weakly evidenced thesis does not become stronger because the proposed position is small.

## 2. Calibrate Probabilities And Evidence

Start from a relevant base rate or conservative prior. Update it with observed evidence, not confidence language. Report ranges when the prior, likelihood, or data quality is uncertain; avoid decimal-level precision without repeated calibration data.

Before treating several observations as confirmation, write:

```text
observed signals -> shared latent cause -> rival explanations -> incremental evidence after overlap
```

Cluster earnings, management commentary, supplier orders, and analyst revisions when they originate from the same underlying event. Classify each new item as:

- **Incremental:** changes a key probability after conditioning on what is already known;
- **Corroborative but overlapping:** increases confidence only slightly;
- **Redundant:** restates information already embedded in the thesis or price;
- **Contradictory:** lowers a thesis probability or requires a new model.

For repeated forecasts, preserve the forecast, horizon, information set, and outcome so calibration can later be checked. For one-off investments, use probability bands and sensitivity analysis instead of claiming an objective posterior.

## 3. Compute Net Expected Value Without Hiding The Tail

Use scenario returns after dilution, financing, taxes when relevant, transaction costs, and a plausible exit multiple or terminal value:

```text
Net EV = sum(scenario probability * scenario net return)
```

Report the probability-weighted result together with downside severity, drawdown path, time horizon, and the assumptions that dominate the value. Do not let a positive average override a low-probability loss that violates the user's stated survival constraint or an explicit risk budget.

Treat the current market price as information, not as truth or a uniquely identified probability distribution. State which independently supported operating/payoff estimate differs from the conditional requirements of price. If a prior already incorporates a news event through price, do not count the same event again as an independent update.

### Entry, Exit, And Opportunity Cost

Compare a proposed switch with keeping the current holding and the best relevant feasible alternative, including cash when appropriate, on the same horizon and net-wealth basis. Deduct immediate sale taxes, fees, and financing costs before applying returns to the capital that can actually be redeployed. Include relevant liquidity, correlated tail risk, and estimation error; a slightly higher gross target return does not establish a robust switching advantage. Missing portfolio or tax inputs limits the switch recommendation, not the standalone stock research.

Entry/exit gates should reflect conservative scenario returns, survival constraints, and value relative to alternatives, not universal PE levels or fixed price discounts. Respect an explicitly chosen personal strategy as such while showing its economic assumptions. Distinguish a discount to today's intrinsic value from a discount to an uncertain future value; translate the latter into horizon return and cash distributions rather than calling it guaranteed margin of safety.

A price fall alone proves neither cheapness nor thesis failure: separate the new price from changes in cash flows, financing, and the falsifier. Likewise, unchanged fundamentals can merit a `valuation-only change` report when a price move crosses an agreed return gate. Waiting for a price/evidence trigger is a conditional posture with a review point, not proof the opportunity will eventually pay off. It does not authorize trading, alerts, or external records.

## 4. Bound Exposure Robustly

Do not derive a position percentage without the user's portfolio size, existing exposures, maximum tolerable loss, liquidity horizon, tax/financing constraints, and a sufficiently supported payoff distribution. When those inputs are absent, provide a conditional posture such as `observe`, `small exploratory`, `add after validation`, `reduce`, or `exit`, plus the evidence or price gate that changes it.

Use Kelly-style sizing only as a diagnostic upper bound when bets are sufficiently repeatable, payoffs and probabilities are estimable, losses are bounded, and cross-position dependence is modeled. Never present full Kelly or the approximation `mu / variance` as a universal recommendation. Shrink uncertain edge estimates, stress adverse correlation and tails, and cap any model-derived fraction:

```text
Exposure cap = min(
  robust fractional sizing estimate,
  maximum-loss budget,
  liquidity/capacity cap,
  factor/concentration cap
)
```

Explain which cap binds. If none can be estimated, do not fabricate a percentage.

## 5. Check Portfolio Factors And Stress Correlation

When portfolio holdings are available, map common exposures before calling the portfolio diversified: market beta, size, value/growth duration, momentum, volatility, rates, FX, commodity, geography, sector, liquidity, and any thesis-specific factor. Use the factors that fit the assets; do not force a fixed factor count.

Distinguish ticker count from independent risk bets. Inspect risk contribution and stressed correlation, because correlations that look low in normal periods can converge during deleveraging or liquidity shocks. If portfolio data is unavailable, name the likely overlaps and mark the portfolio conclusion unverified.

## 6. Treat Regime And Edge Decay As Updates, Not Oracles

Use regime evidence to update priors, expected payoff, and risk budget gradually. Do not make an unvalidated HMM or any single state classifier a hard top-level switch.

Track an explicit edge half-life and decay indicators: estimate revisions, valuation convergence, crowding, capacity, transaction costs, causal mechanism, and fresh out-of-sample performance where applicable. Diagnose decay rather than assuming every deterioration comes from crowding; possible causes include overfitting, structural change, data drift, execution cost, capacity saturation, or measurement failure.

## 7. Minimum Decision Output

When the data supports it, report:

1. Thesis quality and its dominant falsifier;
2. Price attractiveness and market-implied assumptions;
3. Scenario probabilities, net payoffs, weighted value, and dominant tail;
4. Which evidence is genuinely incremental versus overlapping;
5. Likely portfolio/factor overlap and stress caveat;
6. Exposure posture, binding constraint, and price/evidence gates;
7. Edge half-life, decay indicators, and next update time.
