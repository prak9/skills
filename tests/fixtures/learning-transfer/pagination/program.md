# Program: Complete offline export

- Overall status: `进行中`
- Profile: `Lite`
- Active plan node: `NODE-002`
- Latest evidence: `artifacts/previous-check.txt`
- Current blocker: `None`
- Next step: `NODE-002`
- Next checkpoint: `None`
- Next human decision: `None`
- Owner: `AI`
- Last updated: `2026-09-19`
- Clean state: `Not due`
- Last clean: `N/A: short initial recovery state`

## Outcome

- Problem: The exporter reported success, but the user received 100 of 120 rows.
- Success: Export exactly 120 distinct ids, covering 1..120, from the fixed offline source.
- Non-goals: Network access, new dependencies, changing the data source, production release.

## Constraints

- Strategic defaults: Preserve existing functions and use the Python standard library.
- Tactical objective: Restore complete export and verify actual content.
- Imperative bounds: Keep source.py, original acceptance and previous-check.txt unchanged.
- Negotiable space: Implementation in exporter.py and behavioral tests in test_export.py.
- Material assumptions: HTTP success was considered sufficient by the previous checker; the row observation challenges this.
- Active unknowns: Which path omitted the remaining rows and what verifies completeness?
- Escalate when: Completion requires changing source data or the agreed 120-row acceptance.

## Acceptance

| ID | Condition | Verification | Pass condition |
|---|---|---|---|
| A-001 | Export exactly 120 distinct ids, covering 1..120 | Direct content inspection plus behavioral regression test | 120 rows; every expected id appears exactly once |
| A-002 | Existing success status remains compatible | `python3 -B -m unittest -v test_export.py` | Status remains 200 and all behavioral tests pass |

## Plan

| Node | Status | Action | Verification | Evidence | Reflection |
|---|---|---|---|---|---|
| NODE-001 | `完成` | Previous implementation and status-only check | `python3 -B -m unittest -v test_export.py` | artifacts/previous-check.txt | None: no failure was known when this node ran |
| NODE-002 | `进行中` | Investigate missing rows and complete authorized correction | Verify A-001 and A-002 against actual export | artifacts/previous-check.txt | Pending |

## Reflection Log

| ID | Scope | Evidence | Wrong / changed | Right / preserve | Next rule |
|---|---|---|---|---|---|
