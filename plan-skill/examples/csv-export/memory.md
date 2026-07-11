# Memory: demo-cli CSV 导出

- Last updated: 2026-07-11
- Program: program.md

## 1. Important Findings

| ID | Status | Finding | Impact | Evidence | Source | Date |
|---|---|---|---|---|---|---|
| F-001 | 有效 | The query path returns an iterator of dict rows; headers can come from the first row's keys. | The exporter can consume the iterator directly without changing the query layer. | `src/query.py` read + REPL check | TASK-001 | 2026-07-11 |

## 2. Knowledge Base

| ID | Category | Knowledge | Applies when | Boundary / counterexample | Evidence |
|---|---|---|---|---|---|
| K-001 | implementation | Open CSV output files with `newline=''`; otherwise Windows can produce extra blank lines. | CSV file writing | Text mode only | `tests/test_export.py` |

## 3. Changelog

| ID | Time | Type | Scope | Summary | Trigger | Evidence | Impact |
|---|---|---|---|---|---|---|---|
| CHG-001 | 2026-07-11 | code | `src/exporter.py` | Added the exporter module. | NODE-001 | commit abc123 | Downstream flows can export CSV. |

## 4. Run Logs

| ID | Time | Scope | Type | Action | Result | Evidence | Next | Distillation |
|---|---|---|---|---|---|---|---|---|
| RUN-001 | 2026-07-11 | TASK-001 N-001 | test | Ran `pytest tests/test_export.py` with escaping cases. | passed | ci run 118 | N-002 | K-001 |

## 5. History Summaries

None yet; the first task package is still in progress.

## 6. Failures And Rework

None.

## 7. Open Knowledge Gaps

| ID | Status | Question | Why it matters | Validation method | Related plan node |
|---|---|---|---|---|---|
| Q-001 | 待验证 | Memory use for very large result exports | Reports may query full datasets | 1M-row benchmark | NODE-001 |

## 8. Preference Learning

None.

## 9. Reflection And Curation

Trigger when a task package closes or `待提炼` reaches 5. No backlog now: RUN-001 was distilled into K-001.

## 10. Update Rules

Follow plan-skill memory rules: add entries incrementally, keep evidence pointers, and mark superseded entries instead of deleting them.
