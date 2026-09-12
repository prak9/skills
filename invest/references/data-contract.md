# Material Investment Data Contract

Use this contract when linked calculations depend on three or more material numbers, when rebuilding a model, or when reconstructing a historical decision. A Quick memo may show the same fields in a compact table; do not force a JSON artifact when no calculation depends on it.

The contract prevents unknown values from becoming zero, estimates from becoming facts, incompatible bases from being added, and later information from leaking into a historical view. It does not prove that a source supports a number; compare every material claim with the cited original passage.

Maintain two different checks: **input integrity** (this schema and calculator) and **underwriting support** (why a premise/range is justified and whether it supports the inference). For a load-bearing analyst assumption, retain its derivation, supporting observations/reference class, range and failure condition in the model or memo. `source.reference` pointing to that model is not independent support for its growth or margin. A validator pass, a large metric count or reproducible DCF cannot be presented as proof of investment depth or forecast reliability. These semantic checks do not add required JSON fields or change the v1 schema.

## Metric record

Each material number is one item in `metrics`:

```json
{
  "id": "revenue_fy2025",
  "name": "Revenue",
  "value": 1250.0,
  "unit": "USD million",
  "currency": "USD",
  "period": "FY2025 ended 2025-12-31",
  "basis": "GAAP; continuing operations",
  "classification": "reported_fact",
  "source": {
    "reference": "https://example.com/10-k",
    "document_type": "10-K",
    "published_at": "2026-02-20T13:00:00Z",
    "available_at": "2026-02-20T13:02:00Z",
    "locator": "p. 42"
  },
  "missing_reason": null
}
```

Required semantics:

- `value` is a finite number or `null`. Zero is a measured value; unknown is `null` plus a non-empty `missing_reason`.
- `unit`, `currency`, `period`, and `basis` make the accounting and temporal basis explicit. `currency` may be explicit `null` for ratios, counts, or probabilities.
- `classification` is exactly one of `reported_fact`, `management_guidance`, `consensus`, or `analyst_assumption`. Do not disguise a forecast as a filing fact.
- `source.reference` identifies the original document or a clearly named analyst-model artifact. Record `document_type`, exact publication and availability timestamps with time zones, and a page/section `locator` when available; use explicit `null` when no stable locator exists.
- `available_at` is the first time the decision-maker could actually have used the item, which may be later than the document's nominal `published_at`.

## File and checks

```json
{
  "schema_version": 1,
  "as_of": "2026-09-05T10:00:00+08:00",
  "decision_time": "2026-09-05T10:00:00+08:00",
  "metrics": [],
  "checks": {
    "sums": [
      {"name": "segments to revenue", "components": ["segment_a", "segment_b"], "total": "revenue", "tolerance": 0.001}
    ],
    "growth_rates": [
      {"name": "revenue growth", "prior": "revenue_prior", "current": "revenue", "expected": 0.25, "tolerance": 0.001}
    ],
    "probability_groups": [
      {"name": "scenario probabilities", "items": ["bull_p", "base_p", "bear_p"], "target": 1.0, "tolerance": 0.001}
    ],
    "basis_groups": [
      {"name": "margin inputs", "items": ["gross_profit", "revenue"], "fields": ["unit", "currency", "period", "basis"]}
    ]
  }
}
```

- `decision_time` activates point-in-time validation. Any `available_at` later than it is a failure and cannot be backfilled into the historical judgment.
- Sum checks require the same unit, currency, period, and basis before arithmetic.
- Growth checks require the same unit, currency, and basis, a non-zero prior value, and a decimal expected growth rate.
- Probability values must each lie in `[0, 1]` and sum to the configured target.
- Basis groups explicitly require selected fields—unit, currency, period, basis, or classification—to match before linked calculations use them.

Run:

```bash
python scripts/validate_invest_data.py path/to/data-contract.json
```

For compatibility, exit code `0` means that a JSON report was produced, even when its `status` is `fail`. Automation must parse the JSON and require `status == "pass"`; checking the process exit code alone does not validate the data. File/JSON loading errors still exit nonzero.

Treat every finding as a model-input issue to resolve or expose. The validator's two explicit limits remain in force: timestamps only validate the recorded evidence set, and arithmetic consistency cannot establish source support, economic comparability, or forecast quality.
