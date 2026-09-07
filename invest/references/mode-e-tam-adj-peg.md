# Mode E — TAM-Adjusted PEG

Use when explicitly requested for TAM-Adj-PEG, TAM-supported valuation, runway-adjusted PEG, or a quality-adjusted growth valuation, or for a clearly stated Mode A crux requiring this lens. Do not trigger from a bare ticker.

This is an **uncalibrated screening heuristic**, not a fair-value model or a standalone trade signal. Its factors and legacy bands have no demonstrated out-of-sample calibration here. Report that status with any calculation; a lower adjusted PEG alone does not establish cheapness.

## Formula And Units

```text
Adjusted Growth = EPS CAGR x TAM Runway Factor x Quality Factor
TAM-Adj-PEG = Forward PE / Adjusted Growth
```

Use EPS CAGR as a percentage number: Forward PE 40 and adjusted growth 50% produce 0.8. Show ordinary PEG alongside the adjusted result, with the factor inputs and their provenance. “Adjusted Growth” is an index denominator, not a forecast EPS growth rate. Do not add TAM CAGR to EPS CAGR. TAM mainly modifies duration and confidence, and each factor must add information not already embedded in the EPS forecast.

If PE or EPS CAGR is not meaningful, mark the method inapplicable and use normalized earnings, EV/revenue, milestone scenarios, or an option-style framework.

## TAM Runway Factor

When a supported duration estimate is available, `sqrt(high-growth duration / 5)`, capped at 2.0, is an optional heuristic. Declare the formula or user-supplied convention used and retain precision until final rounding; the table below is approximate. If duration is unsupported, leave the factor and adjusted result `N/A`, or calculate an explicitly hypothetical sensitivity rather than filling a default.

| Duration | Factor |
|---:|---:|
| 2 years | 0.6 |
| 3 years | 0.75 |
| 5 years | 1.0 |
| 8 years | 1.25 |
| 10 years | 1.4 |
| 15 years | 1.7 |
| 20+ years | 2.0 cap |

Do not assign runway from a sector label. Test penetration, TAM growth, share durability, capacity, competition, substitution, technology iterations, requalification, and whether frontier AI shifts the profit pool.

## Quality Factor

These legacy ranges are illustrative parameter choices, not calibrated mappings from business quality to value. Prefer an explicit user-supplied factor or a disclosed sensitivity; unsupported quality factors leave the adjusted result `N/A`.

| Illustrative factor | Assumed evidence state |
|---:|---|
| 0.3–0.5 | early, loss-making, unproven, or high dilution |
| 0.5–0.7 | cyclical, concentrated, or high execution risk |
| 0.7–0.9 | high growth with unstable margins/competition |
| 0.9–1.1 | ordinary high-quality growth |
| 1.1–1.3 | moat, pricing power, sticky customers |
| 1.3–1.5 | platform/ecosystem or monopoly-like asset |
| >1.5 | rare bottleneck/super-platform; use cautiously |

Evaluate accrual of TAM to the company, pricing power, customer concentration, technology/requalification risk, sustainable margins, capex, second sourcing, financing/dilution, and AI substitution.

## Interpretation

Report supported or explicitly hypothetical Low/Base/High factor combinations. If a plausible parameter change materially alters the screening result, label the conclusion `model-sensitive`; do not turn a band crossing into a buy/sell rule. An explicitly requested legacy or personal band may be reported as that convention, not as independently established fair value.

Do not double-count moat, margins, cyclicality, or TAM already present in the forecast. Explain how much of the result comes only from changing factors. For example, PE 40 / EPS growth 20 gives ordinary PEG 2; user-specified factors 1.4 and 1.4 lower it to about 1.02 without adding cash-flow evidence. Put durable advantages into margin, incremental return, reinvestment duration/fade, or scenario probabilities in a cash-flow model instead of awarding another quality premium for the same effect. If those economics cannot be checked, conclude `valuation unresolved`, not “cheap.”

Special cases:

- **Loss-making:** no direct PE/PEG; focus on milestones, normalized economics, financing, and dilution.
- **Cyclical:** use mid-cycle EPS; separate structural demand from inventory/capacity/margin cycle.
- **Turnaround:** show current/base and successful-normalization cases separately.

## Output

```markdown
# [Ticker] — TAM-Adj-PEG
## Current Valuation And Input Quality
## EPS/Revenue/TAM Growth And Penetration
## Runway Factor: Low / Base / High
## Quality Factor: Low / Base / High
## Calculation And Sensitivity
## Calibration Status, Model Sensitivity, And Cash-Flow Cross-Check
## Upside Requirements, Risks, And Milestones
## Conditional Position Type
## Sources And Missing Inputs
```
