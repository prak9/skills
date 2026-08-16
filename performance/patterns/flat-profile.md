<!-- (C) 2026 Intel Corporation, MIT license -->
# Pattern: flat profile

## When to apply

Apply when no leaf symbol dominates, yet the workload is materially slower or
more resource-intensive than required. A flat profile often means cost is spread
across many small callees or duplicated throughout one higher-level operation.

## Why this is hard

Optimizing the largest leaf may produce noise-level improvement. The useful unit
of analysis is the inclusive stack, top-level loop, allocation family, data
representation, or repeated boundary that causes many leaves to execute.

## The fix

1. Confirm the profile represents the production-shaped workload and optimized
   binary.
2. Inspect inclusive stacks and loops near the top of the call graph.
3. Group cumulative work by mechanism: allocation, parsing, hashing, logging,
   synchronization, pointer chasing, or repeated helper calls.
4. Collect the matching sensor—allocation profile, cache counters, contention
   data, code-size evidence, or a focused benchmark.
5. Form one structural hypothesis and change one mechanism at a time.
6. Accept cumulative small wins only when stable measurement can resolve them.

## Verification

Keep the same workload, build, hardware, and metric. Compare inclusive cost and
end-to-end behavior after each change; use enough samples to distinguish a small
gain from noise. Re-profile because removing one layer may reveal the next.

## Presenting this to the user

Do not report “no hotspot.” Report the dominant inclusive operation, cumulative
cost family, next sensor, falsifiable hypothesis, and evidence boundary.
