# Memory: <Project Name>

> Durable facts and node learning. Keep status in program/task state and evidence in raw sources.

- Last updated: `YYYY-MM-DD`
- Program: `program.md`

## Decisions

None yet.

## Findings

None yet.

## Runs

None yet. Record only Loop, migration, rollout, rollback, or otherwise consequential runs.

## Reflections

| ID | Scope | Evidence | Wrong / changed | Right / preserve | Next rule |
|---|---|---|---|---|---|

## Update Rules

- Use stable `D-*`, `F-*`, `RUN-*`, and `R-*` IDs with evidence.
- Store trajectory events: attempt, result, evidence, changed belief, and next rule; not coarse snapshots or token transcripts.
- Add one `R-*` for every completed atomic node and verified Loop attempt.
- Mark superseded entries with a pointer; do not duplicate ordinary progress or Git history.
- During Clean, preserve unique `R-*` feedback and stable IDs; distill repeated lessons with a pointer instead of deleting them.
