<!-- (C) 2026 Intel Corporation, MIT license -->
# Pattern: reduce allocations

## When to apply

Apply when allocation profiles, source inspection, or container growth show heap
allocation, copying, or temporary construction repeating in a frequent path.
Common signals are growing containers without reserve, short-lived objects inside
loops, and scratch buffers reconstructed on every call.

## Why this is slow

Allocation adds allocator bookkeeping, synchronization, initialization, cache
misses, and eventual destruction or collection. Scattered objects also increase
pointer chasing and working-set size.

## The fix

Use the least invasive applicable option:

1. remove the object or computation entirely;
2. reserve or size the destination from a trustworthy bound;
3. reuse caller-owned or loop-external scratch storage;
4. pass a non-owning view when ownership transfer is unnecessary;
5. use inline, arena, batched, or contiguous storage when lifetime and upper
   bounds justify it;
6. periodically release oversized reusable buffers when peak retention matters.

Do not trade clear ownership for a small allocation count without evidence.

## Verification

Compare allocation count and bytes, CPU or wall time, peak and retained memory,
and cache behavior on representative input distributions. Verify lifetime,
aliasing, exception/failure cleanup, and output equivalence.

## Presenting this to the user

Name the allocation site and multiplicity, then connect the proposed lifetime or
storage change to measured allocation and end-to-end effects. State retained
memory or ownership tradeoffs explicitly.
