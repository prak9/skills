---
name: recall
description: Recover recent work, decisions, open threads, and file paths from local coding-agent conversation transcripts (Antigravity CLI, Codex, Claude Code). Use when resuming multi-day work across chats or pulling prior context before starting a related task; do not treat old transcript claims as live repo truth without checking current files.
---

# Recall

Pull high-density context from recent local session transcripts so a fresh conversation resumes immediately without re-explaining prior work.

## Scope Gate

Use when the user asks to recall prior sessions, yesterday's work, recent debugging/design context, or decisions made in earlier chats. Read-only recovery—does not modify transcripts or authorize code changes.

## Workflow

1. **Search recent transcripts** using the bundled CLI (`scripts/recall_sessions.py`):
   ```bash
   python3 scripts/recall_sessions.py search --days 7 --query "<keywords>" --json
   ```
   - Supports `--source all|antigravity|codex|claude`, `--days N`, `--query "..."`, and `--limit N`.
   - When `--query` is omitted, returns the most recently updated sessions within `--days`.
2. **Inspect the most relevant session(s)** without dumping raw noise into context:
   ```bash
   python3 scripts/recall_sessions.py show <transcript_path> --max-turns 20 --json
   ```
   - Read only the turns relevant to the requested topic; avoid loading full multi-megabyte logs verbatim.
3. **Reconcile against live repo state.** Transcripts are historical memory, not live ground truth. Before acting on recalled facts, check `git status` / `git log -n 5` or the referenced files to confirm whether code changed since that session.
4. **Synthesize a compact Recall Brief:**
   - **Matched sessions:** timestamp, runtime (`antigravity`/`codex`/`claude`), session ID/path, and workspace (`cwd` if recorded).
   - **What was done & verified:** concrete changes, commits, or test results actually observed.
   - **Key decisions & tradeoffs:** why a route was chosen or rejected.
   - **Open threads / next step:** unresolved bugs, blockers, or follow-ups left over.
   - **Key files:** clickable file paths referenced in the session.

## Guardrails

- Never fabricate missing history; if no matching transcript exists within the window, say so and suggest widening `--days` or trying alternate keywords.
- Strip secrets/tokens if any accidentally appear in raw transcript excerpts before quoting them.
