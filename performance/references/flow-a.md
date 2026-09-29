<!-- (C) 2026 Intel Corporation, MIT license -->
# Flow A: execution steps

## Interpret the output

Treat counters as observations, not portable bottleneck thresholds. Check the
measurement scope, event definitions, support and running fraction before
combining ratios; multiplexed or differently scoped counts may not be comparable.
Missing events are measurement gaps, not zero counts or failed optimizations.

| Observation | What it supports, and the next discriminating check |
|-------------|----------------------------------------------------|
| Low IPC | Possible dependency, memory, frontend or branch limits; localize hot code and inspect a matching stall or dependency signal. High IPC alone does not establish useful work or end-to-end efficiency. |
| Cache misses | Inspect absolute counts, event coverage and workload size; use access patterns and latency/bandwidth evidence to distinguish memory limits from incidental misses. A low rate does not exclude costly dependent loads. |
| Branch misses | Locate hot branches and their contribution before proposing branch removal; a miss percentage alone does not establish the dominant cost. |
| `task-clock` versus elapsed time | Describes CPU use within the measured task scope, not kernel share. Use separate user/system CPU accounting or appropriately scoped counters for kernel work; use off-CPU/scheduling evidence for waits. |

Report the leading supported explanation, the important alternative and the
smallest check that would distinguish them. Separate expensive on-CPU kernel
work from off-CPU waiting: neither a large kernel share nor low CPU use alone
proves an I/O bottleneck. If no mechanism is localized, suggest Flow B or a
matching wait/allocation sensor rather than prescribe a speculative fix.

For an interpretation-only request, answer from the supplied evidence and state
the missing check; do not start collecting data or changing code. For an
authorized optimization, continue through correctness and comparable workload
measurement. Further investigation is unnecessary once the requested acceptance
is supported; counter improvement alone is not an end-to-end speedup.
