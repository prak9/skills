# Memory: <Project Name>

> Durable facts that change future planning or execution. Git and task packages already preserve ordinary change and completion history.

- Last updated: `YYYY-MM-DD`
- Program: `program.md`

## Decisions

| ID | Decision | Why | Scope | Evidence | Status |
|---|---|---|---|---|---|
| D-001 | <decision that constrains later work> | <reason> | <scope> | <source> | `active / superseded` |

## Findings

Use this table for implementation facts, invariants, failures, reusable knowledge, and learned preferences.

| ID | Finding | Applies when | Boundary / counterexample | Evidence | Status |
|---|---|---|---|---|---|
| F-001 | <durable finding> | <trigger or scope> | <when it does not apply> | <source> | `active / superseded / pending` |

## Runs

Record only Loop attempts, migrations, rollouts, rollbacks, or other consequential operations. Link raw logs rather than copying them.

| ID | Time | Scope | Action | Result | Evidence | Next |
|---|---|---|---|---|---|---|
| RUN-001 | `YYYY-MM-DD` | <scope> | <action> | `passed / failed / partial / blocked` | <log or check> | <next or none> |

## Update Rules

- Add an entry only when it will change a future decision or avoid repeated investigation.
- Prefer one entry with a type-appropriate ID over parallel changelog, history, failure, and preference copies.
- Mark superseded entries with a pointer instead of deleting them.
