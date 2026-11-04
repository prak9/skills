# Skill simplification — 2026-11-04

## Scope and decision

Accept a scoped simplification of the repository-owned entries. Remove generic
workflow wrappers; retain user requirements, specialist methods, tool contracts,
permissions and executable evidence. No model-performance uplift is claimed.
The initial simplification was local only. A follow-up request authorizes
repairing the failing cases and committing/pushing these scoped changes;
deployment remains outside scope.
Existing system-directory changes and the external alpha-research symlink were
not modified.

- Retire the independent iterate and eli5 entries and their UI metadata.
  Ordinary autonomous work follows project/domain rules; special explanation and
  learning guidance is optional under writing. Preserve evaluation assets.
- Narrow research-craft to experimental design, ablation, prediction validity,
  instruction/model migration and related specialist methods. Generic research
  no longer inherits its report/memo/package workflow. Existing method paths,
  scripts and historical packages remain available.
- Simplify invest's entry and buy-side reference. Preserve business/earnings
  reconstruction, financial architecture, strong countercases, evidence checks,
  causal sandbox before final probabilities/verdict, scenario valuation,
  signals/six-month catalysts, one-year risk-neutral options analysis gates and
  company-hub Notion organization. Writing remains its only cross-Skill
  dependency. C/E scoring heuristics are explicit-request only; broad competition,
  growth-runway and price/fundamental analysis remain in the default research.
- Prefer Inline/Lite planning. Stop creating cleanup metadata for ordinary Lite
  plans; preserve existing opted-in Clean validation and Full/Loop contracts.
- Condense writing and final revision guidance. Preserve semantic fidelity,
  edit levels, natural paragraphs, concrete causal explanation, author voice and
  whole-document review; detailed tutorials are conditional.
- Add one project-level rule family for best-verified-result preservation,
  evaluator repair and distinguishing completion from search termination.

Tools/platform-specific skills were reviewed without parallel rewrites: source
identity, OCR/media completeness, login/publish boundaries, performance
measurement and project trading-data semantics are not generic model workarounds.

## Text footprint, not runtime telemetry

Measured UTF-8 bytes relative to 3ffb4089468f346f7155dcc797229bded90c2099:

| File | Before | After | Reduction |
|---|---:|---:|---:|
| invest/SKILL.md | 20,936 | 12,432 | 40.6% |
| invest/references/mode-a-buy-side.md | 21,175 | 9,159 | 56.7% |
| plan-skill/SKILL.md | 10,924 | 6,716 | 38.5% |
| research-craft/SKILL.md | 9,075 | 4,813 | 47.0% |
| writing/SKILL.md | 7,386 | 4,832 | 34.6% |
| writing/references/revision-checklist.md | 15,958 | 5,222 | 67.3% |
| Selected files total | 85,454 | 43,174 | 49.5% |

These are selected instruction-file sizes, not total repository savings, tokens,
latency or cost. Archived instructions and new evidence are intentionally not
counted as active instructions. Loaded context depends on the actual request.

## Verification

Four revised entries passed quick_validate.py. Scoped git diff --check passed.
Structural guards check retirement/discovery, preserved method paths, the
single invest-to-writing link, conditional heuristic routes and Lite metadata.

The old iterate executor depended on its live entry. Its preparer now uses a
versioned archived instruction, with source/revision in the manifest. Its SHA256
is unchanged from the original:
c860e28c9e9339c6a6c74ddc6f096ccb7909de648d8e23a34448b2c3ccd08518.
Historical case packets and graders were not rewritten. Their replay is not a
test of the new active workflow. Test-harness counts were reconciled with the
already expanded 40-case core/48-case combined packet, and repository-local
metadata tests exclude externally owned linked bundles.

Command:

```sh
python3 -m pytest -q tests invest/tests decision/tests plan-skill/tests writing/tests watch/tests read-link/tests read-xiaohongshu/tests result-analysis/tests wechat-article-design/tests iterate/tests
```

Initial result: **457 passed, 2 failed, 645 subtests passed**. Both remaining failures
were present before editing, in test_learning_transfer_fixtures.py:
the initial and archived plan omit the subsequently required Contract status.
Historical raw artifacts and the current confirmation gate were left intact;
that initial repository-wide result was not all green.

Follow-up fixture repair: replay copies now explicitly confirm the already
recorded contract only after checking that Outcome and Acceptance match the
frozen fixture. The raw unconfirmed plan is still rejected; neither the live
validator nor its confirmation gate was relaxed. Historical inputs, prompts and
observed artifacts remain byte-identical. The fixture and plan-validator tests
passed together (88 tests, 44 subtests).
The same full command above then passed: **459 tests and 645 subtests**, with no
remaining failures.

## Forward checks and limits

[Actual four-request outputs](skill-simplification-forward-2026-11.md) cover an
ordinary explanation, minimal code diff, migration experiment design and a
bounded hypothetical investment analysis. The parent separately recomputed
the investment values: 16.50, 10.20 and 5.70; any legitimate probability mixture
is at most 16.50 under those stated assumptions. No probabilities or market data
were invented.

A separate fresh-context recovery probe used only a local Lite plan, source
CSV, export artifact and request receipt. The receipt recorded EXPORT-001 as
succeeded while the plan still showed its node in progress. The agent verified
the three IDs/names, found one receipt and one artifact, reused the existing
effect, and marked the plan complete without creating cleanup metadata. The
parent read back the plan, reran strict validation (PASS), and checked unchanged
source/artifact/request hashes. Details are appended to the forward record.

These are visible development probes, not untouched holdouts or an old/new
paired comparison. The four requests share one agent context; recovery used a
separate context without prior chat. No live publication, tool-failure network
simulation, real company research, model-quality comparison or cost experiment
was performed. Exact backend identity, tokens and billing are unavailable.
Passing these checks supports the bounded change; it does not demonstrate that
shorter instructions universally preserve quality or improve efficiency.
