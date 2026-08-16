<!-- (C) 2026 Intel Corporation, MIT license -->
# Pattern: bulk API

## When to apply

Apply when a loop crosses the same API boundary per element and each call repeats
a fixed cost: locking, RPC, validation, parsing, serialization, dispatch, lookup,
or setup. The signal is multiplication of a small boundary cost by batch size.

## Why this is slow

The interface prevents the implementation from seeing the whole job. It cannot
amortize fixed costs, choose a better algorithm, reserve once, coalesce I/O, or
hold synchronization for the shortest useful aggregate operation.

## The fix

1. Define a bulk operation around the caller's actual need, not merely a vector
   wrapper around the old API.
2. Move the fixed boundary cost outside the element loop.
3. Specify ordering, duplicate handling, partial failure, atomicity, cancellation,
   and return semantics before implementation.
4. Keep the scalar API when it remains useful; implement it through the bulk path
   only when that preserves latency and semantics.
5. Avoid extending a public interface until a real caller demonstrates the shape.

## Verification

Test empty, singleton, duplicate, partial-failure, and large batches. Benchmark
across batch sizes and realistic concurrency. Measure the boundary itself—lock
acquisitions and wait time, RPC count, parses, allocations, or bytes copied—in
addition to end-to-end throughput and latency.

## Presenting this to the user

Show the old per-element cost, the proposed amortized contract, semantic choices,
and evidence. Do not recommend a new lock primitive when the dominant problem is
needlessly acquiring any lock once per element.
