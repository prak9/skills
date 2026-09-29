---
name: performance
description: >-
  Profile and fix Linux CPU performance bottlenecks end-to-end: Linux `perf`
  workflows (A–E), Phoronix Test Suite benchmark execution and optimization, and
  source-level performance pattern diagnosis with measurable verification.
metadata:
  version: "1.0.0"
  language: "en-US"
---

<!-- (C) 2026 Intel Corporation, MIT license -->

# Performance skill (merged)

Unified entry for performance work: Linux `perf` profiling and reporting,
Phoronix benchmark handling, and performance-pattern guided code optimization.

The user's task determines the stopping point: diagnosis/report requests return
evidence and recommendations without source edits; fix/optimize requests continue
through in-scope changes and comparable verification. A flow or pattern does not
introduce a second approval gate for work already authorized. Ask only for a
material unknown, expanded scope, unapproved system/production change, or resource
cost beyond the task's bounds. Technical choices such as call graphs are yours to
make from the evidence and overhead, not preference questions for the user.

---

## How to use this skill

### Establish the performance argument

Use the supplied workload, metric, correctness constraint, baseline and evidence
boundary; recover only what is missing and material to the request. Existing
profiles can be interpreted without starting new measurement. Never claim a
measured speedup without comparable before/after evidence and correctness checks.

Read [performance foundations](references/performance-foundations.md) when
choosing or challenging an optimization mechanism, cost model, baseline or
resource tradeoff. Read [structural optimization](references/structural-optimization.md)
when reformulating a problem or permanently pruning/merging states. A local
counter explanation does not require either full analysis.

Select only the relevant branch below. Source-only diagnosis can start with
`triggers/from-source.md`; it does not require PTS setup or a perf recording.

---

## Part 1 — PTS benchmarks (`pts/<name>`)

For workload names like `pts/mt-dgemm`, read [PTS execution and optimization](references/pts.md)
before preparing or rebuilding the benchmark. Existing PTS results can be
interpreted without installing or rerunning the suite.

---

## Part 2 — Linux perf workflows

### Setup before new collection

Check only when collecting new evidence, not merely reading supplied counters:
- availability of `perf` and the requested events (`perf list`); do not assume a CPU-specific PMU name exists
- `/proc/sys/kernel/perf_event_paranoid` and permission mode
- debug symbols (`-g`) presence for `perf annotate`
- command context (who owns build, expected baseline, acceptable runtime)

- If debug symbols are missing, follow the scoped rebuild or assembly fallback in `references/building-blocks.md`; do not stop an authorized local optimization merely to reconfirm its build step.

### Choose a flow

Read only the flow needed by this question. Its collection and annotation steps
apply when they add material evidence within the authorized runtime, not as a
requirement to repeat already-matching work. The building-block reference is a
shared mechanics library, not an additional set of tasks to execute.

| Flow | Purpose | Read |
| --- | --- | --- |
| **Flow A** | `perf stat` quick counters (IPC / cache-miss / branch-miss) | `references/flow-a.md` |
| **Flow B** | `perf record + report` hotspots | `references/flow-b.md` |
| **Flow C** | `perf c2c` contention | `references/flow-c.md` |
| **Flow D** | scaling with core-count sweeps | `references/flow-d.md` |
| **Flow E** | hotspot report for sharing/follow-up | `references/flow-e.md` |

### Match the signal to pattern files

When `perf` identifies a repeated pattern, read:

- `triggers/from-profile.md` when you already have counters/profile.
- `patterns/` file matching that trigger row.
- `guidelines/new-code.md` for new code changes.

Keep the resolution order explicit:
1. asymptotic change,
2. remove/defer work,
3. data layout / allocation,
4. batching and contention reduction,
5. compiler + SIMD + instruction-level tuning.

---

## Part 3 — Resolution library

### Reusable modules

- `library/cpu-dispatch.md` — runtime ISA dispatch (`target_clones`, `__builtin_cpu_supports`)
- `patterns/simd-upconversion-impl.md` — safe vector width widening (SSE→AVX2→AVX-512), with guard/cleanup
- `patterns/fast-crc32c-impl.md` — CRC32C implementations and runtime selection

### Tooling

- `tools/branchprob.py` — runtime branch probability sampling from hot functions
- `tools/gccbranchprob.py` — GCC static branch-probability hints from profile-estimate dumps

Use one or two changes per iteration and remeasure each change before broad
refactoring.

For repeated experiment infrastructure, measure the full preparation, execution,
verification and retry cycle as well as the hot path. Relate an optimization to
plausible downstream reuse at unchanged correctness and measurement quality;
track valid negative experiments separately from infrastructure failures. Use
[research flywheel](../research-craft/references/research-flywheel.md) when results
drive a continuing research queue. A shorter benchmark call alone does not prove
higher research throughput, and ordinary profiling needs no new ledger.

### Common fix map

For representative hotspots, use these mapping targets:

- flat profile → `patterns/flat-profile.md`
- repeated API/lock crossings → `patterns/bulk-api.md`
- allocation churn → `patterns/reduce-allocations.md`
- cache-unfriendly structures → `patterns/compact-data-layout.md`
- repeated work and eagerness → `patterns/avoid-unnecessary-work.md`
- contention & locks → `patterns/false-sharing.md`, `patterns/ttas.md`, `patterns/per-cpu-stats.md`
- SIMD limitations → `patterns/simd-upconversion.md`, `patterns/parallel-accumulator.md`, `patterns/missing-vzeroupper.md`
- compiler support check → `patterns/library-version-upgrade.md`
