# Program: <Project Name>

> Lite current-state plan for one or two focused sessions. Use exactly one concrete value for every choice field.

- Overall status: `<待开始 / 进行中 / 阻塞 / 待验收 / 完成 / 已取消 — choose one>`
- Profile: `Lite`
- Plan mode: `Linear`
- Execution readiness: `Blocked`
- Memory: `memory.md / None`
- Active task package: `tasks/TASK-NNN-<slug>.md / None`
- Task output root: `tasks/output/` (gitignored)
- Active plan node: `NODE-NNN / None`
- Latest evidence: `<V-NNN, RUN-NNN, command output, or None>`
- Owner: `<name or role>`
- Last updated: `YYYY-MM-DD`

## Concept Refinement

Use `None: <clear spec or accepted source>` when divergent refinement is unnecessary.

| Field | Content |
|---|---|
| Source | <request, issue, spec, or code context> |
| Problem statement | <one-sentence problem> |
| Target user | <specific user or system actor> |
| Success criteria | <observable outcome> |
| Direction | <chosen approach and why> |
| Non-goals | <what this round excludes> |

## Execution Readiness Gate

Keep `Blocked` while material judgment is unresolved. Set `Ready` only after every field is concrete. For a clear directly verifiable spec, set `Not required` and replace the table with `N/A: <concrete reason>`.

| Field | Content |
|---|---|
| Decision this work informs | <what action changes after pass or fail> |
| Claim / hypothesis | <falsifiable statement> |
| Baseline / counterfactual | <comparison or null> |
| Evidence / data quality | <source, generation, freshness, leakage, gaps> |
| Real constraints | <cost, capacity, time, scale, safety, compatibility> |
| Pass condition | <pre-registered decision threshold> |
| Falsifier / stop condition | <evidence that kills, pauses, or redirects> |
| Cheapest informative check | <smallest belief-changing test> |
| False-positive loop | <tempting output that adds no information> |
| Human judgment retained | <domain decision AI must not silently make> |

## Problem Definition

<Current problem, why it matters, constraints, and non-goals.>

## Goals And Metrics

### Acceptance Criteria

| ID | Acceptance criterion | Verification method | Pass condition |
|---|---|---|---|
| A-001 | <observable result> | <test, command, or manual check> | <clear condition> |

## Implementation Plan

### Node Status

| Node | Status | Task package | Evidence |
|---|---|---|---|
| NODE-001 | `待开始` | `tasks/TASK-001-short-slug.md` | <evidence or None> |

### Node Details

| Node | Size | Dependencies | Acceptance | Updated |
|---|---|---|---|---|
| NODE-001 | `Small / Medium — choose one` | `None` | `A-001` | `YYYY-MM-DD` |

## Current Status

- Current blocker: <None, or blocker and unblock condition>
- Next step: <task package and atomic node>
- Next human decision: <None, or decision point>
- Pending memory write: <None, or durable finding/run summary to record>
