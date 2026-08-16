<!-- (C) 2026 Intel Corporation, MIT license -->
# Performance foundations

Use this reference before choosing a source or profile pattern. Performance work
is a controlled argument: a representative workload and cost model identify the
dominant mechanism; a change removes that mechanism; comparable evidence shows
whether the system improved without breaking correctness.

## Set the contract

- Name the workload shape: cardinality, request mix, data distribution, thread
  count, warm/cold state, and relevant hardware or deployment constraints.
- Choose the user-facing objective: latency percentile, throughput, CPU time,
  memory, code size, build time, or cost. Do not silently substitute one metric
  for another.
- Record correctness, compatibility, determinism, and resource constraints that
  the optimization must preserve.
- Establish a baseline. If execution is unavailable, use a back-of-the-envelope
  estimate and label the conclusion as a hypothesis rather than a speedup.

## Rank by leverage

Investigate in this order unless evidence rules out an earlier layer:

1. **Algorithm:** remove superlinear, duplicate, or incremental work.
2. **Necessity:** skip, defer, precompute, cache, or specialize work that need not
   occur on the common path.
3. **Representation:** reduce bytes, pointers, cache misses, allocations, copies,
   and over-general containers.
4. **Boundary:** batch API calls, locks, validation, parsing, serialization, and
   other fixed per-operation costs.
5. **Execution:** improve parallelism, contention, compiler visibility, code
   layout, branch behavior, instruction selection, and SIMD.

An instruction-level win cannot compensate for unnecessary orders of magnitude
of work. Conversely, do not impose a disruptive redesign when a simple local
choice is measurably sufficient.

## Estimate before building

Count expensive operations at realistic scale: scans, allocations, bytes moved,
cache-line traffic, locks, syscalls, storage operations, and network round trips.
Multiply by rough local costs to reject dominated designs. Keep dated hardware
numbers as estimates, not universal constants.

Distinguish setup code, application hot paths, and reusable library code. A small
local inefficiency in a widely reused library can become material even when no
single caller can fix it easily.

## Treat APIs as performance commitments

- Offer bulk operations when callers otherwise repeat a fixed boundary cost.
- Prefer non-owning views when ownership transfer is unnecessary.
- Permit caller-owned scratch or precomputed inputs when this removes repeated
  allocation or computation without making the interface unsafe.
- Do not force internal synchronization on callers that already synchronize;
  when most callers need synchronization, encapsulate it so the implementation
  can shard or change without breaking them.
- Avoid promises such as pointer stability or generality unless users need them;
  they constrain future representations and make every caller pay.

## Interpret flat profiles

When no leaf dominates, inspect inclusive stacks and loops near the top of the
call graph. Many small costs can share one structural cause. Collect a matching
sensor rather than guessing: allocation profiles for heap churn, hardware
counters for cache or branch behavior, contention data for synchronization, and
binary-size or instruction-cache evidence for code bloat.

Change one mechanism at a time. Stable microbenchmarks are useful for iteration,
but validate important gains in the full workload because cache state, contention,
I/O, and call patterns can reverse a local result.

## Acceptance evidence

Report the baseline and candidate on the same workload, metric, environment, and
build. Include correctness checks, sample count or uncertainty when available,
resource tradeoffs, and the residual boundary not exercised. Never turn a profile
percentage directly into an expected end-to-end speedup.

## Source

This reference distills the general single-binary tuning principles in Jeff Dean
and Sanjay Ghemawat's [Abseil Performance Hints](https://abseil.io/fast/hints.html).
Library-specific examples remain conditional on the project's language,
dependencies, workload, and measured bottleneck.
