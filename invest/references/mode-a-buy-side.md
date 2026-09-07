# Mode A — Buy-Side Equity Research

Use this mode for a bare ticker, a general stock-analysis request, an investment-committee memo, full re-underwriting, or a thesis-change update.

## Select The Research Depth

**Quick research is the default for a bare ticker or ordinary “analyze this stock” request.** Use the latest annual filing, latest quarter, latest earnings call or official guidance, current price/valuation, current consensus when available, and only the peer or industry evidence needed to resolve the investment crux. Deliver a decision-useful view; do not simulate a ten-year underwriting exercise with missing data.

**Full research** applies when the user asks for deep/comprehensive research, an IC memo, a long historical reconstruction, a financial model, DCF/normalized EPS/reverse DCF, or re-underwriting. Read [underwriting-loop.md](underwriting-loop.md) and build the auditable evidence/model chain it specifies.

**Monitoring** applies when the user asks what changed since a prior memo or requests material-change alerts. Use the prior versioned baseline when available and return only the delta. If nothing material changed, say `no thesis change`, name the evidence window checked, and do not regenerate background.

## Common Workflow

1. **Define the security and boundary.** Resolve company, exchange, ticker, fiscal year, reporting currency, business/segment structure, latest source set, and disclosure limits from context and sources. This is a research check, not a user confirmation step; ask only when unresolved ambiguity could select the wrong security.
2. **Lead with the investment view.** State horizon, current price, valuation range or qualitative bracket, and supported upside/downside. Connect the price-implied operating hurdle to an independently supported variant, its per-share value effect, and the breakpoint that would force re-underwriting. Good business performance alone does not establish an attractive price.
3. **Map industry economics.** Locate the company in its value chain; identify suppliers, customers, substitutes, scarce inputs, bargaining power, profit pool, supply/demand cycle, and structural versus cyclical drivers.
4. **Assess competition and moat direction.** Compare share direction, margins, pricing power, switching costs, scale, network/data/R&D advantages, customer concentration, entrants, and substitutes. Say whether the moat is widening or narrowing.
5. **Rebuild only the economics required by the chosen depth.** Separate reported history, management guidance, sell-side consensus, and analyst assumptions. Link operating drivers to revenue, margins, reinvestment, FCF, dilution, and per-share value. For linked calculations or historical reconstruction, follow [the material data contract](data-contract.md) and run its validator. Full research uses the longitudinal underwriting reference; Quick research names missing history rather than inventing it.
6. **Concentrate on the decisive value drivers.** Usually one or two dominate; keep additional jointly necessary conditions when the economics require them, not to fill a quota. For each, distinguish observed consensus, conditional price-implied requirements, and the analyst forecast; show valuation sensitivity, source evidence, and the next discriminating observation. Revenue, costs, or capital investment can be decisive.
7. **Value and reconcile.** Use SOTP when segments deserve different economics; otherwise choose DCF, normalized earnings, reverse DCF, EV/revenue, EV/EBITDA, P/E, P/FCF, NAV, or milestone valuation as appropriate. Full research triangulates rather than mechanically averaging methods. Always expose the assumptions that drive the range.
8. **Run Bull/Base/Bear and oppose the thesis.** Show probabilities, operating assumptions, valuation, return, and triggers. Identify the dominant thesis-killer with a threshold and deadline, or the smallest honest weakest-link set.
9. **Define catalysts and monitoring.** Track only events connected to model lines, market-implied hurdles, falsifiers, or decision gates. Separate thesis confidence, valuation attractiveness, and exposure posture.

Classify the asset as *mean-reverting*, *paradigm-shifting*, or *mixed*. A divergent view is useful only if evidence supports its accuracy and incomplete pricing, with a plausible realization path, edge half-life, and falsifier. Being non-consensus is not itself an edge.

## Expectations And Research Allocation

Keep sell-side consensus (an observed, dated estimate), price-implied requirements (conditional inverse-model solutions), and the analyst forecast (an evidence-backed hypothesis) separate. Missing consensus stays missing; it does not prevent a conditional reverse valuation. Show which assumptions are held fixed, and do not infer a unique growth rate or market probability distribution from one price. Quick research may state a qualitative hurdle when numeric inputs are insufficient.

Use reverse valuation to locate the hurdle, not to tune the independent forecast until the desired mispricing appears. Trace the variant to primary evidence, its strongest rival explanation, and the observation/date that would resolve it. Forward and reverse models sharing assumptions are not independent confirmations.

Separate research commitment from capital commitment. After the requested scope is complete, prefer the cheapest additional evidence that could change the decision; defer low-information interviews or more background reading. Complete useful analysis now, state the unresolved condition and review trigger, and do not buy merely to justify exploration. In repeated research, preserve dated shortlisted and unchosen opportunities so selection can be reviewed without hindsight. Use existing `decision` or `research-craft` outputs when supplied; do not require another skill or ledger for a one-off memo.

Treat positive FCF, accelerating revenue, founder ownership, or a ten-year runway as strategy-specific filters or evidence, not universal inclusion rules. Mature cash distributions, cyclical normalization, and investment-phase losses require different economics. Fixed PE bands and percentage discounts are user strategy parameters when explicitly chosen, not fair-value laws; translate them into conditional net returns and test the underlying assumptions. A risk-free yield is not the equity discount rate. Long-term moat analysis does not imply precise annual profit forecasts for a decade.

## Optional Specialist Lenses

Load another mode only when it resolves the crux:

- [mode-b-bayesian-growth.md](mode-b-bayesian-growth.md) for intrinsic versus market-implied growth;
- [mode-c-gf-dma.md](mode-c-gf-dma.md) for a requested trend/entry-health calculation with adequate technical data;
- [mode-d-serenity-alpha.md](mode-d-serenity-alpha.md) for news, procurement, product, or supply-chain transmission;
- [mode-e-tam-adj-peg.md](mode-e-tam-adj-peg.md) for growth-duration and TAM-supported valuation.

## Quick Output

```markdown
# [Company / Ticker] — Quick Investment View

## Decision
- Bias, horizon, current price, valuation bracket, expected return range
- Core thesis, market-implied expectation, confidence, and breakpoint

## Evidence That Matters
- Latest reported facts and guidance
- Dated sell-side consensus, if available
- Conditional price-implied requirements versus the independent forecast
- Independent or contradictory evidence

## Economics And Valuation
- Key drivers and financial transmission
- Base/Bull/Bear assumptions and range
- What must be true at the current price

## Variant View And Thesis-Killer
- What may be mispriced
- Dominant falsifier, threshold, and deadline

## Catalysts And Next Checks
- Cheapest decision-changing check, exact metric, and next review point

## Sources And Missing Inputs
```

## Full Output

```markdown
# [Company / Ticker] Buy-Side Equity Research Memo

## 0. Executive Investment View
- Rating bias, horizon, target range, current price, implied return
- Core thesis, debate, variant perception, confidence, thesis breakpoint

## 1. Company And Source Boundary
- Business/segment/geography/customer mix
- Reporting basis and latest point-in-time source set

## 2. Industry Chain And Competition
- Value chain, profit pool, bargaining power, cycle, moat direction

## 3. Financial Model
- Revenue and segment drivers
- Gross/operating margin, capex, working capital, FCF, dilution
- Material capital uses, incremental returns, and competitive-advantage fade
- Reported / guidance / consensus / analyst reconciliation

## 4. Key Value Drivers
- Decisive driver, consensus, price hurdle, independent range, sensitivity, falsifier

## 5. Valuation Triangulation
- SOTP or appropriate primary method
- DCF / normalized EPS / reverse DCF when applicable
- Cross-forecast consistency and sensitivity

## 6. Bull / Base / Bear
| Scenario | Probability | Core assumptions | Value | Implied return | Trigger |
|---|---:|---|---:|---:|---|

## 7. Variant Perception And Dominant Thesis-Killer
- Price-expectation gap and supporting evidence, edge half-life, falsifier, threshold, deadline

## 8. Catalysts, Risks, And Monitoring
- Event, timing, expected evidence, decision effect
- Versioned assumptions and prior forecast-versus-actual calibration

## 9. Sources And Unverified Inputs
```

## Quality Bar

Do not replace analysis with a news summary or context dump. Do not extrapolate historical growth mechanically. Reconcile contradictions across demand, capacity, revenue, margins, opex, capex, working capital, FCF, dilution, and terminal value. Preserve prior forecasts instead of rewriting them with hindsight. Mark missing or unverifiable inputs and narrow the conclusion accordingly.
