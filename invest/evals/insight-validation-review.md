# Insight validation: add coverage, not another standing rule

Date: 2026-11-10. Source idea: [the supplied Xiaohongshu note](https://www.xiaohongshu.com/explore/6af0266d0000000003023611). The article motivates a question; it is not evidence that an instruction change improves agent behavior.

## Decision

Retain the current Skill instructions. Add the two-case [development supplement](insight-validation-cases.jsonl), its protocol routing and numeric fixture checks. No new required report section, intuition score, talent label, journal, cross-Skill dependency or forced contrarian claim.

The question was whether existing evidence discipline prematurely rejects vague observations, invents their causal explanation, or mistakes a useful connection for a priced investment edge. Current instructions already distinguish these claims. A visible development smoke check found no material failure requiring a new rule; this is coverage evidence, not an improvement claim.

## Execution and baseline

- Baseline is the actual working instructions, including existing uncommitted one-page-report changes, not Git HEAD alone. Starting HEAD: `8028b23a08ba1f197f92bf5c0fa57d818a0deb71`.
- Froze the two new prompts, semantic criteria and numeric checks before execution; reused the existing `depth-priced-good-news` control without changing its prompt or criteria. New packet SHA-256: `db9a6a01c05d37e1151dda44169644553089e8975e5407efa34e7e0a18ec2ebf`.
- Three fresh-context executors each received only one ID/prompt, the current `invest` entry and conditionally routed references. They did not inherit the article, proposed findings, expected answers, test files or rubric. Parent model/effort were inherited without overrides; exact backend identity and token/cost telemetry were unavailable.
- Local fictional materials and arithmetic only. Each executor reported its instruction reads and no network/external writes. These action reports are not independently captured tool-level telemetry.
- No instruction candidate or A/B uplift comparison was run. Entry and the five initially fingerprinted operating/scenario/discovery/reconciliation references retained their initial hashes.

## Semantic review against frozen criteria

| Case | Observed response | Review |
|---|---|---|
| `insight-vague-collection-clue` | Reconstructed original-business revenue 110, growth 10%, receivables 30 and growth 50%; retained cash-quality concern without asserting fraud. Prioritized invoice-level post-period collection against old/new due dates and did not attribute all consolidated cash deterioration to the original business. | All 5 criteria met. The answer also correctly distinguished receivables/revenue from DSO and a year-on-year balance change from a quarterly cash-flow movement. |
| `insight-same-capex-different-funding` | A funding balance -30; B 0 after counting the extra customer prepayment once. Limited the finding to annual funding coverage, named no cash buffer and future delivery obligations, and declined an investment-quality inference. | All 5 criteria met. Intra-year ordering was excluded by the task; the answer did not claim intra-year solvency or guaranteed forecast cash receipts. |
| Existing `depth-priced-good-news` | Distinguished positive guidance from an incremental expectation/valuation gap, treated repeated media reports as one originating observation, and gave evidence that could change the no-new-edge conclusion. | All 4 criteria met. It did not force alpha, a probability revision or a purchase. |

The parent reviewed meanings and independently recomputed the numerical relationships; matching phrases/headings was not the grader. The three outputs support this scoped check, not an assertion that all future vague clues will be handled correctly.

## Verification and limits

- Fixture baseline before the supplement: **12 passed, 102 subtests passed**.
- Expanded diligence fixture suite: **14 passed, 111 subtests passed**; covers packet integrity and arithmetic, not agent judgment.
- Whole `invest/tests` suite: **110 passed, 373 subtests passed**.
- `quick_validate.py invest` passed. Scoped diff checks passed.
- Frozen protocol, prompt-only inputs and readable final-answer captures are retained locally at `/data/tmp/invest-intuition-Q0f0v6/`; original replies are the `insight_clue_check`, `insight_funding_check` and `insight_pricing_control` task messages in this session. This temporary evidence path is not a published or versioned artifact store.

These are visible development cases, not sealed holdouts or repeated reliability estimates. The parent authored the cases and graded the independent answers; no independent blind grader was used. Real-company retrieval, calibrated forecasts, long-run advantage, learning effects and investment returns were not tested. The existing priced-news case is a regression control, not newly discovered coverage. Only a reproducible failure on further comparable tasks should motivate a narrow instruction correction.

No commit, push, deployment, trading or Notion mutation was performed for this change.
