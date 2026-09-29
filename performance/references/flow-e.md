<!-- (C) 2026 Intel Corporation, MIT license -->
# Flow E: execution steps — Hotspot analysis report

Produce a self-contained hotspot report at the requested depth. A top-functions
table and selected annotated source are useful when they explain the conclusion;
the template below is optional, not a fixed report-size or formatting contract.

---

## Phase 0 — Ensure debug symbols

Run [Building block: Ensure debug symbols](building-blocks.md#building-block-ensure-debug-symbols) on the binary before recording.
Complete an authorized rebuild before Phase 1 so recording and annotation use the
same binary. Otherwise note the limitation and use the Phase 4a assembly fallback.

---

## Phase 1 — Record

Use [Building block: perf record](building-blocks.md#building-block-perf-record)
when new collection is needed. Note the workload duration to judge the cost of
additional evidence, not as an automatic trigger to rerun it.

Reuse existing `perf.data` when its workload, binary, and collection scope match.
Inspect metadata before asking; re-record only when current evidence is insufficient
and collection is authorized.

Call graphs are not required for this flow (percentages come from annotate, not call
chains), but if the user has already recorded with `--call-graph dwarf`, that data can
be reused.

---

## Phase 2 — Perf stat (conditional)

Reuse existing counters when workload, binary and event scope match. Collect new
`perf stat` evidence only when it can change the interpretation and fits the
authorized runtime/resources; otherwise state the material measurement gap.

**If perf stat data is available**, format it as a compact summary table followed by
one sentence describing the performance regime:

```markdown
## System-level summary

| Metric              | Value  |
|---------------------|--------|
| IPC                 | 0.62   |
| Cache-miss rate     | 67.3%  |
| Branch-miss rate    | 1.2%   |
| CPU time            | 4.21 s |

*Low IPC and frequent cache misses suggest investigating memory access costs;
the counters alone do not establish the limiting mechanism.*
```

State a performance regime only when the workload, architecture, event definitions
and corroborating evidence support it. IPC/miss-rate thresholds are not portable
diagnoses; a large kernel share does not distinguish CPU kernel work, syscall
overhead, waiting or I/O. Name an unresolved hypothesis instead of forcing a label.

---

## Phase 3 — Top functions table

Use [Building block: Top-N functions](building-blocks.md#building-block-top-n-functions) to get the ranked function list.

Select functions that explain the material costs or unresolved mechanism, honoring
an explicit requested count. Do not hide a distributed cause behind a fixed
top-five, 5% or cumulative-95% cutoff. State what the selected view omits.

**Location column**: show the function's **definition line** (not the hottest line).
Obtain from `perf report` output or `addr2line`. If unavailable, show `<binary>` or
`<stripped>`.

**Percentage**: round to nearest whole percent.

```markdown
## Top functions

| Rank | Function     | Location      | % |
|------|--------------|---------------|---|
|    1 | `foo(int)`   | src/foo.c:91  | 79% |
|    2 | `bar(void)`  | src/bar.c:21  | 19% |
```

---

## Phase 4 — Per-function detailed sections

Add a detailed section only where source or instruction evidence helps the
reader judge the conclusion; a row in the top table does not itself require one.

### Step 4a — Get annotated source

Run `perf annotate` in source mode for each function:

```bash
perf annotate --stdio -l -s <function_name> 2>/dev/null
```

This outputs source lines interleaved with assembly, with per-line percentages that
are **relative within the function** (they sum to approximately 100%). Use the
source-line percentages for the report; use the assembly lines for Observations (4d).

If source lines are not available (stripped binary or missing `-g`), show the annotated
**assembly** instead, preserving event percentages and addresses. Add a note above the block:

> ⚠️ *Binary has no debug symbols — assembly view shown. Source is available at `<path>` if known.*

Assembly fallback format: show the hot inner loop(s) with a few instructions of context
before and after; mark omitted sections with `...`. Add instruction comments only
when needed to explain the mechanism. Do not omit cold paths that are material
to the conclusion.

Example assembly fallback:

```asm
      ; <function_name> — inner loop (source unavailable)
      ...
   36%  :   3b30:   vmovupd (%rbx,%rdi,1),%ymm0    ; load C[j]
   44%  :   3b35:   vfmadd213pd (%rax,%rdi,1),%ymm2,%ymm0  ; C += a_val * A
   14%  :   3b3b:   vfmadd231pd (%r9,%rdi,1),%ymm1,%ymm0   ; C += a_val2 * B
    5%  :   3b41:   vmovupd %ymm0,(%rax,%rdi,1)    ; store C[j]
         :   3b46:   add    $0x20,%rdi
         :   3b4d:   jne    3b30                   ; loop back
      ...
```

### Step 4b — Short vs long function

Show a whole function when it is the clearest compact explanation; otherwise use
an excerpt. Line count alone does not determine how much context is necessary.

### Step 4c — Summarization strategy

Show a condensed view that keeps the most relevant context and hides the rest.

**Keep the context needed to understand the mechanism, such as:**
1. **Function signature and opening brace** (no percentage needed even if % > 0 there)
2. **Variable definitions** for any variable that appears in a hot line — helps
   the reader understand the hot expression without needing to scroll elsewhere
3. **Closing `}`**

**For a material hot line, useful context includes:**
- 1–2 lines of context **before** the hot line
- The hot line itself
- 1–2 lines of context **after** the hot line
- If the hot line is inside a loop, show the **loop header** as well — loops
  amplify the per-iteration cost and are essential context

**Merging**: if the context windows of two adjacent hot regions overlap, merge them
into a single continuous block (no `...` between them).

**Omitted code**: mark it with `...`; do not invent percentages for omitted/context lines.

### Step 4d — Percentage column format

Use a legible percentage column without a fixed character-position requirement.
Name the measured event and whether shares are within-function or whole-profile;
do not call them cycles when another event was sampled. Preserve source
indentation, and choose precision that does not hide material low-frequency work.
The following layouts are examples, not mandatory output.

Example (long function, summarized):

```c

      void foo(int a)
      {
          int loop;
          double counter = 0;
          ...
          for (loop = 1; loop < a; loop++) {
              ...
   4%         do_something_else();
  95%         counter += exp(memory[loop]);
              ...
          }
          ...
      }

```

Example (short function, shown in full):

```c

      void bar(void)
      {
          int loop;
          double counter = 0;

          for (loop = 1; loop < 5000; loop++) {
 100%          counter += exp(memory[loop]);
          }
      }

```

### Step 4e — Observations

Run [Building block: Annotate pattern scan](building-blocks.md#building-block-annotate-pattern-scan) on the assembly output from Step 4a.
Present each detected pattern as a bullet — include the **Pattern** name and **Evidence**;
omit the Suggested RS column (this is a reporting flow, not a prescriptive one).

If no patterns are detected, omit this section.

For a report-only request, describe supported observations without editing code.
If this report is part of a broader fix/optimize task, return its evidence to that
workflow and continue the already-authorized implementation and verification.

---

## Phase 5 — Output and save

Deliver the requested report in Markdown without duplicating a long artifact in
the terminal solely to satisfy a template.

If a file was requested, write it to the specified destination or a clearly named
local output file and return the path. Otherwise deliver in chat without a mandatory
save prompt. External publication remains governed by its own authorization.

---

## Report template

````markdown
# Hotspot report for `<appname>`

Hotspot analysis was performed using the command: `<full command line>`

## System-level summary

| Metric              | Value  |
|---------------------|--------|
| IPC                 | X.XX   |
| Cache-miss rate     | XX.X%  |
| Branch-miss rate    | X.X%   |
| CPU time            | X.XX s |

*<one-sentence regime description>*

---

## Top functions

| Rank | Function     | Location      | %   |
|------|--------------|---------------|-----|
|    1 | `<function>` | `<file>:<line>` | XX% |
|    2 | `<function>` | `<file>:<line>` | XX% |

---

### Function 1: `<function>` detailed report

```c

      <annotated source with % column>

```

**Observations:**
- <pattern, if any>

---

### Function 2: `<function>` detailed report

```c

      <annotated source with % column>

```

---
````
