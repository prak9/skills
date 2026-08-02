<!-- (C) 2026 Intel Corporation, MIT license -->
# Pattern: algorithmic work

## When to apply

Apply when realistic cardinality multiplies nested scans, repeated searches,
incremental graph or heap maintenance, repeated sorting, or another avoidable
superlinear operation. Confirm input sizes and call frequency before treating a
small setup loop as a bottleneck.

## Why this is slow

The program performs more logical operations than the result requires. Faster
instructions preserve the bad growth curve; the cost returns as data grows and
often creates secondary allocation and cache pressure.

## The fix

1. State the current operation count using workload symbols such as `Q*N`.
2. Identify the invariant or data organization that permits one-pass, indexed,
   sorted, batched, or precomputed work.
3. Choose the smallest representation whose construction and memory cost are
   justified by reuse and cardinality.
4. Preserve duplicate, ordering, missing-value, failure, and lifetime semantics.
5. Treat reserve, copying, branch, and SIMD improvements as secondary until the
   growth curve is fixed.

## Verification

Compare old and new results, including duplicates and empty/missing cases. Measure
several realistic sizes so the expected growth change is visible; then check the
production-shaped workload for wall time, CPU, and memory regressions.

Label a routine-level benchmark as a microbenchmark even when its cardinality is
realistic. It validates the local mechanism, not full-application impact. For a
material system claim, report both the focused benchmark and an end-to-end run
that includes construction, callers, contention, I/O, and downstream work.

## Presenting this to the user

Lead with the operation-count model, show the proposed complexity and tradeoff,
then give measured results or a clearly labeled experiment plan. Do not promise a
speedup from complexity alone when constants or setup costs are unmeasured.
