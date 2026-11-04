# Value Line-Aligned Company Snapshot

Use for the company snapshot in substantive company reports. Align the information architecture and core fields with the classic **Value Line Investment Survey** page; do not claim to reproduce a licensed report, proprietary ratings or vendor-calculated values. This is the snapshot contract, not a template for the entire investment argument. Narrow calculations, raw extraction and price-only monitoring keep their scope.

## Output Order And Layout

After the concise research answer, deliver these linked panels. Chat/Notion may stack the printed side panels vertically and split a wide matrix into adjacent year blocks with the same rows. Do not reduce the snapshot to three years of a few headline ratios when a longer comparable series is accessible.

| Panel | Required content and boundaries |
|---|---|
| Quote header | Company, ticker/exchange, owned security/ADS ratio, cutoff, fiscal year-end, reporting/trading currencies; dated price, market cap, explicitly defined TTM/forward P/E and dividend yield when price analysis is in scope. Historical median and relative P/E require actual comparable data and a named benchmark. |
| Price context | When reliable history is available, show a multi-year price/volume chart or dated annual high/low and total-return table, with split/dividend adjustments and benchmark. Beta requires its window, frequency and benchmark; insider/institutional activity can add context when verified and relevant, not inferred from price. Distinguish historical price from future value. Missing history is disclosed, not drawn from imagination. |
| Annual statistical array | The core matrix below: continuous annual actuals, latest reported/TTM where meaningful, then separately labeled estimates. Seek ten years for Standard/Full when accessible; respect issuer age, scope changes and supplied-data limits. |
| Capital structure and current position | Dated debt/equity/claims and recent balance-sheet components, as below. |
| Annual growth rates | Past ten-year, five-year and conditional future 3–5-year per-share growth, where supported. |
| Recent reported periods | Revenue, diluted EPS and dividends paid by the issuer's actual reporting cadence, plus an annual total only when available/reconstructible. |
| Future value and business note | For investment/valuation work, show dated 3–5-year per-share value ranges, gain/loss from the quote and annualized total-return assumptions, linked to the independently modeled scenario paths and probabilities; the final report still ends with the scenario synthesis. Briefly explain the earnings engine, decisive change and risks. Business-only work does not acquire a target-price requirement. |
| Definitions and calculation trail | Source keys, fiscal/calendar timing, share/ADS/FX bases, adjustments, missing reasons and calculations; not a link to an unexplained spreadsheet. |

Use `A` for reported actuals, `E` for analyst estimates and `S` for conditional scenarios. These are this report's labels, not Value Line ratings. Never relabel management guidance as realized results or analyst estimates as official forecasts. Proprietary Timeliness/Safety/Technical, financial-strength, price-stability or predictability ratings can share one note: `Value Line 专有评级未获取`; do not invent equivalents under the brand.

## Core Annual Statistical Array

Columns: `指标/口径 | FY…A | … | 最新完整FYA | TTM/已报期间 | 当年E | 次年E | 3–5年S | 来源/注`.

Enumerate actual fiscal years and projected endpoints in delivery; the ellipses here describe layout, not permission to omit the historical table. An incomplete current year belongs in a dated YTD/H1 column, not a full-year actual column. Keep unsupported forecast cells `未估计` with a shared reason. A scenario cell can link to bear/base/bull values rather than conceal them in one point estimate.

Retain these core rows in this order for a non-financial company. Where an entire group is unavailable, one explicit grouped missing-data note may replace empty rows; **ROIC retains its own result/status row**. Inapplicable industry metrics may be replaced with named, economically appropriate alternatives and the reason.

| Group | Rows, in order |
|---|---|
| Per-share history | Revenue/share; Value Line-style cash proxy/share; diluted EPS; declared common dividends/share; cash capex/share; common book value/share; year-end common shares. |
| Annual market measures | Average annual P/E; relative annual P/E with named benchmark; average annual dividend yield. These are historical-year measures, not today's quote divided by old earnings. |
| Financial scale and profitability | Revenue; Value Line-style operating margin with definition; depreciation/amortization; net profit with attribution/adjustment basis; income-tax rate with tax base; net margin. |
| Capital and allocation | Working capital; long-term debt; shareholders' equity; Value Line total-capital return **only if actually obtained and identified**; shareholder-equity return with denominator basis; retained earnings/common equity; all dividends/net profit. Keep an explicit unavailable status for the vendor capital-return row if not reproducible. |
| Required analytical extensions | Reported EBIT margin; CFO; cash capex; labeled FCF proxy; NOPAT; average operating invested capital; **after-tax ROIC**. Add gross margin, cash conversion and the few sector KPIs that explain this company's economics. |

Distinguish reported net profit/EPS from normalized or vendor-adjusted values; footnote nonrecurring/discontinued operations and reconcile adjustments. Retain total-company rows beside per-share rows so buybacks, dilution and asset growth cannot masquerade as operating improvement. Do not silently restate historical denominators using today's shares.

### Capital Structure And Current Position

- **Capital structure, as of a date:** gross debt, amounts due within five years and maturity concentrations; long-term debt, interest coverage, material leases/pensions/other senior claims; preferred/common stock, current shares and market cap. State whether lease claims are already included to prevent double counting.
- **Current position:** two comparable year-ends and latest balance-sheet date when available. Show cash/investments with restricted/required/excess distinctions, receivables, inventory, other current assets, total current assets; payables, debt due within one year, other current liabilities and total current liabilities. Traditional working capital is current assets minus current liabilities, not operating working capital.
- Banks/insurers retain the longitudinal/per-share format but replace industrial cash/debt/ROIC mechanics with relevant funding, credit/underwriting, ROE/ROA and regulatory-capital metrics. Negative common equity or operating capital can make P/B, ROE or ROIC economically uninterpretable; state that instead of turning a mechanical ratio into a verdict.

### Growth Rates And Recent Periods

The growth-rate panel has rows for **per-share revenue, cash proxy, EPS, declared dividends and book value**, and columns for past ten years, past five years and conditional future 3–5 years. State exact endpoints; CAGR = `(end/start)^(1/elapsed years) − 1` only with comparable positive endpoints. Zeros/sign changes are `无有意义CAGR`; a short listing history is not a fabricated ten-year series. Label a simple endpoint CAGR as this report's calculation, not a claim to replicate the vendor's smoothing method.

The recent-period panel separates reported values, comparable prior periods and estimates. Revenue/EPS follow the issuer's fiscal cadence; dividends **paid** follow their actual payment dates. Do not merge calendar paid dividends with the fiscal declared-dividend row. TTM additive flows can use `latest FY + current YTD − matching prior YTD`; EPS and ratios require rebuilding from their proper numerators and denominators.

## Definitions That Must Not Be Substituted

| Field | Reproducible treatment |
|---|---|
| Value Line-style cash proxy/share | `(net profit + D&A/depletion − preferred dividends)/year-end common shares` on the stated scope; if profit already belongs to common holders, do not subtract preferred dividends again. This earnings-plus-noncash proxy is **neither CFO nor FCF**. Label scope differences and do not automatically add SBC. |
| Diluted EPS | Common-attributable profit / weighted-average diluted common shares; prefer filed EPS with its reconciliation. Distinguish this count from current and year-end shares, and preserve split/ADS adjustments. |
| Other per-share rows | Revenue, the cash proxy and cash capex divided by disclosed year-end common shares for this reconstruction; common book equity/year-end common shares. Prefer issuer-declared DPS over a reconstruction; if reconstructed from aggregate common declarations, disclose the denominator and any intra-year share-count limitation. |
| Operating margin | The cited Value Line guide uses an EBITDA-style margin. For a reconstruction, label `(operating EBIT + matching operating D&A)/revenue` as **VL-style EBITDA proxy**, separate from reported EBIT/revenue; total D&A with a different operating scope cannot be blindly added. Financial-sector definitions differ. |
| Value Line total-capital return versus ROIC | Do not rename a vendor return on total capital as ROIC. If its actual formula/input scope is unavailable, preserve the sourced value with that limitation or mark `VL口径未核验`; do not invent its tax, interest or averaging adjustments. Independently deliver `ROIC = operating EBIT × (1 − supported operating tax rate)/average operating invested capital` and its capital bridge under [capital-return measurement](business-quality.md#measure-roic-and-new-investment-returns). |
| Equity and retention ratios | State period-end versus average equity and common versus total equity. For a transparent end-common-equity reconstruction: ROE = common profit/end common equity; retention/equity = `(common profit − common declared dividends)/end common equity`. Label these, and show the analytical average-common-equity ROE separately when needed. All-dividend payout = `(common + preferred declared dividends)/matching profit before preferred distributions`; never deduct preferred payouts twice. |
| Average annual P/E and relative P/E | Average price during the fiscal year / matching annual EPS, with average-price sampling and EPS adjustments stated. Relative annual P/E divides by the named benchmark's comparable annual P/E; a self-chosen index is not the unavailable Value Line universe. Current price/EPS is a separate header measure. |
| Dividend yields | Historical average annual yield = annual common DPS / corresponding average annual price under the declared/paid basis used. Current yield requires a dated, explicitly trailing or indicated annual DPS. A special dividend is not automatically recurring. |
| FCF and economic owner cash | `CFO − cash capex` is a labeled FCF proxy. Show CFO, capex and the subtraction, then reconcile leases, maintenance/growth needs, SBC, financing and minority claims before calling it sustainable owner cash. Do not use the Value Line cash proxy as this figure. |

Each material derived metric needs **formula → substituted sourced inputs with units/period/basis → result → implication/limit**. Keep formulas once for a comparable series and retain the inputs for each result. ROIC must show EBIT → operating tax → NOPAT and opening/closing invested capital → average; missing project-level returns do not erase a reconstructible group return. Unavailable tax/capital inputs produce an explicit gap or supported conditional range, not an invented point estimate.

The historical price/cash-proxy curve in a Value Line page uses an analyst-chosen multiple; it is not independent evidence of intrinsic value. Likewise, a historical average P/E is context, not a valuation rule. Future projections must come from the business mechanism and capital model, not from fitting a chart or copying a historical multiple.

## Verified Format Sources

Checked against public official guides on **2026-11-04**, including rendered sample pages:

- [2024 Investment Survey Product Guide](https://investor.valueline.com/hubfs/Guides/1502514_Product_Guide_VLIS_WEB.pdf), Home Depot sample, printed p.16 / PDF p.18: quote header, price context, annual array, side panels and projections.
- [How to Read a Value Line Report (2017)](https://investor.valueline.com/hubfs/Guides/1503516_Reading_VL_Report_WEB_2.7.17.pdf), definitions printed pp.6–10 and Disney sample printed p.11 / PDF p.13: per-share rows, cash proxy, margins, capital and growth panels. Layout and certain quote definitions differ across vintages and industries; do not treat an old sample's forecasts or convention as current company data.
- [Official institutional investment education](https://www.valuelinepro.com/education) and [Small & Mid-Cap Product Guide](https://investor.valueline.com/hubfs/Guides/1506508_Product_Guide_SMC_WEB.pdf): financial definitions and sector variation. A public guide establishes a format/definition, not present issuer financial inputs or vendor ratings.
