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

Treat every output as research analysis, not personalized investment advice. Never invent unavailable data. Mark it `未核验`, name the source that would confirm it, and narrow the conclusion.

## Route By Request

Load only the selected mode and the references it explicitly requires.

| Trigger | Route |
|---|---|
| bare ticker, “analyze this stock,” buy-side view, IC memo, full re-underwriting, or thesis update | [Mode A — Buy-Side Equity Research](references/mode-a-buy-side.md) |
| explicit Bayesian valuation, intrinsic versus implied growth, posterior update, or FOMO versus fundamentals | [Mode B — Bayesian Growth](references/mode-b-bayesian-growth.md) |
| explicit GF-DMA, DMA/ATR health, price/DMA divergence, or EscapeRatio | [Mode C — GF-DMA](references/mode-c-gf-dma.md) |
| news, product/procurement/supply-chain signal, financial-statement transmission, or small-cap beneficiary search | [Mode D — Serenity Alpha](references/mode-d-serenity-alpha.md) |
| explicit TAM-Adj-PEG, runway-adjusted PEG, or quality-adjusted growth valuation | [Mode E — TAM-Adj-PEG](references/mode-e-tam-adj-peg.md) |

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

For every material number or claim, preserve source, document type, publication/filing date, access date, and section/page when available. Distinguish:

- reported fact;
- management guidance or commentary;
- point-in-time consensus/third-party estimate;
- analyst inference.

For each material numeric input also preserve value, unit, currency, period, accounting/estimate basis, first-available timestamp, and an explicit missing reason. Use the [material investment data contract](references/data-contract.md) for linked calculations, model reconstruction, or historical evaluation, and validate it with `scripts/validate_invest_data.py`. A Quick memo may use a compact table with the same semantics. Unknown is never zero; passing arithmetic checks does not prove that the source supports the claim.

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
