<!-- (C) 2026 Intel Corporation, MIT license -->
# Pattern triggers: profiling output

Use this file when you have profiling data — `perf annotate`, `perf c2c`,
`perf stat`, `perf report`, VTune, flamegraphs, or any sampled CPU profile.
Use matching patterns as hypotheses, then read only the relevant detail for
applicability, correctness constraints and a discriminating check. A profile
symbol or percentage routes investigation; it does not authorize a fix or prove
its cause. Numerical thresholds and example speedups are not portable acceptance
criteria, including in linked patterns.

Read `references/performance-foundations.md` when selecting or challenging a
mechanism, baseline or tradeoff; do not require it again just to interpret an
already scoped observation. Check CPU/event support before prescribing PMU commands.

## Contents

- Quick-match table
- Broad structural signals
- Compiler and SIMD patterns
- Concurrency patterns
- Known algorithms and library patterns

---

## Quick-match table

| Signal in profile | Pattern | Detail file |
|-------------------|---------|-------------|
| No dominant leaf symbol, but a wide inclusive stack or top-level loop owns most time | Flat profile | `patterns/flat-profile.md` |
| Allocator symbols or allocation counts are high; heap churn appears across many callers | Allocation reduction | `patterns/reduce-allocations.md` |
| High LLC miss rate, memory bandwidth pressure, large RSS, or pointer-chasing stalls | Compact data layout | `patterns/compact-data-layout.md` |
| Repeated small callees below a loop, or lock/validation/serialization cost multiplied per element | Bulk API | `patterns/bulk-api.md` |
| A common path spends time computing data that is discarded, repeated, invariant, or representable by a simpler fast path | Avoid unnecessary work | `patterns/avoid-unnecessary-work.md` |
| Accumulate instruction (`vaddss`, `vaddpd`, `vfmadd*`) dominates annotate; IPC ≪ 1; cache misses low | Serial accumulator | `patterns/parallel-accumulator.md` |
| `other_assists.avx_to_sse` > 0 in `perf stat`; or first SSE instruction after AVX function carries extreme cycle count in annotate | Missing vzeroupper | `patterns/missing-vzeroupper.md` |
| Scalar preamble (pointer subtraction + conditional branch) before an otherwise vectorizable loop; or two loop versions (one vectorized, one scalar) in annotate for a simple array function | Missing restrict | `patterns/missing-restrict.md` |
| Scalar FP (`addsd`, `mulss`, `movsd`) or `xmm` registers in hot loop on AVX2/AVX-512 CPU | Narrow SIMD | `patterns/simd-upconversion.md` |
| `lock cmpxchg` cluster with high density in annotate; throughput drops with more threads | Test-and-Set spinlock | `patterns/ttas.md` |
| `perf c2c` localizes material HITM traffic to a line; independent fields at different offsets are written by different threads | False sharing | `patterns/false-sharing.md` |
| `lock add` / `lock xadd` / `lock inc` in hot path; `perf c2c` true sharing on a stats/counter field | Shared statistics counter | `patterns/per-cpu-stats.md` |
| Hot symbol's DSO column shows a `.so` file (not the application binary); symbol appears in `references/library-versions.md` | Library version upgrade | `patterns/library-version-upgrade.md` |
| `crc32b`/`crc32q`/`pclmulqdq` instructions dominate a hot function; or a function named `crc32c`/`crc32_c`/`compute_crc32c` is prominent; single-accumulator CRC32 loop | Fast CRC32C | `patterns/fast-crc32c.md` |
| `futex_wake`, `try_to_wake_up`, `__pthread_cond_broadcast` hot; context-switch rate scales with thread count; IPC collapse with high CPU utilization | CV thundering herd | `patterns/cv-thundering-herd.md` |
| `osq_lock`, `mutex_lock`, `__mutex_lock_slowpath` (kernel) or `pthread_mutex_lock`, `__lll_lock_wait`, `futex_wait`/`futex_wake` (user-space) prominent; critical section is read-heavy (lookup/search); IPC drops with core count | Mutex to rwlock | `patterns/mutex-to-rwlock.md` |
| Hot function name matches a known algorithm (`hamming_distance`, `hamming_dist`, `cosine_similarity`, `jaccard_distance`, …) | Known algorithm — optimized SIMD replacement available | `references/known-algorithms-impl.md` |
| `std::sort`, `_introsort_loop`, `__gnu_cxx::__ops` hot in profile; data type is `float`, `double`, `int32_t`, `uint32_t`, `int64_t`, or `uint64_t` | SIMD sort | `patterns/simd-sort.md` |

---

## Pattern descriptions

### Broad structural signals

A flat leaf profile is not proof that no opportunity exists. Read
`patterns/flat-profile.md`, inspect inclusive stacks and top-level loops, and
collect the sensor that matches the suspected cost: allocation profile, cache
counters, lock contention, code-size evidence, or a representative microbenchmark.

Allocator pressure routes to `patterns/reduce-allocations.md`; cache and memory
pressure to `patterns/compact-data-layout.md`; multiplied per-element boundary
cost to `patterns/bulk-api.md`; and repeated or needless work to
`patterns/avoid-unnecessary-work.md`.

---

### Missing restrict

`perf annotate` shows a scalar **aliasing preamble** before the main loop: a
pointer subtraction, comparison, and conditional branch to a scalar fallback,
even though the loop body is a simple array operation. Two versions of the same
loop may appear — one vectorized, one scalar — where the scalar path exists only
to handle the (never-occurring in practice) aliased case. The hot loop may also
be fully scalar if the compiler abandoned vectorization rather than emitting the
versioned form.

Read `patterns/missing-restrict.md`.

---

### Missing vzeroupper

On CPUs exposing these events, `other_assists.avx_to_sse` and
`other_assists.sse_to_avx` can help investigate AVX/SSE transitions. Check
`perf list` and the event semantics first. A hot first legacy SSE instruction
after AVX code is a clue, not proof of transition cost. Confirm the instruction
path and target-specific behavior before testing boundary cleanup; preserve
register liveness and compare the same workload before claiming a gain.

Read `patterns/missing-vzeroupper.md`.

---

### Serial accumulator

The accumulate instruction (e.g., `vaddss`, `vaddpd`, `vmulss`, `vfmadd213ps`)
appears at the top of the `perf annotate` cycle-count column for a tight loop.
Low IPC with low cache-miss rates is compatible with a dependency bottleneck,
but does not exclude memory or frontend limits. Inspect the loop-carried chain
and compare cycles per iteration with the target CPU's instruction latency;
check the permitted numerical semantics before testing independent accumulators.

Read `patterns/parallel-accumulator.md`.

---

### Narrow SIMD

`perf annotate` shows scalar floating-point instructions (`addsd`, `mulss`,
`movsd`, `vaddss`, `vmulss`) or 128-bit packed operations (`xmm` register names)
in the hot loop body, on a CPU that supports AVX2 (`ymm`) or AVX-512 (`zmm`).
This suggests checking vectorization and dispatch, not a proportional speedup:
trip count, dependencies, memory traffic and frequency behavior can dominate.
Low IPC and low cache misses alone do not establish a compute bottleneck.

Read `patterns/simd-upconversion.md`.

---

### Test-and-Set spinlock

`perf annotate` shows a tight cluster of `lock cmpxchg` (or `lock xchg`,
`lock cmpxchg8b`) instructions with high sample density, with no ordinary load
of the lock variable preceding the atomic. `perf report` shows `spin_lock`,
`cmpxchg`, `try_lock`, or CAS wrapper functions prominently. The defining
scaling signal: throughput **declines** (not just plateaus) as thread count
increases, or a dual-profile comparison shows these functions jumping from
invisible at 1 core to dominant at N cores.

Read `patterns/ttas.md`.

---

### False sharing

`perf c2c` localizes HITM (Hit Modified) traffic to a cache line. The per-line
access map shows **different byte offsets** being
written by different CPU or thread IDs — the key sign that threads are not
actually sharing data, just sharing a cache line. The hotspot function appears
in the multi-core profile but not (or barely) at 1 core, and the regression
grows with thread count. Confirm independent source fields and benchmark a
layout change; neither a fixed HITM percentage nor linear scaling is required.

Read `patterns/false-sharing.md`.

---

### Shared statistics counter

`perf annotate` shows `lock add`, `lock xadd`, or `lock inc` in the hot path,
with no `cmpxchg` retry loop (which would indicate the TTAS pattern instead).
`perf c2c` shows true sharing on a counter or statistics field — the **same
byte offset** written by many CPUs. The function barely appears at 1 core but
grows linearly with thread count in the scaling profile, and field names suggest
accounting (`count`, `total`, `hits`, `misses`, `bytes`, `errors`, `stat`).

Read `patterns/per-cpu-stats.md`.

### Fast CRC32C

`perf report` or `perf annotate` shows `crc32b`, `crc32l`, or `crc32q`
instructions dominating a hot function, or a `pclmulqdq`/`vpclmulqdq` chain
with only one or two vector accumulators. A serial chain suggests investigating
instruction latency, but input size and memory traffic can change the limit.
The function name itself (`crc32c`, `crc32_c`, `compute_crc32c`) can route to the
reference; inspect the implementation before selecting a replacement.

Read `patterns/fast-crc32c.md`.

---

### SIMD sort

`perf report` shows `std::sort`, `_introsort_loop`, `__gnu_cxx::__ops`,
`std::__introsort_loop`, or `std::__sort` among the hottest symbols, and the
sorted data type is a numeric primitive (`float`, `double`, `int32_t`,
`uint32_t`, `int64_t`, `uint64_t`). `perf stat` may also show elevated
`branch-misses` — the comparator-driven branches of introsort are notoriously
hard for the branch predictor. Compare comparison/partitioning cost with memory
traffic before testing SIMD sort. Verify comparator and ordering semantics,
target dispatch and representative sizes; do not promise a speedup from a symbol.

Read `patterns/simd-sort.md`.

---

### Known algorithm — optimized SIMD replacement available

`perf report` shows a function whose name matches a well-known algorithm in
the table below. These algorithms have established vectorized implementations
that the agent can generate directly. Identify the ISA levels supported by
the target CPU (check `/proc/cpuinfo`), then read the algorithm's entry for
the dispatch strategy and implementation notes.

| Algorithm | Common function names in code |
|-----------|-------------------------------|
| Cosine Similarity | `cosine_similarity`, `cosine_sim`, `cos_sim`, `cosine_distance`, `angular_similarity`, `dot_normalized` |
| Hamming Distance | `hamming_distance`, `hamming_dist`, `hamming`, `count_differing_bits`, `bit_diff_count`, `popcount_xor` |
| Jaccard Distance | `jaccard_distance`, `jaccard_similarity`, `jaccard_sim`, `jaccard_index`, `jaccard_coeff`, `iou` |

If a function name from the table is present in the profile, read
`references/known-algorithms-impl.md` for the ISA levels, dispatch guards, and
implementation notes. Do not load it otherwise.

---

### CV thundering herd

`perf report` shows `futex_wake`, `try_to_wake_up`, or
`__pthread_cond_broadcast` consuming significant cycles — not lock contention
symbols like `spin_lock_slowpath`. `perf stat -e context-switches` shows
context-switch rate scaling with the number of waiting threads per broadcast.
`perf trace -e futex` shows frequent `FUTEX_WAKE` with `val=INT_MAX` (broadcast)
or rapid bursts of `val=1` (notify_one loop). IPC collapses while CPU utilization
remains high — cores are busy with scheduler dispatch and mutex re-acquisition,
not useful work. Key differentiator from lock contention: `perf lock stat`
shows normal hold/wait times.

Read `patterns/cv-thundering-herd.md`.

---

### Mutex to rwlock

**Kernel mutex**: `perf report` shows `osq_lock` (the kernel mutex Optimistic
Spin Queue), `mutex_lock`, or `__mutex_lock_slowpath` consuming significant
cycles, with cycle count growing as core count increases.

**User-space pthread mutex**: `perf report` shows `pthread_mutex_lock` /
`__lll_lock_wait` on the lock path and `futex_wait` / `futex_wake` in the
kernel slow path. Context-switch rate scales with thread count as threads
sleep and wake on the futex.

In both cases, the call chain traces to a mutex protecting a lookup, search,
or status-check operation that rarely modifies data. `perf lock stat` confirms
high `contentions` relative to `acquisitions` and `wait_total` >> `hold_total`.
IPC degrades with core count even though user-space work remains constant —
the incremental cycles are pure lock serialization overhead from readers
blocking each other.

Read `patterns/mutex-to-rwlock.md`.

---

### Library version upgrade

`perf report` or `perf annotate` shows a symbol whose DSO column names a
system library (`.so` file) rather than the application binary. The function
name matches an entry in `references/library-versions.md` — a known hotspot
for which a newer library version ships a significantly better implementation.

Check the installed version and actual implementation. A hot library symbol can
also reflect excessive caller work; compare an upgrade with reducing calls or
batching them before choosing a change.

Read `patterns/library-version-upgrade.md`.
