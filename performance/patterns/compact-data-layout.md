<!-- (C) 2026 Intel Corporation, MIT license -->
# Pattern: compact data layout

## When to apply

Apply when profiles show cache or memory-bandwidth pressure, or source uses
pointer-heavy nodes, nested maps, oversized fields, general sparse containers for
dense IDs, or individually allocated elements traversed together.

## Why this is slow

Useful data occupies too many cache lines and requires extra pointer loads. The
CPU waits on memory, prefetching becomes less effective, RSS grows, and allocator
metadata consumes additional space.

## The fix

1. Identify fields read together and the domain of keys and values.
2. Remove redundant state or narrow representation only with explicit range and
   compatibility checks.
3. Prefer contiguous or batched storage for elements traversed together.
4. Replace pointers with stable indices when ownership and relocation permit.
5. Use arrays or bit vectors for bounded dense domains; keep maps or sets when
   sparsity, mutation, or semantics justify them.
6. Separate hot fields from cold payload when doing so reduces the hot working set.

Library-specific containers are candidates, not universal defaults.

## Verification

Check behavior, serialization and ABI compatibility, iterator or pointer
stability, and memory ownership. Measure bytes per logical item, RSS, allocation
count, LLC misses or bandwidth, and end-to-end latency on representative data.

## Presenting this to the user

Show the old and new bytes or cache lines per logical item, the semantic promises
that constrain layout, and the measured benefit. Include migration cost when the
representation crosses a durable boundary.
