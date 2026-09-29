# Judgment-focused skill streamlining

## Scope and acceptance

Applied the approved cross-skill audit: remove unsupported action mappings and contradictory workflow assumptions, reduce mandatory generic procedure, and route specialist detail only when needed. Preserve evidence, authorization, compatibility, recovery and domain-specific constraints. This change also includes the previously verified [invest revision](../invest/evals/judgment-quality-review.md).

Updated `code-review-craft`, `decision`, `eli5`, `invest`, `performance`, `plan-skill`, `read-link`, `research-craft`, `watch`, `web-design` and `writing`. Reviewed but left `iterate`, `result-analysis`, `read-xiaohongshu` and `wechat-article-design` unchanged: their essential completion, measurement and platform contracts did not need a parallel rewrite. System-owned directories and unrelated local state are excluded. No deployment or native-goal change is part of this task.

The baseline for this round is a working snapshot taken before edits at Git HEAD `a2de75a1bc869da5ea911505e88c0d2c5d474c30`; it already contains the earlier invest changes. Compression is not evidence of improved model capability, latency or research returns.

## Material corrections

- `decision`: complete scores support comparison under supplied criteria/weights, not fixed action or commitment bands. JSON keys/types, veto precedence, unknown values and ranking remain compatible. Consumers that treated the old recommendation text as an action command must adopt the new comparison semantics.
- `plan-skill`: Lite/Full Linear can explicitly record `None` when no reflection trigger fired; empty/Pending does not pass. Loop still requires substantive evidence-linked reflections. Explicit `N/A` records a completed no-op Clean check; Not run remains unfinished. Legacy reason-bearing records and Lite-to-Full migration remain supported.
- `watch`: captions-only success need not produce video. Follow-up frames use verified existing video or retrieve pixels from the original URL, preserving captions/provenance in a separate output directory and disabling unnecessary ASR. Local-video reruns do not inherit captions automatically.
- `performance`: annotation and further collection depend on diagnostic value. Unsupported Intel PMU events on other CPUs are instrumentation gaps, not failed optimization. Percentages/IPC are clues rather than portable causal diagnoses; keep comparable workloads, correctness and matching build/profile evidence.
- `research-craft`: failed routes or evaluators do not automatically terminate a still-achievable authorized goal. Keep discovery flexible and comparative claims controlled; move team organization and human-learning evaluation out of the ordinary path.
- `code-review-craft`: focus the common path on reconstructed behavior, supported findings and calibrated verdicts; route collaboration and judgment training conditionally. A green internal test does not prove a public workflow, and proven structural regressions can still block.
- `writing`, `web-design`, `eli5`: remove universal argument, layout-alternative, one-defect-per-round and explanation templates. Preserve source fidelity, actual render/interaction evidence, audience knowledge and scoped authority. Long fiction does not need a factual central thesis.
- `read-link`: move X-specific retrieval mechanics to an on-demand reference without weakening completeness, third-party, media or archive boundaries.

## Entrypoint size

UTF-8 bytes, not tokenizer counts, total reading cost or measured execution time. Several technical details moved to conditional references rather than being deleted.

| Entrypoint | Before | After | Reduction |
|---|---:|---:|---:|
| research-craft | 28,627 | 14,520 | 49.3% |
| code-review-craft | 16,036 | 8,596 | 46.4% |
| writing | 14,270 | 10,504 | 26.4% |
| eli5 | 8,729 | 6,216 | 28.8% |
| watch | 21,170 | 6,820 | 67.8% |
| read-link | 6,849 | 3,718 | 45.7% |
| performance | 6,252 | 6,039 | 3.4% |

For a routine full-page web-design task, the verification-foundation adapter is no longer mandatory: the audited common route drops from 367 to 272 lines while actual render/interaction checks remain in the entrypoint. Formal comparisons and design-rule promotion still load the adapter. These route counts are instruction-structure observations, not observed cost savings.

## Verification record

Updated decision/plan tests run against the old runtime reproduced seven failures/subfailures: action mapping in both schemas, no-reason reflection in Lite and Full Linear, no-op Clean, completed Lite migration and spurious migration reflection. Other relevant old-runtime tests passed (102 tests and 43 subtests). Updated runtime passes these regressions. The caption-follow-up test exercises both sequential acquisition branches with mocked media/ASR boundaries; it is not live retrieval validation.

An independent runtime reviewer ran decision and plan suites and compared 74 v1/v2 input combinations against HEAD: only the intended recommendation strings differed. Its explicit marker matrix accepted Linear `None` but rejected it for Loop, accepted legacy and new Clean no-op forms, and rejected empty/Pending/Not run. No blocking runtime finding was reported.

Final integrated command:

```bash
python3 -m pytest -q tests invest/tests decision/tests plan-skill/tests writing/tests watch/tests read-link/tests read-xiaohongshu/tests result-analysis/tests wechat-article-design/tests iterate/tests
```

Result: **418 passed, 568 subtests passed** in 40.69 seconds. Repository diff whitespace checks passed. A check of the changed instruction/report Markdown found 88 relative links/anchors across 46 files with no missing targets; the subsequently added report links were checked separately. These are artifact/contract checks, not model capability tests.

An independent full-text comparison of old/new research and code-review instructions found no blocking loss of evidence, acceptance, abstraction or authorization boundaries. The human-learning adapter retained the assisted-versus-independent distinction. This is a static semantic review, separate from forward execution.

## Forward smoke and limits

The frozen visible [seven-case packet](skill-streamlining-cases.jsonl) is separate from the existing core/holdout suites and is not loaded by `evaluate_behavior_cases.py`. Two fresh executors answered the same prompt-only batch from old/new instruction snapshots without grading criteria; cases within each arm shared context. A third fresh agent graded neutral X/Y answer bodies criterion by criterion, with only workspace paths normalized in grading input. Full responses, executor-reported read lists, fingerprints, settings limits and grading are retained in [observed results](skill-streamlining-observed.json).

Both arms passed all **21 criteria**, with **0 partial and 0 failures**. No material regression was observed in route continuation, lightweight exploration, review evidence, fiction fidelity, proportionate UI checking, caption-to-frame recovery or unsupported PMU handling. Both versions already handled these cases well; the results support scoped preservation, not measured capability improvement. The runtime score/plan defects are separately established by executable red-to-green tests.

Backend model identity, reasoning setting, tokens and monetary cost were not available; none are inferred. Read appendices are self-reported, not independent cost telemetry. These plans were not executed on live websites, media, ASR services, UI runtimes or PMUs. The additional writing/web/eli5 development cases are retained for future testing, not counted as executed here. Real tasks, isolated unseen cases and measured costs would be necessary for stronger generalization or efficiency claims; they are not blockers for this bounded correction and compression task.

Accepted the streamlined candidate under the scoped no-new-material-regression gate. No evaluator was weakened and no holdout suite was changed to produce a pass.
