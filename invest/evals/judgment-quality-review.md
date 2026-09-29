# Invest judgment-focused compression review

## Outcome and scope

Reviewed the entrypoint and all 17 domain references. The revision concentrates the main path on a useful question, an economic mechanism, discriminating evidence, a supported inference and its decision consequence. Novelty, contrarianism and document count are not substitutes for insight. Detailed accounting/source contracts and specialist calculators remain intact and load only when relevant.

The baseline is the pre-edit working snapshot, including earlier uncommitted allocation-comparison work, not Git HEAD alone. Starting HEAD was `a2de75a1bc869da5ea911505e88c0d2c5d474c30`. This review makes no publication or deployment claim.

## Material changes

- Replaced repeated Quick/Full report templates with request-shaped deliverables. Preserved four-period operating coverage, Full's historical and recent-three-month research, current-versus-historical evidence, financial-model reconstruction, writing handoff and external-write boundaries.
- Made omitted costs, distorted denominators, competing mechanisms and decision-changing original evidence the focus. Business-only judgments and simple arithmetic need no forced pricing dispute, target or portfolio analysis.
- Separated operating conviction, current forward payoff and allowable exposure. Appreciation does not exempt an existing position from concentration constraints; neither averaging up nor down bypasses the fresh-capital test. Research does not require a paid starter position.
- Distinguished original-thesis resolution from a new current investment case, and operating delivery from market repricing. New profits cannot erase a failed forecast; flat prices cannot excuse missed milestones or financing gaps. Different buy/hold/sell gates reflect real costs and constraints, not loyalty to winners.
- Replaced an arbitrarily conservative Bayesian prior with an evidence-grounded prior; removed illustrative quality-multiplier tables that could invite false precision. News-to-financial analysis no longer forces beneficiary tiers or valuation for a narrow cost question.
- Consolidated duplicated history, journal and monitoring instructions. Kept detailed cash/funding/dilution bridges, valuation attribution, rival tests and falsifier measurement because they protect substantive reasoning.

Independent instruction review caught two compression omissions before the candidate run: explicit Full routing for re-underwriting/model reconstruction, and the rule that a better price cannot replace missing evidence or feasibility prerequisites. Both were restored.

## Compression measurement

Whitespace-separated words, not model tokens or measured execution cost:

| Scope | Before | After | Reduction |
|---|---:|---:|---:|
| Entrypoint + Mode A | 4,880 | 2,539 | 48.0% |
| Entrypoint, Mode A, underwriting, uncertainty/exposure, thesis reconciliation | 13,880 | 10,745 | 22.6% |
| Entrypoint + all 17 references | 27,743 | 24,511 | 11.6% |

Ten domain references were deliberately unchanged; reducing their accounting or retrieval detail would not follow from this review. No runtime formula or calculator interface changed.

## Verification and evidence limits

- `python3 -m pytest -q invest/tests tests`: **145 passed, 402 subtests passed**. These validate code, contracts and fixture arithmetic, not investment judgment.
- Relative-link/heading check: **18 files, 47 links, no missing targets or anchors**. `git diff --check -- invest tests` passed.
- Frozen six-case visible development packet: `judgment-quality-cases.jsonl`. Two fresh executors answered the same prompt-only batch using old/new snapshots. The six cases within each arm shared context; this is a forward smoke comparison, not isolated holdout evidence.
- Actual answers cover conviction/payoff/concentration, hidden support-cost offsets, old versus new thesis, two clocks, negative cost transmission and simple price-return arithmetic. Arithmetic is correct in both arms. Numerical fixtures are not substituted for these actual outputs.
- Independent blind grading found **20 pass, 1 partial, 0 fail per arm**, with all eight numerical checks correct. No new material regression was observed. Both answers to the two-clocks case left current forward return/opportunity cost implicit rather than explicitly naming it as the next comparison; this is a shared minor gap, not a candidate improvement. The primary review agrees with preserving this limitation.
- Raw outputs, neutral-label grading inputs, snapshots and protocol are preserved locally in `.research/invest-judgment-moFaFR/`. X is candidate; Y is baseline. Only answer bodies, not version identity or instruction diffs, were sent to the independent grader. Tool/read appendices are executor reports, not independently captured cost telemetry.
- Backend model identity, tokens and monetary cost are unknown; no speed/cost improvement is claimed. Live source retrieval, real-company insight, full-report writing fidelity, calibrated probabilities and investment returns were not tested by this smoke comparison.

Snapshot identity is SHA-256 of the JSON-serialized, path-sorted `[relative_path, UTF-8 contents]` pairs for `SKILL.md` and all reference Markdown files:

- Baseline: `5a5dabc202e2db7072d22bd2997dd8cfcc6925fd4a911e60b1d661e63803cb59`.
- Candidate: `f56b0771d0440dd55e7a7a3d8b5bf442402c593a2c0ae26c90bc02fafd7512d0`.
- Frozen case file SHA-256: `e0a4c7c35aa37eb829e9d21f80ff837b46f34875e6e892d831f352d52571ca9b`.

Retained the simpler candidate: the scoped no-new-material-regression gate passed, while the common partial remains documented in `grades.md`. No extra rule was added merely to fit that visible case; current instructions already require forward payoff and opportunity-cost comparisons when relevant. Unchanged successes support preservation, not a claim of generalized capability improvement. Fresh isolated tasks and real-company evidence retrieval would be needed for stronger conclusions.
