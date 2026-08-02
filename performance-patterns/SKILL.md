---
name: performance-patterns
description: >-
  Diagnose and fix performance from source code or profiling output, prioritizing
  algorithmic work elimination, batching, allocation and data layout before
  lower-level x86/C/C++ tuning. Invoke when the user asks to optimize, review
  for performance, explain a flat profile, or write performance-sensitive or
  SIMD code. Trigger on: repeated scans, per-item API or lock crossings,
  allocation churn, pointer-heavy layouts, avoidable hot-path work, serial
  accumulators, narrow SIMD, HITM/cmpxchg clusters, false sharing, missing
  restrict or vzeroupper, thundering herds, or hot library symbols. Includes
  measured playbooks for structural, concurrency, compiler, and SIMD patterns.
---

<!-- (C) 2026 Intel Corporation, MIT license -->

# Performance patterns skill

A growing catalog of well-known code patterns that cause performance problems,
with detection signals and resolution playbooks for each.

---

## How to use this skill

### Step 0 — Establish the performance argument

Read `references/performance-foundations.md` for every task. Define the workload,
metric, correctness constraint, baseline, and evidence boundary before selecting
a fix. Use estimation to rank hypotheses when measurement is unavailable; never
claim an unmeasured speedup.

### Step 1 — Load the right file for your context

| Context | Read this file |
|---------|---------------|
| You have **profiling output** (perf annotate, perf c2c, perf stat, VTune, flamegraph, etc.) | `triggers/from-profile.md` |
| You are **reading existing source code** and have no profiling data yet | `triggers/from-source.md` |
| You are **writing new** performance-sensitive C/C++ or SIMD code | `guidelines/new-code.md` |

The trigger files cover all the same patterns; they are separated so you only
load what is relevant. `guidelines/new-code.md` is a write-time checklist —
load it instead of a trigger file when generating new code, not reviewing it.

### Step 2 — Identify the matching pattern

Each trigger file contains a compact table and brief descriptions — enough to
decide whether the code or profile matches a known pattern.

Search in leverage order: improve asymptotic behavior; remove or defer work;
compact data and reduce allocation; amortize API, lock, and serialization
boundaries; then tune compiler, code size, instructions, and SIMD. Skip an
earlier layer only when evidence rules it out.

### Step 3 — Read the pattern detail file

When a pattern matches, read the corresponding file from `patterns/`. Do not
attempt the fix from memory.

### Step 4 — Apply the fix and verify

Follow the step-by-step instructions and verification method in the pattern file.
Compare the same representative workload before and after, check correctness,
and state whether evidence is microbenchmark-only or end-to-end.

Multiple patterns can co-apply. Check all plausible matches before picking one.

---

## Reusable library modules

These standalone implementation guides are available to any agent working in this
skill, not only when following a specific pattern. Load the relevant file directly
if the capability is needed.

| Module | What it provides |
|--------|-----------------|
| `library/cpu-dispatch.md` | Runtime CPU feature detection and variant selection: `target_clones` (compiler-driven, plain C/C++) and `__builtin_cpu_supports` (hand-written variants). Use whenever a function has multiple performance-level implementations that need to be wired together at runtime. |
| `patterns/simd-upconversion-impl.md` | Full step-by-step zipper algorithm for doubling vector register width in asm/intrinsics (SSE→AVX2 or AVX2→AVX-512); AVX-512 accumulator template; post-transformation checklist (CPUID guards, vzeroupper, clobber list). |
| `patterns/fast-crc32c-impl.md` | Drop-in CRC32C library: AVX-512 VPCLMULQDQ fusion (corsix v3s1_s3, 64–97 GB/s), SSE4.2+PCLMULQDQ 3-accumulator (~15–25 GB/s), plain C fallback. Runtime CPU dispatch wrapper included. Use whenever new CRC32C code is needed or an existing implementation is the bottleneck. |

## General reference

| Reference | What it provides |
|---|---|
| `references/performance-foundations.md` | Cost estimation, optimization order, API and data-shape judgment, flat-profile tactics, and the evidence required to accept a performance change. |
