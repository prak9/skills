# Mode B — Bayesian Intrinsic Growth Valuation

Use alongside Mode A by default for Standard/Full stock research, including a bare ticker, and for explicit Bayesian valuation, intrinsic versus implied growth, posterior updates or FOMO versus fundamentals. Start with coherent competing operating scenarios. A central numerical posterior requires evidence, not merely activation of this mode; when it is not identifiable, the final valuation still includes conditional probability sensitivity or a break-even probability. Business-only research can use the scenario/update lens without valuation.

The decision question is whether evidence-backed joint operating scenarios convert the company's value engine into attractive per-share net returns relative to the requirements of the current price. Choose a horizon appropriate to the business and decision; 3–5 years is an example, not a universal forecast window.

When the reverse-valuation question specifically uses PE and normalized EPS, [conditional PE implied growth](pe-implied-growth.md) provides an optional deterministic calculation. It produces neither priors nor posteriors and does not replace coherent joint scenarios.

When a reliable approximately one-year option surface is available, [the option-implied distribution](options-implied-distribution.md) can show which terminal prices the market currently makes expensive or cheap to insure. Keep those risk-neutral probabilities separate from evidence-based scenario probabilities: neither is a prior for the other without a justified bridge from state prices to real-world likelihoods.

## Inputs

Use a dated current quote, exact security, diluted shares, cash/debt and senior claims alongside verified company fundamentals, industry cycle, demand/supply, historical and guided growth, TAM and penetration, competitive position, valuation, price/multiple changes, consensus revisions, and the new information being evaluated. Mark missing inputs instead of manufacturing precision. A stale or mismatched quote makes the price comparison stale or mismatched; it does not invalidate business-only findings.

## Joint Hypotheses

Define scenarios from the company's actual earning mechanisms—contraction, normalization, share gain, or expansion as relevant. Do not assign universal growth buckets or midpoint values. Each scenario starts from a comparable normalized base and links paid volume, realized price/mix, contribution, fixed costs, capacity, growth duration, reinvestment/incremental returns, financing/dilution, and terminal conditions. Preserve material dependencies; high growth and low reinvestment, or volume above capacity without expansion, cannot be combined without an economic explanation.

Value each coherent scenario before aggregation:

```text
scenario inputs -> dated cash flows -> scenario equity value and net investor payoff
probability-weighted value = sum(p_s * V_s)
```

Use common valuation dates, currency, security basis, and return horizons. Growth-rate means may summarize the distribution but cannot replace it: generally `V(E[g]) != E[V(g)]`. State whether a scenario persists across years or transitions; those are different models. Withhold numeric values when the required inputs are absent rather than converting a growth midpoint into a target price. Probability-weighted values remain conditional on the valuation model and are not uniquely inferred market prices.

## Workflow

1. **Ground the prior.** Use an applicable reference class, company economics, cycle, TAM, and competition; expose selection and comparability limits. Put downside caution into scenario and risk tests rather than an arbitrary probability haircut. Market excitement alone does not justify an expansion scenario.
2. **Map each observation to a latent variable.** Write `observed signal -> latent growth/margin variable -> rival explanation -> disclosure lag`. Cluster observations caused by the same event; they are not independent confirmations.
3. **Update probabilities.** Show prior, likelihood interpretation, and posterior as points or ranges when supported, with mutually exclusive scenario point probabilities summing to 100%. Without a defensible likelihood or prior, mark the central distribution `不可识别` and use explicitly conditional probability sensitivity or solve for the break-even probability at which the price-value verdict changes; do not fabricate posterior precision to complete the format. Cyclical, one-off, or backlog-timing signals should not automatically raise long-run growth. If the mechanism or reporting entity changes, rebuild the model rather than force an update.
4. **Value the joint scenarios.** Carry the operating equation—volume, price/mix, take rate or spread, contribution, necessary fixed cost and capacity—through competitive capture, reinvestment, working capital, financing and net shares into scenario cash flows, equity values, and net investor payoffs before applying posterior probabilities. Show normalized versus peak/trough earnings, sensitivity and tail outcomes, not just weighted growth or an average target. Apply the shared numeric-data rules, including the direct-arithmetic path for wholly hypothetical examples; a data validator does not validate the economic model.
5. **Reverse-engineer the price.** Treat market-implied growth as an inverse problem, not a unique observable. Show combinations of growth duration, steady-state margin, reinvestment/ROIC, dilution, discount rate, and terminal value consistent with price. Name fixed assumptions and free variables. A price alone identifies neither a unique joint forecast nor scenario probabilities; do not present these solutions as observed sell-side consensus.
6. **Compare value with price requirements.** Identify the exact observed forecast or conditional hurdle that differs, what it already includes, the original evidence supporting the variant, its incremental per-share cash-flow effect and strongest rival. Show whether prospective return comes from distributions and retained-value compounding, multiple/price convergence, or both; a realization route must not be counted twice. Keep common assumptions fixed for attribution, then stress joint risks. Do not confuse public good news or an above-market target with an unpriced advantage. Keep the operating forecast independently evidenced rather than fitting it to a preferred verdict. Conclude attractive, unattractive, no demonstrated edge or unresolved only to the extent supported by the scenarios and estimation error.
7. **Measure price/fundamental divergence.** Separate changes in operating expectations from multiple expansion, liquidity, theme crowding, short squeeze, and index flow.
8. **Define verification.** Name competing observable predictions, the source and comparable metric, economically justified breakpoint, maturation/disclosure lag and decision effect. Where the decisive variable is unreported, expose proxy limitations instead of treating absent disclosure as falsification.

## Output

When integrated into Mode A, contribute the relevant scenarios, belief update, price requirements and uncertainty to one report; the standalone outline below is not a second mandatory report. Skip out-of-scope valuation/exposure sections for business-only work.

For company-level stock-opportunity or valuation work, the integrated report must close with one compact table containing: scenario and horizon; causal operating assumptions; normalized earnings/FCF and financing/dilution; analyst probability or conditional sensitivity; per-share value; return/downside from the dated quote; decisive evidence and falsifier. Follow it with the probability-weighted value/return when a distribution is defensible, or the break-even probability and valuation sensitivity when it is not. Then list the discriminating signals to observe and genuine potential catalysts within the next six months under the entrypoint's definitions. Do not merge option-implied risk-neutral probabilities into the analyst distribution.

```markdown
## Company And Decision
## Prior And Posterior Joint Scenarios
## Scenario Cash Flows, Values, Net Returns, And Tail
## Reverse-DCF / Market-Implied Joint Assumptions
## Price Versus Fundamental Update
## Valuation State And Scenario Range
## Upside Requirements And Downside Risks
## Verification Window, Falsifier, And Conditional Exposure Posture
## Sources And Missing Inputs
```

Keep thesis quality, valuation, and exposure separate. Position language must be conditional research guidance—observe, small test, add after proof, trade-only, reduce, or exit—not personalized instruction.
