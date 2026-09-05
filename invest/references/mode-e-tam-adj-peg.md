# Mode E — TAM-Adjusted PEG

Use only when the user explicitly requests TAM-Adj-PEG, TAM-supported valuation, runway-adjusted PEG, or a quality-adjusted growth valuation. Do not trigger from a bare ticker.

## Formula And Units

```text
Adjusted Growth = EPS CAGR x TAM Runway Factor x Quality Factor
TAM-Adj-PEG = Forward PE / Adjusted Growth
```

Use EPS CAGR as a percentage number: Forward PE 40 and adjusted growth 50% produce 0.8. Do not add TAM CAGR to EPS CAGR. TAM mainly modifies duration and confidence, and each factor must add information not already embedded in the EPS forecast.

If PE or EPS CAGR is not meaningful, mark the method inapplicable and use normalized earnings, EV/revenue, milestone scenarios, or an option-style framework.

## TAM Runway Factor

Use `sqrt(high-growth duration / 5)` as a starting heuristic, capped at 2.0, then explain the evidence for duration.

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

| Factor | Evidence state |
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

| TAM-Adj-PEG | View |
|---:|---|
| <0.5 | apparently very cheap; audit forecast optimism |
| 0.5–0.8 | attractive |
| 0.8–1.2 | reasonable to slightly cheap |
| 1.2–1.8 | reasonable to slightly expensive |
| 1.8–2.5 | expensive absent exceptional runway |
| >2.5 | very expensive or distorted inputs |

Report Low/Base/High factor combinations. If a small plausible change in runway or quality crosses more than one band, label the conclusion `model-sensitive` and avoid a strong point estimate. Do not double-count moat, margins, cyclicality, or TAM already present in consensus EPS.

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
## Valuation Band And Model Sensitivity
## Upside Requirements, Risks, And Milestones
## Conditional Position Type
## Sources And Missing Inputs
```
