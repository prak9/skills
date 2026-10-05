# Deepdive Adoption Record

Source: [Socialpranker/deepdive](https://github.com/Socialpranker/deepdive), revision `f05e10dc21f26d8485b73731f61ab00d45a2a075`, inspected 2026-10-05. This is an adapted research-method integration, not a vendored copy or a claim of runtime/CLI compatibility. The local validator is independently implemented with the Python standard library.

## What Changed

The entry point now routes substantial source research to a complete report, memo and evidence package. Controlled experiments retain their original discipline in `references/controlled-research.md` and the existing specialist references. Reading a topic no longer requires an artificial experiment, performance metric or decision to execute.

| Upstream capability | Local implementation / deliberate adaptation |
|---|---|
| Existing-research discovery and reframing | `deep-research.md`: recover scope, reader, period, outcome, prior work and consequential unknowns before collection |
| Decision specification | Preserve action forks when requested; understanding-only questions remain legitimate deep research; actual decisions use `decision` |
| Genres and block composition | `research-reporting.md`: retain qa/explainer/decision/landscape/validation/custom; add a comparison genre without forcing a decision; preserve ten functional block families |
| Research planning and dependency routing | Existing dependency-aware questions, readiness and isolated ownership; the lightest persistent plan when needed, no mandatory 17-section plan |
| Capability discovery | `source-discovery.md`: inspect available tools and relevant providers; no credential enumeration or printing environment variables |
| Source dispatch, channels and structured APIs | Question-to-source matrix, original records, original language, opposition and citation chains; choose live relevant providers rather than copying the entire endpoint catalog |
| Fetch ladder | Inspect actual content; use permitted direct/API/browser/archive alternatives; partial access stays partial, no bypassing access controls |
| Parallel search and compact returns | Distinct discovery axes, isolated source IDs/files, compact evidence returns, one merge owner; only when delegation is permitted and useful |
| Model routing and costs | Use the available authorized model; report actual limits/costs when known; no hard-coded Claude models or invented budgets |
| Round state and search stopping | Known/Gaps/Next working window, targeted gap repair, retire unproductive branches without dropping unresolved questions or independent work |
| Source scoring and triangulation | Claim-specific relevance/authority/freshness/origins instead of an additive truth score or fixed minimum counts; a narrow official fact may have one adequate source |
| Minority protection | Preserve contradictory evidence through ledger, outline, report and memo; majority/reprints cannot erase a decisive minority |
| Evidence filter | `evidence-contract.md`: explicit claim/source/passage links, context separate from support, qualified/limited/unknown authority |
| Pre-synthesis cross-run reconciliation | `research-updates.md`: compare scope/units/period first; retain agreement/conflict/different-claim/unknown, not newer-is-true |
| Section-wise synthesis | Outline → selected claims → relevant evidence → section → report → memo; no concatenated worker reports |
| Numbers and figures | Register material numbers, source IDs, units, vintages, inputs and formulas; recompute arithmetic, inspect denominators and source-linked figures |
| Adversarial review | Five lenses: support, rival, gap, usability and dissent; proportionate checks, honest self-review labeling, recheck fixes |
| Runtime verification axes | Access, authority/support, qualifiers, construct provenance, numbers and coverage; hashed inputs make stale review records detectable |
| Report/memo delivery | Full genre-specific report plus concise entry memo and chat conclusion; substantive output is not replaced by a file-completion message |
| HTML/PDF/DOCX export | Conditional on requested/project deliverables, using available tools; no automatic renderer/dependency installation |
| Refresh targets and atomic findings | Concrete change triggers and reusable bounded findings when useful; dated deltas preserve the prior research |
| Cross-run wiki | Reuse an authorized project knowledge system; no default global home-directory writes or permanent maximum credibility scores |
| Swarm/channel learning | Retain successful and failed discovery observations in authorized recurring work; no automatic catalog/Skill promotion or background schedules |
| Decision walkthrough/application ledger | Only when requested; no forced choice, fabricated user decision or automatic external application ledger |
| Finish gates | Read-only integrity checker plus actual semantic review; disclose partial results rather than hiding them behind a failed gate |

## Output Compatibility

The substantive report contract is adopted; the storage/API format is intentionally local. For the optional full audit package, upstream `outline.md` becomes `outline.csv`, `evidence/CN.md` relationships become `evidence.csv` plus source cards, and `refresh_targets.md` becomes `refresh.md`. Native `research.json` tracks original-question coverage. A single `.verify/review.json` stores individually identified checks and input fingerprints rather than multiple producer-specific receipts.

Existing equivalent project artifacts remain valid with equivalent checks. Lean report plus memo is now the default for standard/deep research; locators, derivations and meaningful checks can live in the report appendix. A full audit package needs an explicit or concrete project/handoff rationale. Brief/chat-only work does not require a persisted package. Exports, cross-run findings and application records are conditional. Upstream helper commands are not installed or claimed to work here.

## Verification And Limits

Recorded local checks on 2026-10-05: `python3 -m unittest discover -s tests` passed 110 tests (21 native-package tests); the synthetic package checker passed with its two disclosed evidence limitations; 46 actual local reference links across 18 research instruction documents resolved; `git diff --check` passed. These are implementation/contract checks, not a measured research-quality comparison.

- `tests/test_research_package.py` exercises the native contract with a clearly synthetic report and adversarial mutations: false arithmetic, executable formulas, dropped dissent, inappropriate confidence, unknown references, missing review axes, changed inputs, path escape and fake quotations. It also tests honest no-source conclusions and read-only CLI exit behavior.
- `tests/test_skill_contracts.py` protects existing routing, experiment and harness boundaries. Run the repository test suite as regression evidence.
- `evals/report-delivery-cases.md` defines semantic acceptance scenarios. They are not scored model runs; static inspection and deterministic tests do not prove better real-world research.
- `evals/report-package/` is a complete small validation-genre artifact example, not a substantive external investigation or an independent reviewer evaluation.
- Repository entry points and relevant mechanisms were examined. The large upstream provider catalog, every endpoint and its full automation stack were not exhaustively tested. No claim is made of feature parity, live provider availability, measured model gains or an independently certified fact checker.

## Upstream Notice

Retained for the adapted workflow and documentation concepts. This does not change other repository files' licenses.

MIT License

Copyright (c) 2026 ivanterescheenko-ai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
