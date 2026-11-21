---
name: recall
description: Reconstruct recent working context from local conversation transcripts (Antigravity CLI, Codex, Claude Code), live git state, and the shared record (PRs, issues, docs, incidents), then hand back a tight current-state brief. Use for "recall my work on X", "catch me up", "where did I leave off", or before starting/resuming related work.
---

# Recall

Before starting or resuming work, rebuild the user's recent working context and hand back a tight capsule of where things stand now and what to do next. Keep it tight and on-topic—read only what in-scope threads need, then stop.

## Two Records

Your context lives in two places:
1. **Chat history** (local transcripts): what you did, decided, struggled with, and left open.
2. **Shared record** (git, PRs, issues, docs, error trackers): everything that happened around the same code under other names—symptoms users keep reporting, fixes that shipped and got reverted, active incidents. A feature with a long bug tail keeps most of its story there; never reconstruct it from transcripts alone.

## Workflow

1. **Classify and route.** If the user already gave a complete state capsule (paths, branch, change), use it and skip mining. Resuming one specific prior chat directly belongs to session pickup; Recall synthesizes context across recent chats and shared records.
2. **Lock scope first.** Pin the time window (default last 7 days; never quietly turn "all" into "recent N"), the topic if named, and the workspace (default the active workspace—never read unrelated projects' transcripts without being asked). State the scope back.
3. **Mine local transcripts** using the bundled CLI (`scripts/recall_sessions.py`):
   ```bash
   python3 scripts/recall_sessions.py search --days 7 --query "<keywords>" --json
   python3 scripts/recall_sessions.py show <transcript_path> --max-turns 20 --json
   ```
   - Order candidates by real modification time (`mtime`), skip the current chat and obvious noise (eval/test runs), and read only relevant regions. For broad multi-session sweeps, fan out across parallel read-only subagents so raw transcripts stay out of the main thread.
4. **Sweep the shared record** whenever the topic names a feature, file, subsystem, area, or bug (skip only for pure activity recall like "what did I do this week"). Check `git log`, open/merged/reverted PRs, issues, docs, and available trackers for: *what is the current state, what was tried and didn't hold, and what are users still reporting?* Null results are findings; note any unavailable tool/MCP.
5. **Verify against live state.** Check surfaced branches, PRs, and commits with `git`/`gh`—transcripts are historical memory, never live ground truth. When an answer hinges on exact tool calls or errors, inspect the full transcript rather than a clipped summary.

## Output Contract

Lead with the capsule, then threads, then recurring problems, then the single next move:

- **Capsule:** at most 5 bullets stating what this work is and where it stands overall.
- **Threads:** one line per thread, prefixed with exactly one status tag: `[merged #N]`, `[open PR #N]`, `[in flight <branch>]`, `[verified, uncommitted]`, `[reverted #N]`, or `[planned, not started]`.
- **Problems:** at most 5 recurring problems, including user-reported symptoms and fixes that shipped and were reverted.
- **Next move:** the single most useful, concrete next action.

Cite chat findings by session ID and shared-record findings by source (PR #, commit SHA, issue ID, file path). Cut detail before cutting threads if the brief outgrows a screen. Strip secrets/tokens before quoting.
