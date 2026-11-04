# Columbia case and company-snapshot integration — 2026-11-04

## Source and scope

Read all nine ordered images of the user-supplied
[哥伦比亚商学院价值投资分享](https://www.xiaohongshu.com/explore/68e516430000000004022fcb).
Public-mobile retrieval acquired all nine with no missing page, cookies, account
or MCP. This is an edited secondary account, not a verified original lecture or
filing. No historical Timberland figures, ownership claims or returns were
promoted to primary financial facts.

The user's follow-up requests a compact Value Line-like company snapshot with
the key metrics and actual calculation process. Borrow the presentation idea,
not a recommendation rating, paid-data dependency or subscription advice.
[Columbia's primary methodological discussion](https://business.columbia.edu/insights/chazen-global-insights/value-investings-long-run)
was also read as a cross-check on distinguishing assets, current earning power
and future growth; it does not verify this secondary case's specific history.

## What changed, and what already existed

| Theme | Treatment |
|---|---|
| Whole-business ownership, normalized earnings, minority access | Already covered; retain rather than duplicate the philosophy. |
| Price-led search versus full underwriting | Refine the existing discovery branch: rough cheapness earns research priority, not eligibility or an investment verdict. |
| Asset protection and capital returns | Add explicit tax/average-capital reconciliation and no-double-counting checks; keep liquidation and going-concern states separate. |
| Panic/category contagion | Test direct and indirect transmission through contribution, fixed costs, collections and funding; a small revenue share can have a large profit effect. |
| Litigation and control | Inspect actual allegations, process, remedies and economic consequences; separate reputation, voting rights, conduct and accessible common-shareholder cash. |
| Timely action | Add readiness through prior work and decisive checks, without importing transaction authority, concentration or a fixed repricing clock. |
| Company snapshot | Add a compact lead board plus sourced formulas, substituted inputs, comparable periods, results and investment implications. Preserve full calculations without displaying every computable restatement. |

Do not adopt unsupported percentages of irrational investors, a guaranteed
18–24-month mean-reversion period, universal low-P/B or PE bands, high ROIC as
proof of a moat, reputation as proof of integrity, or insider/control access
available only to the historical investor.

The main entry adds one output contract; details stay in existing references.
No new valuation score, calculator dependency, data schema or cross-Skill
research dependency was introduced. Writing remains the only required
cross-Skill handoff for substantive reports. Existing causal sandbox, scenario
probabilities/valuation, options-market distinction and monitoring requirements
remain intact. Monitoring reuses valid history; narrow calculations keep scope.

## Verification

- invest passed quick_validate.py and scoped git diff --check.
- The full existing regression command passed: **472 tests, 699 subtests**.
- After the final presentation clarification, snapshot-fixture and Skill-contract
  checks passed again: **36 tests, 287 subtests**. No executable logic or test
  inputs changed after the full run.
- Six new visible development cases have numeric or semantic criteria.
  Unit tests independently recompute their arithmetic; this is fixture
  validation, not six executed model-behavior results.
- A separate fresh agent completed three supplied synthetic requests without
  seeing criteria, expected results or repository diff. The parent inspected
  full outputs and checked arithmetic against the fixture oracles. The
  [observed record](company-snapshot-observed.json) retains prompts, complete
  answers and self-reported actions.
- The first output was financially sound but overlisted auxiliary metrics.
  A focused presentation refinement was then retested on the same visible
  request, preserving the original. The revised output separates a compact
  lead board from complete calculations.

The three requests shared one context; the revision was a development retest,
not an independent repeat or old/new controlled comparison. Exact backend,
token, cost and independent action telemetry were unavailable. No real-company
forecast, live trading, legal merits investigation, publication or Notion write
was performed. These checks support the scoped contract, not general model,
cost or investment-performance improvement. Commit/push was not requested.

## ROIC coverage correction — 2026-11-04

Subsequent real use exposed a delivery failure: the BABA report discussed
uncertain AI investment returns but omitted group ROIC. The instructions
already defined ROIC, and the original synthetic ratio request explicitly
asked for it. That did not test whether an ordinary company report would
deliver the metric without being reminded. Project-data gaps also incorrectly
became a reason to leave out a separately reconstructible group return.

The entrypoint now makes ROIC coverage explicit for substantive non-financial
company reports. Mode A defines the delivered metric/status, comparable
history, calculation trail and specific unresolved inputs; business-quality
owns measurement detail. Historical group returns remain separate from
incremental/project returns, and construction/ramping capital is not removed
merely because it has yet to earn revenue. Banks and uninterpretable capital
bases retain appropriate alternatives, and narrow requests keep their scope.

Five additional visible development cases cover an implicit group-ROIC
request with missing project data, an unidentified operating tax rate,
investment maturation lag, a bank, and negative operating capital. The five
new fixture checks first failed on absent case IDs; after adding the packets,
all **11 fixture tests and 66 numeric subtests passed**. These are checked
fixtures and human-reviewed semantic criteria, not five executed model runs
or proof that the revised skill can no longer omit ROIC. The original observed
outputs remain unchanged. No new live research, external write or deployment
is part of this correction.

The final scoped suite (`invest/tests`, Skill contracts, hygiene and
simplification checks) passed **112 tests and 514 subtests**; skill validation
and scoped diff checks also passed. These checks do not evaluate a new model's
real-company report or update an already frozen external method snapshot.

## Official Value Line format alignment — 2026-11-04

The next request clarified that borrowing the compact-snapshot idea was not
enough: the user wants the classic Investment Survey information architecture.
Read the official [2024 Product Guide](https://investor.valueline.com/hubfs/Guides/1502514_Product_Guide_VLIS_WEB.pdf)
and [2017 reading guide](https://investor.valueline.com/hubfs/Guides/1503516_Reading_VL_Report_WEB_2.7.17.pdf),
and visually inspected their rendered Home Depot and Disney sample pages
(physical PDF pages 18 and 13 respectively). Cross-checked definitions against
official institutional education and the Small & Mid-Cap guide. No paid data,
account access or current issuer estimates were inferred from old samples.

The new [snapshot reference](../references/company-snapshot.md) owns the dated
quote header, annual metrics-as-rows/years-as-columns array, per-share fields,
capital/current-position panels, five/ten-year growth, recent reporting cadence
and separately labeled estimates/scenarios. Standard/Full seeks ten comparable
years when accessible; short history and incomplete years stay explicit.
Mode A no longer licenses replacing these fields with a few summary ratios.
Chat/Notion can reflow the page without claiming a pixel-identical vendor report.

Important boundaries are explicit: the Value Line earnings-plus-D&A cash proxy
is neither CFO nor FCF; its EBITDA-style margin is not reported EBIT margin;
its total-capital return is not automatically tax-adjusted ROIC; historical
average P/E differs from current-price P/E. Current/year-end/weighted-diluted
shares, preferred dividends, declared/paid distributions, equity denominators
and actual/estimated years retain their bases. ROIC remains a delivered metric
or an explicit gap. Vendor ratings and unidentified methods are not fabricated.

Four new development fixtures cover the statistical array and per-share cash
definitions, vendor/analyst accounting boundaries, incomplete fiscal years,
and an explicit narrow EPS request. The new checks first failed on the absent
case IDs; adding the fixtures produced **15 tests and 89 subtests passed**.
The scoped investment/Skill-contract/hygiene/simplification suite passed
**116 tests and 538 subtests**, and skill validation passed. These independently
check fixture arithmetic and repository invariants, **not four executed model
reports or a behavioral proof of layout compliance**. Original observed outputs
remain unchanged; no new real-company research, Notion write, commit, push or
deployment was requested as part of this alignment.
