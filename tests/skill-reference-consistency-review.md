# Skill reference consistency follow-up

Baseline: `771043f5f9506f90640a4dd2b6ea500189beaa34`. This is a bounded follow-up to the [streamlining review](skill-streamlining-review.md), not a new compression or capability claim.

## Corrections

- `performance`: Flow A no longer derives bottlenecks from fixed IPC/miss thresholds or kernel share from `task-clock`. The profile router treats patterns as hypotheses, checks event applicability, and does not promise SIMD/library speedups from a hot symbol. Specialized implementation patterns remain available; they were not comprehensively revalidated in this change.
- `web-design`: review-only requests return supported findings without editing source; authorized implementation still proceeds through repair and rendered verification.
- `plan-skill`: Lite completion keeps consequential findings in `program.md`; Full/Loop retains `memory.md`. No additional Lite record or approval is required.

For the timing distinction, upstream [perf-stat documentation](https://raw.githubusercontent.com/torvalds/linux/master/tools/perf/Documentation/perf-stat.txt) separately describes elapsed and user/system timings, event selection and counter running fractions. Hardware-specific observations still require target-specific evidence.

## Verification

Two new document-contract tests reproduced the old rules before the correction: the Lite rule failed, and Flow A failed its three forbidden-inference subchecks plus the enclosing test. After the correction, both tests and all three subchecks pass. These tests guard instructions, not runtime or model behavior.

```bash
python3 -m pytest -q tests plan-skill/tests
```

Result: **206 tests and 290 subtests passed** in 22.45 seconds. Explicit-path `git diff --check` passed. The five-case JSONL packet parsed with `jq`. An unrelated `.system` update made one unrestricted diff check race with a disappearing file; the scoped check succeeded, and no system files were changed by this task.

An independent read-only reviewer found no material defect in the targeted diff and verified that the changes preserve authorized implementation, Full/Loop state and performance correctness constraints.

## Forward smoke

The [five-case packet](skill-reference-consistency-cases.jsonl) was fixed before forward execution. A fresh executor received only prompts and instruction paths, not criteria, diffs or previous answers. It answered the cases as one batch, reading the relevant current Skills and references. The main agent graded the answers against the three criteria per case: **5/5 cases, 15/15 criteria passed**.

| Case | Observed answer summary |
|---|---|
| counter-ratios-not-cause | IPC and miss rates do not justify cache blocking; check CPU/event scope and hotspot access/latency/bandwidth evidence. No commands or changes. |
| task-clock-not-kernel-share | 100 ms over 2 s is about 0.05 CPUs within scope, not 95% kernel I/O; separate CPU accounting from off-CPU wait causes. |
| visual-review-is-read-only | Inspect source and rendered mobile/laptop views; return located, evidence-backed findings and limitations without edits. |
| visual-fix-remains-authorized | Reproduce and fix both authorized defects, preserve approved design, verify keyboard focus and mobile error rendering without reapproval. |
| lite-completes-in-one-record | Finalize evidence/result/date in `program.md`, reuse the existing reflection, and complete without `memory.md` or an invented owner gate. |

Executor-reported complete reads: `AGENTS.md`, the three Skills' entrypoints, performance Flow A and profile router, web-design interface-quality, and plan-skill status-and-completion. Only discovery and reading were performed; no hypothetical repair, benchmark or UI inspection was actually executed.

This is a visible development smoke, not an isolated holdout, blinded grading or old/new capability comparison. Cases shared executor context. Backend identity, token usage and monetary cost were not available. It supports this scoped instruction correction, not a claim of measured speedup or general autonomous reliability.

At the end of this verification round, all changes were local; no commit, push, deployment or native-goal operation had been performed. Publication is a separately authorized step.
