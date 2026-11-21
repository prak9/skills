---
name: show-me-your-work
description: Keep a reviewable append-only TSV decision trail for long-running or unattended work (one row per decision: timestamp, phase, decision, why, evidence pointer, result). Local by default; commit when a reviewer needs the trail to trust the result. Use for /show-me-your-work, autonomous or multi-phase runs, or work a human reviews after stepping away.
---

# Show Me Your Work

Keep one canonical append-only decision log so a reviewer can audit an autonomous or multi-phase run at a glance.

## The Format

A single TSV file, one row per decision. Cells stay single-line. Evidence is a pointer, never a paragraph.

Copy `references/decision-log-template.tsv` (or let `scripts/log.sh` initialize it). Columns:

- **ts:** ISO8601 UTC timestamp.
- **phase:** the phase or workstream.
- **decision:** what was chosen or done, one line.
- **why:** the reason in plain words (no jargon tags).
- **evidence:** a pointer that proves it—commit SHA, PR #, `file:line`, or an artifact/trace/screenshot path.
- **result:** concrete outcome or predicate state (`tests green`, `reverted`, `pixel-diff 0`, `INCONCLUSIVE`, `open`).

## Logging A Row

Write each entry the way you would tell a teammate what you did—plain words, concrete actions, no AI filler.

Use `scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>`. It stamps `ts`, writes the header on first use, strips stray tabs/newlines, and prefixes cells starting with `=`, `+`, `-`, or `@` with `'` to prevent spreadsheet formula injection.

Log decision points and checkpoints, not every trivial command: a fork chosen, a unit completed with its verification result, a pivot or revert with its trigger, a blocker surfaced, or a gate fixed. For loop runs, log one row per iteration.

**Multi-run provenance (`start` rows):** a run is one agent conversation. When a new run (pickup, replacement agent, or new chat) appends to an existing log, or resumes after another run wrote to it, its first row uses phase `start`, naming the `ts` range of prior rows not written by this run, with its evidence naming this run (e.g., conversation/agent ID). Use phase `start` for nothing else.

## Where It Lives & Rules

- Working artifact by default: `decisions.tsv` in the work dir (or `.audit/<task-slug>.tsv` for concurrent efforts), kept out of git. Commit only when the work is ambitious enough that a reviewer needs the trail to trust the result.
- **Append-only:** never edit or delete history. A wrong call or inaccurate row gets a new row that supersedes it.
- Prefer evidence produced by committed scripts over hand-made one-offs.

## End-Of-Run Audit & Independent Review

1. **Transcript truth audit:** before handing back, walk this run's stretches in the log against the active conversation transcript (only the active workspace's transcript, never unrelated projects). Verify every row maps to a real action, every evidence pointer resolves and shows what is claimed, and no pivotal fork/abandonment was omitted. Correct errors by appending a superseding row—never rewrite history.
2. **Independent cross-model review (when available):** spawn a read-only reviewer subagent (preferring a different model/vendor) to scan the TSV trail and transcript for weak/absent evidence, skipped verification, risky hindsight choices, or gaps a human would miss on a skim.
3. **Attention block:** end the final reply with an `Attention` section naming the reviewer (`reviewed by <model>` or stating if skipped) and listing specific flagged rows/moments (`No flags` is valid).

## Reviewing & Composing

GitHub renders committed TSVs as tables; `column -s$'\t' -t decisions.tsv` renders cleanly in a terminal. Other skills may route their audit trail here by name instead of inventing a parallel log format.
