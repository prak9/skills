<!-- (C) 2026 Intel Corporation, MIT license -->
# Flow B: execution steps

### Phase 0 — Ensure debug symbols

Before a new recording that needs source annotation, use [Building block: Ensure debug symbols](building-blocks.md#building-block-ensure-debug-symbols). Preserve optimization flags and defines when adding `-g`, and re-record after rebuilding so annotation uses the same binary. If rebuilding is unavailable or outside scope, retain the assembly-only limitation and continue. Matching existing profiles need no new recording solely to follow this flow.

### Phase 1 — Record

Use [Building block: perf record](building-blocks.md#building-block-perf-record).

Include call graphs when caller attribution matters and the recording overhead fits the task. Select `--call-graph dwarf` or a supported lower-overhead unwinder; do not ask the user to choose an ordinary diagnostic flag.

### Phase 2 — Report

```bash
perf report --stdio --no-header -F+srcfile -F+srcline | head -100
```

Key columns: **Overhead**, **Source:Line**, **Command**, **Shared Object**, **Symbol** (`[k]` = kernel, `[.]` = userspace).

**If symbols show as raw addresses**: check the matching binary/debug-symbol availability. Use an authorized symbol build and new recording when needed, or [Building block: resolve address to source](building-blocks.md#building-block-resolve-address-to-source); do not claim a source mapping that could not be recovered.

### Phase 3 — Interpret

Treat these as investigation leads, not diagnoses from sample percentages alone.

- **Large kernel sample share** → distinguish CPU work inside the kernel from syscall overhead, lock waiting and I/O using the relevant stacks, event scope and wait/time evidence. A high `[k]` percentage alone does not establish I/O or syscall limitation; use `strace -c` only when syscall activity is the supported next question
- **malloc/free/new/delete dominates** → allocation-heavy; consider object pools or arena allocators
- **No clear hotspot (< 5% per function)** → well-distributed; look for parallelism or algorithmic improvements
- **One function has a large sample share** → inspect whether its work is material and avoidable; use Phase 4 when instruction/source attribution can change the next decision
- **Many small kernel helpers** (`copy_to_user`, `mutex_lock`) → inspect copy volume, lock wait/hold evidence and callers before attributing the cost to contention or syscall overhead
- **Spinlock / CAS wrappers prominent** (`spin_lock`, `cmpxchg`, `try_lock`, `cas`) → possible Test-and-Set spin pattern; proceed to Phase 4 to confirm `lock cmpxchg` clusters, then apply [Test-and-Test-and-Set](../patterns/ttas.md)

### Phase 4 — Drill-down with `perf annotate`

Use [Building block: perf annotate (assembly view)](building-blocks.md#building-block-perf-annotate-assembly-view) when instruction-level evidence can confirm/refute the leading mechanism or guide an authorized change. A sample percentage such as 20% is a prioritization hint, not an automatic requirement to run more commands. Reuse matching annotation; if the binary is stripped, use [Building block: resolve address to source](building-blocks.md#building-block-resolve-address-to-source) where possible and state the remaining limitation.

When an instruction pattern needs diagnosis, use [Building block: Annotate pattern scan](building-blocks.md#building-block-annotate-pattern-scan) and the relevant row in [triggers/from-profile.md](../triggers/from-profile.md). Read only the matching pattern; a suggested resolution is a hypothesis, not proof that the source must be changed.

After a SIMD fix, verify the intended instructions and comparable workload
performance while checking correctness. Probe supported events first:

```bash
perf list
```

Select relevant events actually supported by this CPU/PMU and permitted in this
environment. On a matching Intel PMU these may include
`fp_arith_inst_retired.scalar_double`, `fp_arith_inst_retired.256b_packed_double`
and `fp_arith_inst_retired.512b_packed_double`; they are not portable requirements.
Check event units, scope and multiplexing before comparing counts. Missing,
unsupported or permission-denied counters are not evidence that vectorization
failed. Use matching disassembly/compiler diagnostics for code generation and a
same-workload benchmark for impact when those counters are unavailable; report
which mechanism or runtime attribution remains unverified. SIMD instructions or
nonzero packed-operation counts alone do not prove an end-to-end speedup.

**Note for Scalar FP pattern**: the most common vectorization blocker is a **strided inner loop** — pointer arithmetic of the form `base + k*stride` where stride is large (e.g., `N*8` bytes for a row-major matrix column access). The fix is a **loop reorder** to make the innermost loop stride-1 — then rebuild and re-run the annotate pattern scan to confirm SIMD is now active.

---
