<!-- (C) 2026 Intel Corporation, MIT license -->
# Pattern: avoid unnecessary work

## When to apply

Apply when a frequent path computes invariant or unused results, runs a general
algorithm for a common simple case, performs eager work that is rarely consumed,
rechecks the same condition, or formats/logs data even when the output is disabled.

## Why this is slow

The fastest operation is the one not executed. Repeated work consumes CPU and
often creates allocations, cache pressure, branches, and code size that disguise
the shared structural cause across a flat profile.

## The fix

1. Prove which outputs or cases are common and which work is invariant or unused.
2. Remove the work, hoist it to a less frequent scope, defer it until demanded,
   precompute stable results, or add a simple fast path.
3. Cache only with explicit invalidation, size, ownership, and concurrency rules.
4. Keep the generic slow path as the semantic reference when it is still needed.
5. Avoid duplicating large logic between paths; the optimization must remain
   auditable against one contract.

## Verification

Test fast and slow paths, invalidation, state changes, and uncommon inputs.
Measure path frequency and end-to-end impact; confirm that deferred work does not
move latency to a more important point or increase retained memory unexpectedly.

## Presenting this to the user

State what work was avoided and how often, not merely which instruction became
faster. Show the guard or lifetime assumption and the evidence that it holds.
