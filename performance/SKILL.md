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

Unified entry for Linux `perf`, Phoronix benchmarks and source-level optimization.
Diagnosis returns evidence; authorized optimization continues through comparable
before/after measurement and correctness verification.

---

## How to use this skill

### Establish the performance argument

Recover the workload, metric, correctness constraint and baseline. Existing profiles
can be interpreted directly; a speedup claim requires comparable before/after
evidence and correctness checks.

Read [performance foundations](references/performance-foundations.md) for mechanisms,
cost models or baseline/resource tradeoffs, and [structural optimization](references/structural-optimization.md)
when reformulating a problem or permanently pruning states.

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

Only for new collection, check:
- availability of `perf` and the requested events (`perf list`); do not assume a CPU-specific PMU name exists
- `/proc/sys/kernel/perf_event_paranoid` and permission mode
- debug symbols (`-g`) presence for `perf annotate`
- build ownership, baseline and acceptable runtime

If symbols are missing, use the scoped rebuild or assembly fallback in `references/building-blocks.md`.

### Choose a flow

Read only the flow needed. Do not repeat matching evidence; `references/building-blocks.md`
is a mechanics library, not another workflow.

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

Prefer isolated changes and remeasure before broad refactoring.

For repeated experiments, include preparation, verification and retry cost, and
separate valid negative results from infrastructure failures. Use the
[research flywheel](../research-craft/references/research-flywheel.md) only when
results drive a continuing queue; ordinary profiling needs no ledger.

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
