# Program: demo-cli CSV export

- Overall status: `进行中`
- Profile: `Full`
- Plan mode: `Linear`
- Loop state: `Not applicable`
- Loop iteration: `Not applicable`
- Memory: memory.md
- Active task package: `tasks/TASK-001-add-export.md`
- Task output root: `tasks/output/` (gitignored)
- Active plan node: `NODE-001`
- Next plan node: `None`
- Latest evidence: RUN-001
- Next checkpoint: CP-001
- Owner / TL: x
- Last updated: 2026-07-11

## Concept Refinement

Refine raw ideas into sharp, actionable concepts worth building through structured divergent and convergent thinking.

### How It Works

- Understand & Expand (Divergent): Restate the idea, ask sharpening questions, and generate variations.
- Evaluate & Converge: Cluster ideas, stress-test them, and surface hidden assumptions.
- Sharpen & Ship: Produce a concrete markdown one-pager moving work forward.

### One-Page Brief

The request was already a clear implementation need, so no divergent ideation session was required.

| Field | Content |
|---|---|
| Raw idea / Source | Clear user request: add CSV export to demo-cli query results |
| Problem statement | How might we let report users export CLI query results to a file without changing the query flow? |
| Target user | Downstream report workflow users |
| Success criteria | `demo query --csv out.csv` writes valid CSV |
| Recommended direction | Add a small standard-library CSV exporter at the query output boundary |
| Key assumptions to validate | Query output is iterable and column names can come from row keys |
| MVP scope | exporter module, CLI flag, escaping tests, and one e2e check |
| Not doing | Excel export |
| Open questions | Memory usage for very large result sets |

## Problem Definition

### Background

CLI query results only print to the terminal. The downstream report workflow needs CSV files.

### Problem To Solve

Query results cannot be exported to a file.

### Why Now

The report workflow launches this month and depends on export.

### Non-goals

- Excel export

## Context And References

### Key Context

| ID | Type | Summary | Location / Ref | Why it matters | Freshness |
|---|---|---|---|---|---|
| CTX-001 | code | Query output function | src/query.py | Export logic attaches here | current |

### Code And Runtime Entrypoints

| ID | Entrypoint | Path / Command | Related node | Notes |
|---|---|---|---|---|
| REF-001 | Tests | pytest tests/ | NODE-001 | Full test suite |

### External References And Evidence

| ID | Source | Ref | Use | Checked date |
|---|---|---|---|---|
| REF-EXT-001 | RFC 4180 | https://www.rfc-editor.org/rfc/rfc4180 | CSV escaping rules | 2026-07-11 |

### People And Decisions

| ID | Role / Person | Scope | When to involve | Contact or record |
|---|---|---|---|---|
| OWN-001 | x | Final acceptance | Acceptance criteria changes | This file |

## Preferences And Tradeoffs

### Preferences

| ID | Preference | Type | Strength | Scope | Rationale |
|---|---|---|---|---|---|
| PREF-001 | Prefer standard library; do not add dependencies | imperative | locked | strategic | Dependencies are long-term cost |

### Tradeoffs

| Decision | Option A | Option B | Tradeoff | Choice | Negotiable? |
|---|---|---|---|---|---|
| CSV implementation | Python `csv` module | pandas | dependency cost vs convenience | `csv` module | no |

### Locked Constraints And Negotiable Space

| Area | Locked constraints | Negotiable space | Escalation rule |
|---|---|---|---|
| Dependencies | No new third-party dependency | Output column order | Ask before adding a dependency |

## Goals And Metrics

### Goals

| ID | Goal | Success metric | Baseline | Target | Data source / observation |
|---|---|---|---:|---:|---|
| G-001 | Support CSV export | Export command works and escaping is correct | 0 | 1 | pytest |

### Acceptance Criteria

| ID | Acceptance criterion | Verification method | Pass condition | Owner |
|---|---|---|---|---|
| A-001 | `demo query --csv out.csv` writes valid CSV | pytest tests/test_export.py tests/test_cli.py | Exporter and CLI tests pass | x |

## Constraints

### Hard Constraints

| ID | Constraint | Scope | Verification / monitoring |
|---|---|---|---|
| C-001 | Python 3.10+ compatibility | All code | CI |

### Risk Boundaries And Escalation

| Situation | Rule |
|---|---|
| Reversible local change | AI may proceed and record evidence |

## Strategy

### Strategy Summary

Attach a CSV writer at the query output boundary and verify the full vertical path with tests.

### Dependency And Slicing Strategy

```text
query output -> exporter module -> CLI flag -> e2e test
```

- Slice type: vertical
- Why this slice: one complete export flow is independently testable
- Early high-risk item: escaping fields with commas, quotes, and newlines

### Execution Principles

- Each task package needs independent acceptance evidence.

## Decisions

| ID | Status | Decision | Reason / Evidence | Impact | Date |
|---|---|---|---|---|---|
| D-001 | approved | Use the standard-library `csv` module | PREF-001 | NODE-001 | 2026-07-11 |

## Exploration And Hypothesis Validation

| ID | Status | Hypothesis / Unknown | Validation method | Deadline task | Pass / fail action | Evidence |
|---|---|---|---|---|---|---|
| H-001 | supported | Query output returns iterable rows | Read src/query.py and verify in REPL | TASK-001 | Confirmed; implement directly | F-001 / `src/query.py` REPL check |

### Exploration Plan

None. The assumption was closed through code reading; evidence is in memory.md F-001.

## Implementation Plan

### Overview

One task package delivers and verifies CSV export.

### Architecture Decisions

- Keep CSV logic in a small exporter module so it can be unit tested.

### Plan Dependency Graph

```text
NODE-001 CSV export（进行中）
```

### Node Status

| Node | Status | Task package | Evidence |
|---|---|---|---|
| NODE-001 | `进行中` | `tasks/TASK-001-add-export.md` | RUN-001 |

### Node Details

| Node | Size | Dependencies | Acceptance | Updated |
|---|---|---|---|---|
| NODE-001 | `Medium` | None | A-001 | 2026-07-11 |

### Loop Contract

Not applicable (Linear).

### Loop State

Not applicable.

### Memory Sync

| Type | Status | Source | memory.md location | Updated |
|---|---|---|---|---|
| Finding | written | TASK-001 | memory.md#1-important-findings | 2026-07-11 |
| Changelog | written | CHG-001 | memory.md#3-changelog | 2026-07-11 |
| Run log | written | RUN-001 | memory.md#4-run-logs | 2026-07-11 |
| History summary | pending | TASK-001 | memory.md#5-history-summaries | 2026-07-11 |

### Task List

#### Phase 1

- [ ] NODE-001 / tasks/TASK-001-add-export.md: CSV export

### Checkpoints

| Checkpoint | Position | Verification requirements | Human review |
|---|---|---|---|
| CP-001 | After NODE-001 | pytest green + manual inspection of output file | yes |

### Parallelization Opportunities

None.

### Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Incorrect escaping for commas/newlines | Medium | Use `csv` module and add escaping cases |

### Open Questions

None.

## Current Status

- Current blocker: None
- Current risk: Large exports may require a later streaming benchmark; it does not block the MVP.
- Next step: N-002 CLI flag
- Next human decision: Review the exported sample at CP-001.
- Pending memory write: None

## Update Protocol

Follow plan-skill update rules: task package status changes update Implementation Plan; history and findings go to memory.md.
