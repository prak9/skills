---
name: invest
description: Research public companies and stocks using filings, earnings calls, business quality, valuation, and thesis monitoring. Use for U.S., Hong Kong, or A-share equity analysis.
---

# Invest

## Research Contract

Answer the requested question, not a report template. The causal spine is **how the business earns money, why it retains a profit spread, whether that can persist, how much owner cash it can produce, and what reaches the owned security per diluted share relative to the price paid**.

Separate customer value, industry or national progress, company success, security value and price attractiveness. Follow value from customer need and willingness to pay through charging unit, realized price/volume, costs, capital needs, taxes, debt, governance and dilution. Locate who captures the benefit, who bears the cost, and the weakest link. Growth without adequate incremental returns or shareholder access need not create investor value. A low quote cannot repair missing rights or a broken earnings engine.

Reconstruct normalized and future earning power from economic drivers. Distinguish structural returns from cycle, scarcity, subsidy, acquisitions, accounting timing, underinvestment and financing. Identify the proposed return source—business compounding/distributions, mispricing convergence, risk compensation or prediction of other holders—and its evidence, horizon and realization conditions. Treat price as a dated offer and informative observation, neither proof of value nor an instruction.

The central work is **investment logic and verification of its key assumptions**. Seek evidence that changes an estimate, separates rival explanations or exposes a constraint; complete accessible decisive checks. Convert “inevitable” claims into necessary conditions and falsifiers. No forced contrarianism, novelty, source quota or composite score. An unresolved case or no demonstrated edge is valid. Mark missing inputs `未核验` and bound the conclusion rather than manufacture precision.

Substantive company reports include a compact **company snapshot with reproducible calculations**: the material operating, financial, capital-return and price/valuation metrics, their comparable history where available, and what changes the investment judgment. For derived metrics show the formula, substituted inputs, units/period/basis, result and sources; a ratio or rating alone is insufficient. Use [the snapshot contract](references/mode-a-buy-side.md#company-snapshot-and-calculation-trail), adapting metrics to the business without expanding narrow requests.

## Select The Needed References

For general company research, read [buy-side research](references/mode-a-buy-side.md). Standard multi-dimensional analysis is the default; Quick requires a brief/quick request, Full covers deep research, IC memos, re-underwriting and substantive model reconstruction, and Monitoring updates affected prior claims. Depth does not mean a separate report for every analytical lens.

| Need | Reference |
|---|---|
| Business-only work, bare ticker or stock-opportunity research | [A — Buy-side research](references/mode-a-buy-side.md) |
| Stock-opportunity/valuation conclusion, competing future paths or belief updates | [B — Joint scenarios and causal sandbox](references/mode-b-bayesian-growth.md) |
| Policy, macro, technology or household-wealth narrative carries the thesis | [Value transmission](references/value-transmission.md) |
| AI/cloud cost, capex or compute utilization carries the thesis | [AI/cloud economics](references/ai-cloud-costs.md) |
| Material product, contract, supply, cost or regulatory change | [D — News to financials](references/mode-d-serenity-alpha.md) |
| Principles, ability boundary, purchasing power or capital-duration fit | [Ownership discipline](references/value-investing-discipline.md) |
| Opportunity search or candidate-universe review | [Opportunity discovery](references/opportunity-discovery.md) |
| One-year option-implied terminal-price probabilities | [Option-implied distribution](references/options-implied-distribution.md) |
| Conditional PE-to-growth or forward-price arithmetic | [PE implied growth](references/pe-implied-growth.md) directly |
| Standalone filing/call extraction | [Financial extraction](references/financial-extraction.md) or [calls](references/earnings-transcripts.md) directly |
| Explicit GF-DMA or TAM-Adj-PEG calculation | [C — GF-DMA](references/mode-c-gf-dma.md) or [E — TAM-Adj-PEG](references/mode-e-tam-adj-peg.md); uncalibrated heuristics, not default valuation models |

Broad research proactively covers economics, competition/runway, financial architecture, expectations, relevant changes and downside. More perspectives mean different questions and evidence, not more LLM calls or votes. Analyze price/fundamental divergence and profitable growth duration directly in the operating/scenario model; neither requires loading C/E or calculating their scores. A single-company request does not authorize a universe sweep.

## Evidence And Numeric Integrity

Verify current prices, filings, guidance, estimates, regulations and event dates. Prefer original exchange/regulatory filings and company IR for reported facts; challenge interpretations with customer, supplier, competitor, regulator and industry evidence. Third-party research can add mechanisms or estimates, but repeated management claims are not independent confirmation.

Cite material claims and table inputs inline with the original document, date and actual section/page/timecode when available; retain access dates. Distinguish reported facts, management statements, dated third-party estimates and analyst assumptions. Trace borrowed claims or label `二手转引，原始证据未核验`. A transcript proves what was said, not that it is true. Never invent locators or claim full-text access from snippets. Show calculations and cite their inputs.

Retain numeric value, unit, currency, period, accounting/estimate basis, first-available timestamp and missing reason. For linked models or historical evaluation use [the data contract](references/data-contract.md) and `scripts/validate_invest_data.py`; Quick may express equivalent semantics compactly. Unknown is not zero. Hypothetical arithmetic needs explicit premises and checked formulas, not a fabricated source ledger. Preserve point-in-time cutoffs and prevent later revisions/outcomes leaking backward.

Distinguish stocks, flows, transaction amounts, price changes and revaluations; preserve denominator, population and period comparability. Similar magnitudes or simultaneous changes do not establish money transfer or causality. Use [financial evidence](references/financial-evidence.md) for disputed support, citation repair and Full's final claim audit; follow [PDF retrieval](references/pdf-retrieval.md) when material filings are inaccessible. Missing data narrows affected claims, not all feasible research.

Use existing SEC/IR access; `edgartools` is optional, not an installation prerequisite. Do not buy data, configure a real SEC identity, contact experts or obtain nonpublic information without applicable authorization.

## Required Scenario And Valuation Conclusion

Every company-level investment-value, stock-opportunity or valuation report ends with a coherent **forward scenario distribution and valuation synthesis**. Business-only work, raw extraction and explicitly narrow calculations are exempt unless an investment/valuation conclusion is requested.

Before final probabilities or the verdict, perform [the causal sandbox](references/mode-b-bayesian-growth.md#causal-sandbox-before-scenario-judgment). Begin from dated operating/financial facts; introduce material changes and trace participant responses through time, feedback, capacity/funding constraints and dilution into per-share outcomes. Show the decision-relevant derivation: **premise/evidence → causal transmission → financial lines → valuation/return → falsifier**. This auditable argument is not private chain-of-thought. Quick can compress it, not bypass it.

Use a small mutually exclusive, collectively exhaustive set of business-specific future states over a stated horizon. For each show operating assumptions, normalized earnings/owner cash, material financing/dilution, analyst probability or range, per-share value, return from the dated quote, evidence and falsifier. Point probabilities sum to 100%; explain their basis and confidence. If a central distribution is `不可识别`, still show conditional probability sensitivity or break-even probabilities and their valuation consequence. Do not replace the distribution with one average target.

Compare independent earning/value ranges with the operating and capital-allocation combinations required by the current price. One quote does not identify unique forecasts or probabilities. State valuation basis, horizon and estimation error before calling the stock cheap or expensive.

For stock-opportunity work, attempt the approximately one-year options distribution when a liquid chain and reproducible inputs are accessible. It is a dated **risk-neutral market-pricing distribution**, not an objective forecast or analyst posterior. If the chain, rate, corporate-action treatment or no-arbitrage fit is unreliable, state `期权隐含分布不可可靠估计` and why.

Close with **signals to observe** (baseline, discriminating expected direction/range, source/date, threshold and implication for probabilities/value) and genuine **potential catalysts in the next six months** (date/window, transmission, scenario affected and what may already be priced). A scheduled event is not a catalyst without that link; say when none is identifiable.

## Downside, Exposure And Updates

For opportunity/risk, sizing, allocation comparisons, evidence overlap or a thesis-changing event, read [uncertainty and exposure](references/uncertainty-exposure.md), including adversarial underwriting before concentration. Keep business quality, valuation and capital commitment separate; gains or losses alone do not justify adding.

Monitoring distinguishes no change, confidence update, valuation-only change, assumption breach and new regime. Reuse valid history and preserve prior judgments. Research does not authorize trades, watchlist mutation, alerts or continuous monitoring; those require authority and actual persistent tooling.

## Skill Boundary And Handoff

`invest` independently owns company evidence, competing hypotheses, financial reconstruction, valuation and thesis monitoring. It must not require or invoke another Skill for these responsibilities. Its only cross-Skill dependency is the substantive-report writing pass below; use available tools directly for authorized persistence, extraction and delivery. Boundary and handoff: do not rerun upstream work unless missing or contradictory, and do not invoke all four by default.

### Required Writing Pass For Final Articles

For a substantive report, memo or article-form update—including chat delivery—read and apply [writing](../writing/SKILL.md) and actually perform its whole-document rhetoric review (全文修辞复核). Detailed writing references are conditional, not three mandatory files on every report. Pure calculations, raw extraction and brief status retain their scope.

Preserve conclusion, cutoff, units, assumptions, probability/valuation math, contrary evidence, limits and claim-level citations. Reorganize self-written outlines around the reader's investment question; combine repetitive conclusions and remove internal process narration without losing distinct evidence or local qualifiers. Reconcile text and tables after revision. Writing does not change research conviction or authorize publication.

## Notion Delivery

Research **does not authorize a Notion write**. Use a current request or unrevoked standing authorization covering this research and target. Resolve ambiguity with read-only discovery before asking; do not reuse an unrelated destination.

For company research use **one canonical company subpage per issuer** under the authorized investment parent, with dated reports/updates as children. Search official name and primary ticker before creating a hub; listings/share classes normally share it. Comparison reports can link hubs. Do not move historical pages without authorization.

Preserve dated thesis, scenarios, falsifiers and inline sources; fit the authorized revision, appendix or dated-update scope without duplicating full chat answers. Verify returned ID/URL, **company-hub parent**, destination and expected content with proportionate readback. Check whether an uncertain write succeeded before retrying.

If archiving is blocked after feasible checks, deliver the research with `Notion archive pending`, the precise missing access/target and recovery action. An authorized unfinished archive remains required work, separate from research completeness.
