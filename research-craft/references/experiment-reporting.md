# Reproducible Experiment Results

Use for substantive baseline/candidate comparisons, not every explanation, successful test or research proposal. Reuse the project's existing result format and authorized storage; do not create a competing ledger. The [report template](../assets/experiment-report.md) is optional scaffolding, not a required set of headings. Missing evidence limits the claim, not unrelated useful work.

## Preserve the comparison

Record the question, hypothesis, baseline identity and reason for its selection, arm/run IDs, code version (including a patch or fingerprint for relevant uncommitted changes), data/version and split, evaluator version, commands, and artifact locations. Distinguish measured results from proposed, estimated or reconstructed values.

Show each arm's configuration differences in the report; retain resolved effective configurations, including material defaults, in machine-readable artifacts. Link shared fixed settings instead of repeating them. Record actual tuning budgets, seeds/repeats and failed attempts where relevant. A different dataset, evaluator, cost model or budget limits comparability; label it rather than calling the result a controlled improvement.

## Detailed supporting tables are part of the result

A headline table or screenshot is not the underlying evidence. Retain readable, machine-readable tables (existing CSV, Parquet, JSONL or workbook formats are fine) at the granularity needed to reproduce the reported metrics and investigate the important heterogeneity:

- **Run/config index:** arm and run IDs, baseline link, effective configuration or path, data/split/evaluator identities, execution status and raw artifact paths. Include unsuccessful arms and missing runs; never silently drop them.
- **Observation or component table:** stable sample/task IDs or natural keys, arm/run, split and relevant time/group, prediction/outcome or metric components, inclusion/exclusion status and reason. For paired claims retain the pairing keys and unmatched counts. Reuse accessible source tables with an exact query rather than duplicating large raw datasets.
- **Metric/comparison table:** arm, metric, unit and preferred direction, cohort/split, value, denominator or weights, sample count, baseline value, absolute and valid relative deltas. Retain numerators/denominators or sufficient inputs for ratios and weighted metrics; non-additive measures need their computation/query and underlying ordered records, not sums of subgroup scores.

Provide a short data dictionary: row grain, unique keys, units, missing-value semantics, filters, aggregation/weighting rules and how tables join. Choose useful granularity, not all possible columns or Cartesian slices. Detail means auditable evidence, not a large unreadable dump. Large tables can be linked with a preview and counts; previews must not be described as complete. Do not fabricate unavailable rows, infer individual outcomes from aggregates, or export restricted data. If only aggregates are available, deliver that bottom table and explicitly state which claims cannot be reconstructed.

Check key uniqueness at the declared grain, join multiplicity, expected vs actual rows, missing/failed/excluded counts and reconciliation of the summary to the supporting tables within a stated rounding tolerance. Do not fill missing results with zero. Preserve filters and computation commands/scripts so another run can regenerate the same summary; a file hash alone does not verify its contents or the metric logic.

## Compare without hiding the tradeoff

For a metric B at baseline and C for a candidate, report the signed absolute change `C - B`. For positive, meaningfully nonzero B, relative change can be `100 * (C - B) / B`; label its direction, since lower loss may be better. For zero, negative or near-zero baselines, use absolute changes and explain why relative change is N/A or unstable, unless a justified domain convention is explicitly defined. A rate changing from 40% to 44% is +4 percentage points and +10% relative, not +4% relative.

Show primary metrics alongside relevant risk, cost, coverage and sample-size guardrails. Report uncertainty when it matters and is estimable; respect paired observations, time dependence and the actual independent unit. No made-up intervals from aggregate-only data. Keep tuning/validation outcomes separate from untouched test confirmation. Disclose search exposure and failed arms rather than presenting only the best run.

## Visualize to answer a question

Default to a compact baseline/arm comparison table. Add a plot only when it clarifies an important relationship: time stability, distributions/tails, per-group contributions, parameter sensitivity or cost-quality tradeoffs. Label axes, units, cohorts and uncertainty where applicable; retain plotting data and the generating command/script. A single scalar comparison does not need a chart. Never hide excluded groups, unmatched records or a changed denominator behind a polished plot.

## Interpret, not merely decorate

Separate what changed, where it changed, candidate mechanisms and what evidence distinguishes them. Discuss practical magnitude, robustness, costs and unresolved competing explanations. Aggregate gains may reflect composition or selection changes; post-hoc slices generate hypotheses and do not become independent validation. An accounting decomposition locates a difference but does not establish its cause.

End with accept/reject/unresolved under the existing contract, supported findings and their limits. Propose the cheapest discriminating follow-up only if it can still change the judgment; do not add mandatory experiments or approval turns. Delivery links should let the user reach the detailed tables, configurations and raw evidence, not just the polished report.
