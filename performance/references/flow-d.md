<!-- (C) 2026 Intel Corporation, MIT license -->
# Flow D: execution steps — Core-count scaling analysis

Use this flow when a workload does not scale well as CPU core count increases: adding
more cores produces little or no throughput gain, or performance actually regresses.

---

## Phase 0 — Optional: threading pre-check and scaling sweep

Before diving into function-level profiling, a scaling sweep can show where throughput
stops improving. Inspect source/library clues and runtime thread activity separately;
throughput scaling alone cannot establish whether a workload is threaded.

### Step 0a — Threading inspection (always run)

Check whether the binary links a threading library as a preliminary clue:

```bash
ldd <binary> | grep -E 'libpthread|libgomp|libtbb|libomp'
```

Also check for threading use in source if available:

```bash
grep -r 'OMP_NUM_THREADS\|pthread_create\|tbb::\|std::thread\|#pragma omp' \
    <source_dir> 2>/dev/null | head -5
```

Summarize what you found — e.g., *"Binary links libgomp (OpenMP)"* or *"No separate
threading library or source usage found; runtime threading remains unverified."*
Static linkage, runtime-loaded libraries, and threading APIs in libc can make `ldd`
inconclusive. When a representative run is available, inspect worker counts, thread
states and per-thread CPU use during its timed region (for example `ps -L -p <pid>`
and `pidstat -t -p <pid> 1`, if available). Distinguish created threads from active
workers; record affinity and CPU quota that could limit their execution.

### Choose the sweep (informed by Step 0a)

Use a bounded sweep when the scaling curve will change the diagnosis and fits the
task's runtime and resource bounds. Reuse matching profiles; otherwise start with
function-level evidence. Ask only if collection needs a material resource commitment
or environment change outside the authorized task.

If only static clues are available, report threading as unverified; do not use the
absence of a separate threading library to predict or diagnose flat scaling.

If the sweep is unnecessary or out of scope, skip to Phase 1.

### Step 0b — Sweep and profile collection

Run the workload at a bisecting sequence of core counts. Use `taskset -c 0-<N-1>` to
pin to the first N logical CPUs.

Start with: **1, 2, nproc/4, nproc/2, nproc** (remove duplicates for small nproc).
If the scaling factor between two adjacent points drops unexpectedly (< 0.80/core of
ideal), insert a midpoint and re-run.

**For each core count**, run once for throughput numbers:

```bash
taskset -c 0-<N-1> <command> 2>&1 | grep -E '<metric_pattern>'
```

**Additionally, at the three anchor points (1-core, nproc/2, nproc), also collect a
`perf record` profile** so Phase 1 can reuse them without re-running:

```bash
# 1-core profile
taskset -c 0 perf record -g -o perf_1core.data -- <command>

# N/2-core profile
taskset -c 0-<half-1> perf record -g -o perf_halfcore.data -- <command>

# N-core profile
taskset -c 0-<N-1> perf record -g -o perf_ncore.data -- <command>
```

Note: the throughput run and the perf record run are separate — `perf record` adds
overhead that would skew the sweep numbers.

If the N-vs-1 throughput ratio is < 1.05, report **no meaningful scaling observed;
cause not yet established**, accounting for measurement noise. This is not evidence
that threads are absent. Use the runtime evidence to choose the next investigation:

- Workers blocked in `pthread_mutex_lock`/futex waits: measure lock wait/hold time
  and inspect the protecting critical section and call chain. CPU samples alone can
  miss sleeping waiters; do not prescribe rwlock or TTAS without the access pattern.
- Multiple busy workers with little lock waiting: check memory bandwidth against
  the machine's measured sustainable bandwidth, working-set/access patterns, and
  relevant NUMA evidence. Low IPC or cache misses alone do not prove saturation.
- Only one active worker: check thread configuration, work distribution, and CPU
  limits before concluding the workload is serial.

Continue the relevant diagnostic path for a threaded workload even if the ratio is
near one or falls below one. Narrow or stop extra sweep points only when they add no
useful evidence or exceed the agreed runtime; do not stop diagnosis at a ratio cutoff.

### Step 0c — Format the sweep table

Present results as:

```markdown
## Scaling sweep

| Cores | Score   | Score factor | Scaling factor |
|-------|---------|--------------|----------------|
|     1 | 12.3 X  |      1.00×   |          —     |
|     2 | 22.1 X  |      1.80×   |      0.90×/core|
|     5 | 48.6 X  |      3.95×   |      0.79×/core|
|    10 | 67.2 X  |      5.46×   |      0.55×/core|
|    20 | 71.0 X  |      5.77×   |      0.29×/core|
```

- **Score factor** = Score(N) / Score(1)
- **Scaling factor** = (Score(N) – Score(prev)) / (N – prev) / Score(1) — the
  per-core marginal gain, normalized to the single-core score. A value well below 1.0
  indicates Amdahl-limited or lock-contended behaviour.

Note the **inflection point** — the core count at which the scaling factor first drops
below **0.80**. This is the primary target for Phase 1 profiling.

> *"Scaling inflection: cores ≤ N give near-linear gains; beyond N, gains become
> sub-linear. Running Phase 1 dual-profile at 1 vs. [inflection+1 or nproc] —
> profiles already collected in `perf_1core.data` and `perf_ncore.data`."*

---

## Phase 1 — Dual-profile collection

Run **Building block: Ensure debug symbols** in [building-blocks.md](building-blocks.md#building-block-ensure-debug-symbols) on the binary **before** Phase 1 recording. The dual-profile recordings must use the same binary as any later `perf annotate` passes — recompiling after recording invalidates the perf.data files.

**If Phase 0 was completed**, `perf_1core.data` and `perf_ncore.data` are already
available — skip straight to the Dual-profile comparison building block using those
files. Only re-record if the binary was recompiled for debug symbols after Phase 0.

Use [Building block: Dual-profile comparison](building-blocks.md#building-block-dual-profile-comparison).

This runs the workload at 1 core (`taskset -c 0`) and at all cores, collects the
top-15 hottest functions from each, and produces a delta table with rank-change (Rank Δ)
and percentage-change (% Δ) columns.

Identify the **jumper** functions using the thresholds defined in the building block
(rank rose ≥ 3, % ratio ≥ 2×, absolute gain ≥ 3%, or new entrant ≥ 2%).

**If the delta is overwhelming** (more than ~7 functions jump significantly, making
prioritization unclear): collect a midpoint profile at N/2 cores within the task's bounds (see
Building block: Dual-profile comparison, Step 3) and use the midpoint vs N-core
delta instead to get a shorter, more actionable list.

---

## Phase 2 — Source collection for jumping functions

For each jumper function identified in Phase 1:

### 2a. Collect the source

Use **Building block: Top-N lines within a function** to find the hot lines, and
collect the full source of the function using the source display rules in [Flow C](flow-c.md#annotation-conventions-used-throughout-the-report)
(≤ 20 lines: show in full; > 20 lines: show signature + context around hot lines).

### 2b. Check for inlining

Check whether the function is inlined into a caller using `perf report` or `objdump`:

```bash
perf report -i perf_ncore.data --stdio --no-children \
    --sort=sym --show-nr-samples 2>/dev/null | grep -A3 "<function_name>"
```

If inlined, decide which function is the true candidate:

| Inlinee size | Priority |
|--------------|----------|
| **Small helper** (≤ ~10 lines, wraps a single atomic or lock primitive) | The **outer (inlining) function** is the candidate — the helper is just a thin wrapper; fix the calling pattern |
| **Non-trivial** (loop, decision tree, non-trivial logic) | The **inlinee itself** is the candidate — the logic inside is the bottleneck |

Collect source for both the inlinee and the outer function; note the priority in the
report.

---

## Phase 3 — Focused c2c

When the evidence suggests cache-line sharing, use [Building block: c2c hot cache
lines](building-blocks.md#building-block-c2c-hot-cache-lines), then filter the
presentation to the functions from Phase 2. For blocked mutex waiters or suspected
bandwidth saturation, use the matching wait-time or bandwidth measurements from
Phase 0b; c2c is not required to investigate those mechanisms.

### 3a. Collect and generate the full c2c report

Use **Building block: c2c hot cache lines** for recording and reporting.

### 3b. Filter to jumping functions

From the c2c report, extract only the cache lines where any accessor function matches
a jumper from Phase 1. Ignore all other cache lines regardless of their HITM
percentage — the goal is to link the scaling bottleneck to specific cache lines, not
to do a general contention audit.

Present the filtered table:

```markdown
## Focused c2c — cache lines touched by jumping functions

| Address | Tot Hitm | Accessor functions (from Phase 1) | Sharing type |
|---------|----------|-----------------------------------|--------------|
| 0x...   | 18.3%    | `spin_lock`, `spin_unlock`        | True sharing |
| 0x...   | 9.1%     | `update_counter`                  | True sharing |
```

If a jumping function does not appear in a hot cache line, report the evidence limit.
Absence of HITM does not exclude sleeping lock waiters, bandwidth saturation, or NUMA
effects. Choose wait-time, bandwidth, or **Flow B** compute/branch investigation from
the runtime evidence rather than inferring the cause from missing c2c entries.

---

## Phase 4 — Categorize and diagnose

For each jumping function and its associated hot cache line (if any), classify the
bottleneck into one of these patterns:

| Pattern | Signals | Resolution strategy |
|---------|---------|---------------------|
| **False sharing** | Jumping function writes to one struct field; another function (different thread) writes a different field on the same cache line (different offsets in c2c Offset column) | [Structured false-sharing fix](../patterns/false-sharing.md) |
| **cmpxchg / Test-and-Set spin** | `lock cmpxchg` / `lock xchg` in hot path; function name contains `spin_lock`, `mutex`, `cas`, `try_lock`. Confirm the retry loop with [Annotate pattern scan](building-blocks.md#building-block-annotate-pattern-scan) | [Test-and-Test-and-Set (TTAS)](../patterns/ttas.md) |
| **True sharing — statistics** | Contended field is a counter or accumulator (`atomic_inc`, `++`, `atomic_add`); no compare-exchange loop | [Per-CPU statistics aggregation](../patterns/per-cpu-stats.md) |
| **True sharing — data** | Contended field is genuine shared data (not a counter, not a lock) | Consider atomics, RCU, finer lock granularity, or R/W primitives (see Flow C true-sharing guidance) |
| **No c2c signal** | Function jumps in profile but does not appear in c2c top cache lines | Use observed worker states, lock waits and bandwidth to select the next sensor; use **Flow B** for supported compute/branch hypotheses |

Document the diagnosis clearly before applying any fix. If multiple jumpers fall into
different categories, address them in order of HITM percentage (highest first).

---

## Phase 5 — Apply resolution

Apply the pattern linked in the Phase 4 table after confirming its mechanism. Other
profile-to-pattern mappings are in [triggers/from-profile.md](../triggers/from-profile.md).

For an authorized optimization, explain the supported change briefly and apply it
without another go-ahead. Diagnosis-only requests stop at the evidenced recommendation,
not at an invitation to perform unrequested edits. A semantic, production, or scope
change outside the task still requires the corresponding authorization.

After the fix is applied, rebuild the workload and run a quick `perf stat` (use
**Building block: perf stat**) to confirm the workload's overall throughput improved.

---

## Phase 6 — Iterate

Multiple bottlenecks almost always exist simultaneously. When one bottleneck dominates,
it masks the others: fixing it reveals the next one in the profile.

**Iterate only while the requested acceptance remains unmet and new evidence supports
another in-scope improvement**:

1. After applying and verifying a fix, go back to **Phase 1** with the updated binary.
2. Collect fresh 1-core and N-core profiles.
3. Identify the new top jumper.
4. Update the Phase 7 report with the new iteration's findings (add the next
   "Iteration N" section and update the Solutions section).
5. Stop optimization when acceptance is met; profile thresholds alone are not a
   requirement to eliminate every remaining hotspot. If a real resource limit or
   blocker prevents acceptance, report the achieved result and outstanding gap.

Note: the ordering of the remaining bottlenecks may change after each fix — a function
that appeared minor before may become the new dominant issue. Do not assume the Phase 1
list from the first iteration is still valid.

**Before claiming the requested scaling improvement**, compare the changed binary
against the relevant baseline core counts. This is part of verification, not a new
approval step. Reuse current matching results and omit extra sweep points that would
not change acceptance. Record unavailable measurements rather than claiming success.

Then proceed to **Phase 7 — Final report**.

---

## Phase 7 — Final report

Retain each accepted iteration's evidence and update a requested report as work
progresses. Do not repeatedly print the full report or create a living document for
a short task that only needs a concise result. Distinguish proposed changes from
implemented and verified ones.

Keep a requested report file current and return its path with the final result.
Otherwise summarize in chat; do not force a separate save-confirmation turn.

**If a graphing skill is available** (check the session context), note it to the user
after printing the sweep table:
> *"A graphing skill is available — ask me to plot the scaling curves if you'd like a chart."*

Do not offer this note if no graphing skill is present, and do not generate CSV
unprompted. If the user asks for a graph (in this prompt or any follow-up), use the
graphing skill if available; otherwise generate a CSV file with the format:

```
cores,baseline_score[,optimized_score]
1,12.3
2,22.1
...
```

### Report template

Use this template for a full report, trimming it to the requested depth. Omit sections that have no data (e.g., omit the scaling
table if Phase 0 was skipped; omit "Optimized" columns if no second sweep was done).

````markdown
# CPU Scaling Report — <workload>

## Scaling sweep
<!-- Only include if Phase 0 was performed -->

| Cores | Score (baseline) | Score factor | Scaling factor | Score (optimized) | Improvement |
|-------|-----------------|--------------|----------------|-------------------|-------------|
|     1 | 12.3 X          |       1.00×  |             —  | 18.1 X            |      +47%   |
|     2 | 22.1 X          |       1.80×  |    0.90×/core  | 34.5 X            |      +56%   |
|    20 | 71.0 X          |       5.77×  |    0.29×/core  | 148.2 X           |     +109%   |

Omit the "Score (optimized)" and "Improvement" columns if no post-fix sweep was done.

<!-- If graphing skill available and user has asked for a graph, embed it here -->

## Iteration <N> — Key functions
<!-- One such section per iteration; N starts at 1 -->

### Dual-profile table

<!-- Phase 1 delta table for this iteration; bold the jumper rows -->

| N-core rank | Function | N-core % | baseline rank | baseline % | Rank Δ | % Δ |
|-------------|----------|----------|---------------|------------|--------|-----|
| **1**       | **`spin_lock`** | **12.3%** | **8** | **2.1%** | **▲7** | **+10.2%** |

### Jumper function details

One subsection per jumper function. Use the annotation conventions from Flow C
(≤ 20 lines: show full body; > 20 lines: summarize around hot lines).

Annotate the hot line with the specific contention marker:

| Bottleneck type | Marker |
|-----------------|--------|
| False sharing / true sharing (c2c) | `/* ◄ cache contention */` |
| Lock / CAS spin | `/* ◄ lock CAS */` |
| Atomic counter increment | `/* ◄ atomic counter */` |

#### `<function_name>` — `path/to/file.c:<line>`

```c
void long_function(struct foo *s)
{
    ...
    s->hit_count++;   /* ◄ atomic counter */
    ...
}
```

### Diagnostic results

Summarize the Phase 3–4 findings for this iteration: which cache lines were hot,
what sharing type was identified, and which resolution strategy was selected.

## Solutions

One subsection per proposed or implemented fix, across all iterations.

### Proposed: <short description>   <!-- or: Implemented: <short description> -->

Provide a detailed description of the proposed or implemented change, including:
- What was changed (struct, function, file)
- Why it addresses the bottleneck
- Code diff or before/after snippet
- Verification result (`perf c2c` HITM drop, throughput improvement)

Update the subsection header from `Proposed:` to `Implemented:` once the fix is applied.
````
