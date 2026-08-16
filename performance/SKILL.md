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

---

## How to use this skill

### Step 0 — Establish the performance argument

Read `references/performance-foundations.md` for every task. Define workload,
metric, correctness constraint, baseline, and evidence boundary before selecting
the first action. Use estimation only when measurement is unavailable; never
claim a measured speedup without before/after evidence.

---

## Part 1 — PTS benchmarks (`pts/<name>`)

For workload names like `pts/mt-dgemm`, run this part before any `perf` work.

### Flow A — Run a benchmark

1. Resolve version: if version missing, refresh and resolve via test profiles.
2. Install benchmark definition/package.
3. Run benchmark.
4. Parse output.
5. Save/report result with score and units.

### Flow B — Optimize a benchmark

1. Run Flow A and label `"baseline"`.
2. Prepare source from test definition (`installed-tests/.../install.sh`).
3. Profile/optimize with this skill:
   - `performance` profiling flows for hotspots
   - `patterns/` fixes for recognized code paths
4. Rebuild benchmark and rerun Flow A with change label.
5. Compare using test `hib` semantics.

### PTS primitives you should use

Use this PTS flow:

- `batch-install`, `batch-run` command flow
- parse summary output (`Average:`) into score + unit
- persist and compare results in `files/pts-results.json` when available

Use these paths:

- `phoronix-test-suite` installed test path: `/var/lib/phoronix-test-suite` (root) or `~/.phoronix-test-suite` (user)
- install metadata in `installed-tests/pts/<test-name>-<version>/`
- compile flags in `generated.json` / `pts-install.json` when optimizing

For benchmark-specific source edits:
- read the benchmark `install.sh`
- follow original build order
- avoid changing upstream defaults except when explicitly testing `-march`/`-O`/SIMD flags
- rebuild in the source layout described by `install.sh`

---

## Part 2 — Linux perf workflows

### Step 1 — Setup checks

Quickly check:
- `/proc/sys/kernel/perf_event_paranoid` and permission mode
- debug symbols (`-g`) presence for `perf annotate`
- command context (who owns build, expected baseline, acceptable runtime)

- If debug symbols are missing and workload is non-PTS, ask permission to rebuild with only `-g` added.

### Step 2 — Choose a flow

| Flow | Purpose | Read |
| --- | --- | --- |
| **Flow A** | `perf stat` quick counters (IPC / cache-miss / branch-miss) | `references/flow-a.md` |
| **Flow B** | `perf record + report` hotspots | `references/flow-b.md` |
| **Flow C** | `perf c2c` contention | `references/flow-c.md` |
| **Flow D** | scaling with core-count sweeps | `references/flow-d.md` |
| **Flow E** | hotspot report for sharing/follow-up | `references/flow-e.md` |

### Step 3 — Match the signal to pattern files

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
