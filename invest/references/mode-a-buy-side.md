# Mode A — Buy-Side Equity Research

Use this mode for a bare ticker, a general stock-analysis request, an investment-committee memo, full re-underwriting, or a thesis-change update.

## Select The Research Depth

**Quick research is the default for a bare ticker or ordinary “analyze this stock” request.** Use the latest annual filing, latest quarter, latest earnings call or official guidance, current price/valuation, current consensus when available, and only the peer or industry evidence needed to resolve the investment crux. Deliver a decision-useful view; do not simulate a ten-year underwriting exercise with missing data.

**Full research** applies when the user asks for deep/comprehensive research, an IC memo, a long historical reconstruction, a financial model, DCF/normalized EPS/reverse DCF, or re-underwriting. Read [underwriting-loop.md](underwriting-loop.md) for mechanism-level diligence, evidence-backed variants, assumption provenance, valuation attribution and observable falsification. Full means investigating the load-bearing claims, not filling a longer report outline.

**Monitoring** applies when the user asks what changed since a prior memo or requests material-change alerts. Use the prior versioned baseline when available and return only the delta. If nothing material changed, say `no thesis change`, name the evidence window checked, and do not regenerate background.

## Common Workflow

1. **Define the security and boundary.** Resolve company, exchange, ticker, fiscal year, reporting currency, business/segment structure, latest source set, and disclosure limits from context and sources. This is a research check, not a user confirmation step; ask only when unresolved ambiguity could select the wrong security.
2. **Form a provisional investment question.** Identify the price hurdle and rival explanations, then update the view through diligence; do not select a verdict and fit the model to it. Lead the final answer with horizon, current price, supported value/return range or qualitative bracket, the demonstrated gap (if any), and the breakpoint. Good business performance alone does not establish an attractive price.
3. **Map industry economics.** Locate the company in its value chain; identify suppliers, customers, substitutes, scarce inputs, bargaining power, profit pool, supply/demand cycle, and structural versus cyclical drivers. Explain who pays, why they cannot readily switch, who captures each incremental dollar, and what capacity, competition or incentive limits that capture.
4. **Assess competition and moat direction.** Compare share direction, margins, pricing power, switching costs, scale, network/data/R&D advantages, customer concentration, entrants, and substitutes. Say whether the moat is widening or narrowing.
5. **Rebuild only the economics required by the chosen depth.** Separate reported history, management guidance, sell-side consensus, and analyst assumptions. Link operating drivers to revenue, margins, reinvestment, FCF, dilution, and per-share value. For linked calculations or historical reconstruction, follow [the material data contract](data-contract.md) and run its validator. Full research uses the longitudinal underwriting reference; Quick research names missing history rather than inventing it.
6. **Discover and test the decisive value drivers.** Use the industry map, accounting bridges and value sensitivity to select them; do not merely rename management's KPIs. Usually one or two dominate; keep additional jointly necessary conditions when required. Follow each through cohort/segment/unit economics and its countervailing costs until the mechanism, evidence boundary and alternative explanation are clear. Distinguish observed consensus, conditional price-implied requirements and the analyst forecast. Revenue, costs, capital investment or dilution can be decisive.
7. **Value and reconcile.** Use SOTP when segments deserve different economics; otherwise choose DCF, normalized earnings, reverse DCF, EV/revenue, EV/EBITDA, P/E, P/FCF, NAV, or milestone valuation as appropriate. Full research triangulates rather than mechanically averaging methods. Always expose the assumptions that drive the range.
8. **Run coherent scenarios and oppose the thesis.** Show operating assumptions, valuation, return and triggers; use probabilities only when defensible, otherwise unweighted scenarios or clearly hypothetical probability sensitivity. Identify the dominant thesis-killer or smallest weakest-link set. Tie its threshold to economics, observable evidence and a realistic disclosure window rather than an arbitrary percentage or the stock price.
9. **Define catalysts and monitoring.** Track only events connected to model lines, market-implied hurdles, falsifiers, or decision gates. Separate thesis confidence, valuation attractiveness, and exposure posture.

Classify the asset as *mean-reverting*, *paradigm-shifting*, or *mixed*. A divergent view is useful only if evidence supports its accuracy and incomplete pricing, with a plausible realization path, edge half-life, and falsifier. Being non-consensus is not itself an edge.

## Expectations And Research Allocation

Keep sell-side consensus (an observed, dated estimate), price-implied requirements (conditional inverse-model solutions), and the analyst forecast (an evidence-backed hypothesis) separate. Missing consensus stays missing; it does not prevent a conditional reverse valuation. Show which assumptions are held fixed, and do not infer a unique growth rate or market probability distribution from one price. Quick research may state a qualitative hurdle when numeric inputs are insufficient.

Use reverse valuation to locate the hurdle, not to tune the independent forecast until the desired mispricing appears. Trace the variant to primary evidence, its strongest rival explanation, and the observation/date that would resolve it. Forward and reverse models sharing assumptions are not independent confirmations.

Before claiming a non-consensus opportunity, state exactly which forecast differs, whose dated expectation is observed, what price condition it changes, and why credible investors could still disagree. Publicly known good news may already be priced; a target above the quote is not evidence that the market missed something. A positive or negative gap is conditional on the supported economics, not proof of market psychology. Report `no demonstrated edge` when the chain does not survive the rival case.

Investigate available decision-changing evidence now: follow a relevant footnote, call Q&A, customer/competitor disclosure, underlying dataset or failed guidance instead of leaving an accessible check on a generic next-steps list. Select sources for the claim they can test, not a source-count quota. Distinguish company assertions from external verification, and multiple publishers from independent underlying observations. Do not arrange interviews, purchase data or seek nonpublic information without applicable authorization.

Separate research commitment from capital commitment. After the requested scope is complete, prefer the cheapest additional evidence that could change the decision; defer low-information interviews or more background reading. Complete useful analysis now, state the unresolved condition and review trigger, and do not buy merely to justify exploration. In repeated research, preserve dated shortlisted and unchosen opportunities so selection can be reviewed without hindsight. Use existing `decision` or `research-craft` outputs when supplied; do not require another skill or ledger for a one-off memo.

Separate user-strategy exclusion, unattractive price and insufficient understanding. An unfamiliar term calls for a concrete definition and economic example, not automatic rejection. Use `Too Hard at present` only for an essential mechanism/payoff that remains unbounded after feasible inquiry; name the unresolved link, completed checks and reopening evidence. Neither a three-variable cutoff nor multiplying dependent event probabilities measures complexity. Research can be complete with an unresolved investment verdict; lack of a verdict cannot excuse omitting feasible requested work.

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
- Demonstrated gap or no demonstrated edge; strongest rival explanation
- Dominant falsifier, economic threshold, observable source and disclosure window

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
- Mechanism and net value capture; cohort/segment evidence and offsetting effects
- Claim -> original observation -> inference -> strongest rival -> discriminating result
- Observed expectation, price hurdle, independent range and its evidence anchor

## 5. Valuation Triangulation
- SOTP or appropriate primary method
- DCF / normalized EPS / reverse DCF when applicable
- Price-to-value bridge attributable to the variant; fixed assumptions and joint sensitivity
- Load-bearing forecast support, cross-forecast consistency, terminal dependence and unsupported portions

## 6. Bull / Base / Bear
| Scenario | Probability | Core assumptions | Value | Implied return | Trigger |
|---|---:|---|---:|---:|---|

Probability may be N/A. Distinguish present-value gaps from dated holding-period returns.

## 7. Variant Perception And Dominant Thesis-Killer
- Specific pricing disagreement or no demonstrated edge; why the rival could be right
- Evidence required to reject our interpretation, economic threshold, source, lag and consequence

## 8. Catalysts, Risks, And Monitoring
- Event, timing, expected evidence, decision effect
- Versioned assumptions and prior forecast-versus-actual calibration

## 9. Sources And Unverified Inputs
```

## Quality Bar

Do not replace analysis with a news summary, context dump or unsupported spreadsheet. Can the reader trace the decisive claim from raw evidence to net per-share economics, identify what the comparison view already knows, and specify an observation that would change the verdict? If not, expose the failed link rather than add confident prose. Do not extrapolate historical growth mechanically. Reconcile demand, capacity, revenue, margins, opex, capex, working capital, FCF, dilution and terminal value. Preserve prior forecasts instead of rewriting them with hindsight. Use the output sections as an adaptable structure, not evidence that diligence is complete.
