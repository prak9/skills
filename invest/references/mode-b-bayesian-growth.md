# Mode B — Bayesian Intrinsic Growth Valuation

Use only when the user explicitly asks for Bayesian valuation, intrinsic versus implied growth, posterior growth hypotheses, or FOMO versus fundamentals. Do not trigger from a bare ticker.

The decision question is whether a sourced probability distribution for 3–5 year growth and margins is better or worse than the joint assumptions embedded in the current enterprise value.

## Inputs

Use verified company fundamentals, industry cycle, demand/supply, historical and guided growth, TAM and penetration, competitive position, valuation, price/multiple changes, consensus revisions, and the new information being evaluated. Mark missing inputs instead of manufacturing precision.

## Growth Hypotheses

| Hypothesis | Label | 3–5Y revenue CAGR | Suggested midpoint |
|---|---|---:|---:|
| H0 | contraction | <0% | -5% |
| H1 | mature slow growth | 0%–5% | 2.5% |
| H2 | steady growth | 5%–12% | 8.5% |
| H3 | high-cycle growth | 12%–25% | 18.5% |
| H4 | structural breakout | 25%–50% | 37.5% |
| H5 | platform expansion | >50% | 60% or scenario-specific |

## Workflow

1. **Set a conservative prior.** Use base rates, company economics, cycle, TAM, and competition. Market excitement alone does not justify H4/H5.
2. **Map each observation to a latent variable.** Write `observed signal -> latent growth/margin variable -> rival explanation -> disclosure lag`. Cluster observations caused by the same event; they are not independent confirmations.
3. **Update probabilities.** Show prior, likelihood interpretation, and posterior as ranges. Cyclical, one-off, or backlog-timing signals should not automatically raise long-run growth. If the mechanism or reporting entity changes, rebuild the model rather than force an update.
4. **Calculate weighted intrinsic growth.** Use the posterior and declared midpoints; show sensitivity rather than decimal-level confidence.
5. **Reverse-engineer the price.** Treat market-implied growth as an inverse problem, not a unique observable. Show combinations of growth duration, steady-state margin, reinvestment/ROIC, dilution, discount rate, and terminal value consistent with price.
6. **Compare intrinsic and implied distributions.** Label the valuation low, aligned, expensive-but-tradable, or bubble-like; do not call a high-quality company cheap merely because growth is high.
7. **Measure price/fundamental divergence.** Separate changes in operating expectations from multiple expansion, liquidity, theme crowding, short squeeze, and index flow.
8. **Define verification.** Name the next 1–4 quarter evidence, posterior-changing threshold, and falsifier.

## Output

```markdown
## Company And Decision
## Prior And Posterior Growth Table
## Weighted Intrinsic Growth Range
## Reverse-DCF / Market-Implied Joint Assumptions
## Price Versus Fundamental Update
## Valuation State And Scenario Range
## Upside Requirements And Downside Risks
## Verification Window, Falsifier, And Conditional Exposure Posture
## Sources And Missing Inputs
```

Keep thesis quality, valuation, and exposure separate. Position language must be conditional research guidance—observe, small test, add after proof, trade-only, reduce, or exit—not personalized instruction.
