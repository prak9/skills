---
name: invest
description: Generate source-backed buy-side equity research and thesis-change monitoring from a ticker or market signal. Routes between quick/full underwriting, Bayesian intrinsic-vs-implied growth, deterministic GF-DMA trend health, news-to-alpha transmission, and TAM-adjusted PEG; use for stock analysis, IC memos, valuation, thesis updates, catalysts, risks, or explicit specialist-lens requests.
---

# Invest

## Decision Contract

Start with the investment decision, not company background or a news digest. Turn the input into a decision-useful thesis, valuation range, probability update, trend-health result, or monitoring delta, with the evidence and threshold that could prove it wrong.

Replace point certainty with conditional scenarios. Keep these judgments separate:

- thesis quality and evidence;
- price/valuation attractiveness;
- exposure size and survivability.

Depth means resolving the causal and pricing dispute, not producing more sections or a more elaborate spreadsheet. A material investment claim needs a traceable chain: operating mechanism -> discriminating evidence -> independently supported forecast -> conditional price requirements -> per-share payoff -> observable falsifier. A source for a number is not automatically evidence for the inference built on it.

Distinguish a supported investment case, an illustrative valuation sensitivity, and an unresolved underwriting question. `No demonstrated edge` and `Too Hard at present` are valid conclusions, not reasons to abandon requested research. Complete accessible checks, identify the unsupported link and what would resolve it; do not invent a variant, target or probability to fill a template.

Treat every output as research analysis, not personalized investment advice. Never invent unavailable data. Mark it `未核验`, name the source that would confirm it, and narrow the conclusion.

## Route By Request

Load only the selected mode and the references it explicitly requires.

| Trigger | Route |
|---|---|
| bare ticker, “analyze this stock,” buy-side view, IC memo, full re-underwriting, or thesis update | [Mode A — Buy-Side Equity Research](references/mode-a-buy-side.md) |
| explicit Bayesian valuation, intrinsic versus implied growth, posterior update, or FOMO versus fundamentals | [Mode B — Bayesian Joint Scenarios](references/mode-b-bayesian-growth.md) |
| explicit GF-DMA, DMA/ATR health, price/DMA divergence, or EscapeRatio | [Mode C — GF-DMA](references/mode-c-gf-dma.md) |
| news, product/procurement/supply-chain signal, financial-statement transmission, or small-cap beneficiary search | [Mode D — Serenity Alpha](references/mode-d-serenity-alpha.md) |
| explicit TAM-Adj-PEG, runway-adjusted PEG, or quality-adjusted growth valuation | [Mode E — TAM-Adj-PEG Screening](references/mode-e-tam-adj-peg.md) |

For a narrowly requested PE-to-EPS-growth hurdle or its forward price calculation, load [conditional PE implied growth](references/pe-implied-growth.md) directly. This optional calculator does not require Mode B, a full company report, or a new probability model.

Do not trigger Modes B, C, or E from a bare ticker or generic stock-analysis request. They require an explicit request or a clearly stated Mode A crux. Do not load all modes for completeness.

## Select Depth Inside Mode A

- **Quick is the default** for a bare ticker or ordinary stock-analysis request: use current primary evidence and the minimum history needed to bound the crux, valuation, scenarios, thesis-killer, and next checks.
- **Full** applies when the user asks for deep/comprehensive research, an IC memo, a long history, integrated modeling, DCF/normalized EPS/reverse DCF, or re-underwriting. Mode A will load [the longitudinal underwriting loop](references/underwriting-loop.md).
- **Monitoring** uses the prior versioned thesis and reports only what changed. No material change means a concise `no thesis change` result with the evidence window checked.

Depth controls evidence breadth and model detail, not truthfulness. A Quick result must expose missing inputs; a Full result must not pad length with irrelevant history.

Proceed with the selected depth without asking the user to approve the route or supply facts available through authorized research. Ask only for a user-owned choice that materially changes the task and cannot be resolved from context. Missing consensus, history, or a model input narrows the claim; it does not automatically block all useful research. Complete the requested checks that remain possible and name any undelivered component instead of silently replacing Full research with Quick.

## Shared Source Discipline

For time-sensitive prices, market cap, filings, guidance, consensus, multiples, earnings calls, presentations, catalysts, technical data, or regulation, verify current information before using it.

Prioritize sources in this order:

1. SEC/local-exchange filings and exchange announcements;
2. company IR releases, presentations, and earnings calls;
3. customer, supplier, competitor, regulator, and industry-association disclosures;
4. reputable market-data/estimate providers and mainstream financial reporting.

Also actively discover original specialist research, public expert/customer interviews and technical fieldwork relevant to the crux. Use them for mechanisms, competing interpretations and missing operating detail; their authority does not turn an estimate into a reported fact. Full research includes the recent-three-month discovery pass in the underwriting reference.

For every material number or claim, preserve source, document type, publication/filing date, access date, and section/page when available. Distinguish:

- reported fact;
- management guidance or commentary;
- point-in-time consensus/third-party estimate;
- analyst inference.

Attach original-source citations next to material facts, numbers, quotations and thesis-bearing claims, including in tables; a bibliography alone is insufficient. Link the actual filing, report or interview, not a homepage or search result, with the date and page/section/timecode where available. Trace a report's borrowed claim to the original evidence; if inaccessible, cite the intermediary explicitly as `二手转引，原始证据未核验`. For original research or interviews, attribute the author's estimate or speaker's view and disclose inaccessible underlying data. A transcript proves what was said, not that the assertion is true. Label own calculations/inferences, cite their inputs and show the bridge; never attach a source as if it endorsed an analyst-derived target. Do not invent locators or imply full-text access from a snippet. Preserve these claim-to-source links in any authorized archive.

For each material numeric input also preserve value, unit, currency, period, accounting/estimate basis, first-available timestamp, and an explicit missing reason. Use the [material investment data contract](references/data-contract.md) for linked calculations, model reconstruction, or historical evaluation, and validate it with `scripts/validate_invest_data.py`. A Quick memo may use a compact table with the same semantics. Unknown is never zero; passing arithmetic checks does not prove that the source supports the claim.

For filing extraction, disputed source support or citation repair, read [financial evidence and claim audit](references/financial-evidence.md). Ground each locator in its document, check material extracted values against the original context, and distinguish a broken citation from an unsupported claim. Full research uses this audit before delivery; a supported Quick answer does not require a separate audit pipeline.

For self-contained hypothetical arithmetic supplied by the user, state the premises, units, and relative horizon and verify the formulas directly. Do not build a sourced-data ledger or require publication timestamps for invented companies or assumed scenarios. This exception does not cover real-company model reconstruction, sourced inputs, or historical point-in-time claims; retain the data contract for those portions of a mixed task.

Do not let current estimates, later restatements, or known outcomes leak into a historical decision reconstruction. Cluster evidence sharing one underlying event rather than counting it as independent confirmation.

For U.S.-listed companies, use current SEC/IR access as the factual baseline when available. Use `edgartools` only if already installed; installing software or configuring a real SEC identity requires explicit user authorization. SEC data does not replace current price, technical, consensus, TAM, share, or catalyst sources.

## Exposure And Monitoring

When the user asks about opportunity/risk, entry, sizing, portfolio fit, evidence overlap, or whether news changes a thesis, read [uncertainty and exposure](references/uncertainty-exposure.md). Use conditional research postures rather than individualized trading commands.

Monitoring must classify observations as no change, confidence update, valuation-only change, core-assumption breach, or new regime. Do not claim continuous monitoring, create alerts, or mutate a watchlist without both user authorization and persistent tooling.

## Skill Boundary And Handoff

`invest` owns investment-domain research. `decision` may choose among actions, `plan-skill` may maintain durable execution state, and `writing` may shape presentation. Preserve confirmed goals, constraints, conclusions, evidence, and citations; do not rerun upstream work unless they are missing or contradictory, and do not invoke all four by default.

## Notion Delivery

An analysis, full memo, monitoring request, or material thesis change **does not authorize a Notion write**.

Write only when the user explicitly requests it for the current task (including an earlier turn of that same unfinished task), or when an existing, unrevoked standing authorization clearly covers both this research type and the exact target. Reuse that authorization without asking again; revocation or a material scope/target change requires reevaluation. An unrelated prior write request is not standing authorization. A personal default belongs in user configuration, not this shared skill. Material change does not expand authorization.

When authorized:

- resolve exactly one target from the request, task context, and read-only search; ask only if multiple plausible destinations remain. Do not make the user repeat a target already resolved;
- preserve the as-of date, decision, crux, scenarios, citations, and falsifiers;
- for a monitoring update, append to the resolved prior thesis page rather than creating duplicates; a `no thesis change` entry is written only when the standing authorization explicitly includes routine logging;
- require a returned Notion page URL or ID and a proportionate readback of the destination/parent and expected content before claiming success. Report the direct link; a creation receipt alone does not establish that the complete report reached the requested location. If a write response is uncertain, check for the existing page before retrying to avoid duplicates.

If delivery is genuinely blocked after available in-scope resolution checks, deliver the research completed so far, distinguish research completeness from archive status, state `Notion archive pending`, and name the exact missing target or access. Do not call the overall task complete merely because the text is ready; continue an authorized archive when its blocker is resolved.
