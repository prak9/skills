# Dependency-Aware Research — Smoke Review

Reviewed 2026-10-05. Baseline: `18fe023c1a82c8e3bd2254481e8c52c0bf264f89`. Candidate adds a conditional research adapter and routing, without a new Skill or runtime scheduler. [Cases and criteria](deep-research-cases.md) were fixed before editing. Raw responses: [baseline](deep-research-baseline.json), [candidate](deep-research-candidate.json).

## Execution And Limits

Two fresh forward executors received the same six prompts and no grading criteria, proposed edits or sibling outputs. The baseline read a copied pre-edit Skill; the candidate read the changed Skill. Both inherited the parent runtime/model settings without overrides; exact model version, reasoning configuration, tokens and billed costs were not captured. Each arm answered the six prompts sequentially in one shared context. This is a batch-context smoke comparison, not six independent trials or a held-out benchmark.

The instruction author graded observable answers against the fixed criteria; grading was not blind or independent. Both executors reported reading the entrypoint and three references. The baseline reference set included automated-discovery; the candidate used deep-research instead. File counts are self-reported, not verified per-case cost telemetry. The harness captured JSON responses separately; no scenario research, live source access or operational handoff writes were performed.

| Case | Baseline | Candidate | Evidence in the recorded answers |
|---|---|---|---|
| D1 | Pass | Pass | Both make eligibility/workload prerequisites for applicable cost and keep correctness independent; neither executes the plan. Candidate also makes the readiness of workload discovery explicit. |
| D2 | Pass | Pass | Both retain Q3, distinguish retrieval failure from ineligibility, and keep Q2 conditional despite the worker's completion label. |
| D3 | Pass | Pass | Both identify 2,200 missing rows, cite S1/S2 locators, reject repeated S3 as independent support, and keep chunking untested. Candidate explicitly avoids attributing the exact 9,800 result to the 10,000 cap. |
| D4 | Pass | Pass | Both select the current plan-specific manual rather than stop after one follow-up or declare compliance from incompatible values. |
| D5 | Pass | Pass | Both give two direct sentences without planning or task-side operations. |
| D6 | Pass | Pass | Both reuse the existing owners, retain revision/section/claim provenance, distinguish a tenant ceiling from worker count, and preserve the unrelated running branch. Candidate also qualifies local replay's inability to establish vendor behavior. |

Both arms pass 6/6 under author grading. Differences in specificity do not establish a general capability or efficiency gain. The change is retained as explicit, discoverable support for dependent source research and a lighter alternative to experiment infrastructure, with no observed regression on these prompts.

Unverified: actual parallel-worker execution, readiness scheduling latency, source persistence across real compaction, interruption recovery, live-source reliability, automatic Skill selection from its new description, and effects outside the visible prompts. These require appropriate execution fixtures or future usage evidence, not stronger claims from this batch.

## Candidate Identity And Static Checks

SHA-256 of the tested instruction surface:

```text
4c554780c162494f3ca112f3806e09955f5bd65c799c708c7c2f8ed91f71c150  research-craft/SKILL.md
b3cfe2d97d99eafa9f62ac350afc0a14d135ba58650fbb51ec9d6c36135af282  research-craft/references/deep-research.md
162d68a07cb161e0358418c096491299181aa275c852de9fdc655816ce957f2c  research-craft/references/automated-discovery.md
e9b0739862427a432125f2a9dfd97be26fd5abe34316b8e8f6b810f7b11acb2d  research-craft/agents/openai.yaml
```

`python3 .system/skill-creator/scripts/quick_validate.py research-craft` passed. `python3 -m unittest discover -s tests` passed 89 tests. These checks establish repository/metadata compatibility, not behavioral learning or real scheduling guarantees.
