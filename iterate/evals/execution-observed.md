# Iterate execution results — 2026-09-28

Status: all five paired development cases completed; local revision accepted
with the evidence limits below. This is not a general capability benchmark.
See [protocol](execution-protocol.md) and [portable evidence](execution-evidence.json).

## Identity and evidence boundaries

- Baseline repository: `7c86bf24bc3f5e397c4945e55d8875fd9a551a77`.
- Baseline runtime SHA256: `485da25b794516c45a25e8056f0b4c9ce31844396051fe9fbf065bc55af9b09f`.
- Candidate runtime SHA256: `aad45ee539387effbdadd3747b89359a6e1fc2a28c6bba702fe85623dc89d238`.
- Packet SHA256: `0a847eb10944ca4e193648e2419f130ed48e9264f79c5f9682619ab6947f093e`.
- Five cases, one isolated executor per case and arm. Same inherited session
  model/settings and tool surface; exact model identity, tokens and billing are
  unavailable. No overrides or cross-arm conversation forks.
- Runtime edit was withheld until all baseline executors finished. Fixture and
  packet bytes remain fixed. Run preparation later gained a guard against copying
  a fixture into itself; prepared contents and grading are unchanged.
- Execution commands and timings in `execution.md` are executor-written reports,
  not a harness-captured full action trace. Parent replay independently verifies
  final files, metrics, instruction snapshots and frozen-file integrity.
- Pipeline work counters measure executed decoding and category operations, not
  CPU speed. The measurement-selection cases use explicitly synthetic historical
  records. No deployment performance or generalization claim follows.

Local raw run directory: `.research/iterate-autonomy-2026-09-28/`, each run owns
`task.md`, `instruction.md`, `manifest.json`, `workspace/` and `replay.json`.
The portable archive contains these files, retained candidates and supplementary
results. Verbatim final chat messages and full action traces were not archived.

## Paired observations

All ten final artifacts pass the frozen v1 checks. This is narrower than full
contract correctness: both resume outputs fail the supplementary check below.
Pipeline figures are `decode / lookup`; lower counts are better.

| Case | Baseline instruction | Candidate instruction | Interpretation |
| --- | --- | --- | --- |
| pipeline-search | small 68 / 60; wide 164 / 300 | small 68 / 60; wide 164 / 300 | Tie on frozen metrics; both continued across mechanisms |
| pipeline-resume | small 70 / 60; wide 166 / 300 | small 68 / 60; wide 164 / 300 | Both rejected stale evidence; two fewer decodes is one observed outcome, not established skill uplift |
| noisy-promotion | steady, mean 109 | steady, mean 109 | Both used all confirmation rows rather than discovery leader |
| search-converged | current, mean 100 | current, mean 100 | Same choice; candidate notes explicitly state reopening conditions |
| explicit-target-done | current meets 100 | current meets 100 | Both stop at the sufficient target |

Selection means independently recomputed: current 100, sprint 94.5, steady 109.
All frozen files match their original fingerprints. Implementation inspection
found no instrumentation bypass; candidate caches are local to each call.
This does not establish absence of all unauthorized effects in an unrecorded trace.

The baseline already chose `steady` over the single-run leader, kept `current`
within the restricted candidate set, and stopped at the explicit sufficient
target. Independent artifact replay passed all three. The restricted-search
response scoped its result correctly but did not state an explicit reopening
condition; do not turn this omission into a claim that its choice was wrong.

The pipeline-search baseline also continued through several mechanisms and
retained a worse comparison candidate. Independent replay verifies its final
small-v1 work counts of 68 decode / 60 lookup and wide-v1 counts of 164 / 300,
with correct output on both datasets. Its original fixture counts were
664 / 1450 and 2392 / 29098. These are task improvements under the old skill,
not evidence that the new instructions improved performance.

The candidate pipeline executor retained a demand-driven lookup alternative.
It tied on the required workloads and improved a separately tested sparse case,
but added intermediate state. It kept the simpler standard-workload result and
recorded the sparse workload as a reopening condition. The baseline resume
executor made the opposite tradeoff after measuring that sparse case. Neither
choice is a general winner without a workload distribution and memory costs.

## Post-hoc correctness finding

The README accepts string records. A `str` subclass can be unhashable; the reference
still accepts it. Both resume implementations index their input cache by the raw
string and raise `TypeError`. Both pipeline-search implementations handle this
case. The parent reproduced all four outcomes with
[check_contract_edges.py](check_contract_edges.py), without modifying v1 results.

| Output | Frozen v1 checks | Supplementary unhashable-string check |
| --- | --- | --- |
| baseline-pipeline | Pass | Pass |
| candidate-pipeline | Pass | Pass |
| baseline-resume | Pass | Fail: TypeError |
| candidate-resume | Pass | Fail: TypeError |

These two generated programs are retained as failed contract examples, not
repaired in place or offered as deployable optimizations. The skill revision did
not eliminate this shared error. No string-specific instruction was added to
the general iterate skill in response to the visible case.

The parent also ran the same preserved 500-trial randomized contract checker on
all four outputs; all passed. Baseline pipeline's 1,200-trial script and candidate
resume's 1,000 batches / 2,000 random strings / 135 shape cases were independently
rerun successfully. Thus even these broader checks missed the string-subclass
case: reported random-test counts are not a correctness guarantee.

## Cost and remaining uncertainty

Executor time reports: pipeline about 5m51s / 5m45s; resume about 5–6m / 5–6m;
selection cases about 1–2m per arm. Exact initial-read and final-message times
were not uniformly captured, so these are reports/estimates, not measured cost
advantages. Same case caps were 6m for pipeline and 3m for replay cases.
Candidate documentation plus verification can consume much of a short replay
budget. No token or billing reduction is established.

The cases are visible development scenarios, each sampled once per arm, using a
single model setting. There is no model-only arm, untouched holdout, randomized
arm order, multi-day task, or cross-model replication. Route selection, memory
transfer to an unseen problem, true wall-clock performance, physical interruption
recovery and unrestricted open-search stopping remain unestablished. Sequential
arm execution prevents live-skill contamination but cannot exclude order effects.

## Delivery decision

Accept the scoped guidance and evaluation infrastructure changes: experiment
selection, promotion, relevant-memory retrieval and closure are more explicit,
without new approval gates, mandatory scores or experiment quotas. Runtime grew
from 107 to 112 lines (14,023 to 15,575 bytes), after consolidating repeated text.
This is a clarity and testability improvement, not demonstrated general autonomy
uplift. Existing prose cases remain unchanged; the executable suite is separate.

Local verification: 17 iterate tests and 47 repository tests pass. Archive tests
reconstruct all ten runs and reproduce both successes and known failures. Green
archive tests mean faithful replay, not ten fully correct executor solutions.
No commit, push, deployment or external system change was performed for this task.
