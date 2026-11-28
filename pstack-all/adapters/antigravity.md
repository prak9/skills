# pstack in Antigravity

pstack skills use Cursor names. In Antigravity, read this file once per session, then map each Cursor name in a skill with the tables below. `<pstack>` means the folder that holds `skills/` and `docs/` (for example `~/.gemini/config/plugins/pstack` or `<workspace>/.agents/plugins/pstack`). If a Cursor field has no row, drop it and say so. Never pass a field or value the tool schema rejects.

## Tools

| Cursor | Antigravity |
| --- | --- |
| `Task` | `invoke_subagent` (pass `Subagents` entries with `TypeName`, `Role`, `Prompt`, and optional `Model`/`Workspace`). Use `define_subagent` for transient custom subagents, `send_message` to message a running or idle subagent, and `manage_subagents` to list or kill subagents. |
| `AskQuestion` | `ask_question`. In headless CLI mode (`agy -p`) or when unavailable, ask in plain text. |
| Open a todolist, or copy steps into the todolist tool | Antigravity has no dedicated todolist tool. Keep the checklist in a markdown artifact or in your reply and update it at each phase. |
| Run another pstack skill (`/name` or "the **name** skill") | Call `lookup_skill` (or `lookup_skills`) with `<name>`, or `view_file` on `<pstack>/skills/<name>/SKILL.md` and follow it. When you tell the user to type it, write `/<name>` (Antigravity does not prefix plugin skill slash commands). |
| `Read`, `Write`, `StrReplace` | `view_file`, `write_to_file`, `replace_file_content`. |
| `Shell`, `Bash` | `run_command` (use `IsDaemon: true` for long-running servers, and `manage_task` for background tasks). |
| `Grep`, `Glob` | `grep_search` / `find_by_name` if available in the session, otherwise `run_command` with `rg` / `find`. |

## Subagent fields

| Cursor | Antigravity |
| --- | --- |
| `subagent_type: generalPurpose` | `TypeName: "self"` (clones the calling agent with its full toolset and permissions). |
| `poteto-agent`, `comment-sicko` | `TypeName: "poteto-agent"`, `TypeName: "comment-sicko"` (bundled in `<pstack>/agents/`). |
| The `model:` line in `poteto-agent`'s file | Antigravity's generated `agents/poteto-agent.md` sets `model: inherit`. Override with `Model` on `invoke_subagent` only when a role explicitly requires a different tier from the Models table. |
| `readonly: true` | `TypeName: "research"` (built-in read-only sandboxed subagent with no network access). If the task needs shell commands without editing files, use `TypeName: "self"`, state "do not edit files" in `Prompt`, and check `git status` afterward. |
| `readonly: false` | `TypeName: "self"` (or `TypeName: "poteto-agent"` inside a playbook step). |
| `environment: "cloud"` | `Workspace: "branch"` (isolated Git worktree) or `Workspace: "share"` when supported by the local Antigravity runtime. On remote cloud VMs where branched/shared workspaces are unsupported, use `Workspace: "inherit"` and create a git worktree manually if isolation is needed. |
| `environment: "local"` | `Workspace: "inherit"` (or omit). |
| `cloud_base_branch: <b>` | Tell the subagent in its `Prompt` to check out `<b>` first. |
| `run_in_background: true` | Omit. Antigravity subagents always run asynchronously in the background and automatically wake the parent when they report back. Never poll `manage_subagents` in a loop. |
| `resume` | Call `send_message` with the idle subagent's `conversationId` (an idle subagent automatically re-awakens and retains its prior context). If the subagent was killed or is from a prior session, spawn a fresh subagent with `invoke_subagent` and include the earlier summary or transcript path in `Prompt`. |
| `file_attachments` | List the absolute file paths in `Prompt`. |

## Models

Antigravity's `invoke_subagent` accepts a `Model` tier enum (`inherit`, `pro`, `flash`, `flash_lite`) rather than raw Cursor model slugs. Never pass a Cursor slug directly to `Model`.

| Cursor | Antigravity |
| --- | --- |
| `claude-`, `grok-`, `gpt-`, or `gemini-*` high-reasoning slugs (such as `claude-opus-5-5-xhigh-fast`, `claude-fable-5-2-high`, `gemini-4-neon-xhigh`) | `Model: "inherit"` (default when the parent session already uses a frontier model) or `Model: "pro"` when explicitly configured in `~/.gemini/config/rules/pstack-models.md`. For cross-vendor review panels (`arena`, `interrogate`), run independent subagents with distinct roles/prompts on `inherit` or `pro` and note when multi-vendor diversity is unavailable. |
| Lightweight or fast mechanical worker slugs | `Model: "flash"` (or `flash_lite` for very simple lookups), or `Model: "inherit"` by default. |
| `auto` or `inherit-parent` | `Model: "inherit"` (or omit `Model`). |
| The `pstack-models.mdc` rule, `~/.cursor/rules/pstack-models.mdc` | `~/.gemini/config/rules/pstack-models.md` with `trigger: always_on` YAML frontmatter. Antigravity loads it into every new session automatically. If the file or a role's line is missing, default to `Model: "inherit"`. |
| A role value (`inherit`, `pro`, `flash`, `flash_lite`) | Pass `Model: "<tier>"` on `invoke_subagent`. |

## setup-pstack

Antigravity loads every `.md` file in `~/.gemini/config/rules/` that declares valid YAML frontmatter (`trigger: always_on`) into each new session, so `setup-pstack` writes its rule there. Follow its steps with these changes:

- Detect. The available subagent model tiers are the `Model` enum values accepted by `invoke_subagent`: `inherit`, `pro`, `flash`, and `flash_lite`.
- Defaults. Map each role to an Antigravity tier: `inherit` (recommended default so subagents match the session model), `pro` for deep reasoning/code roles when explicitly chosen, and `flash` for fast helper/swarm workers if desired.
- Write. Write `~/.gemini/config/rules/pstack-models.md` with Antigravity YAML frontmatter (`trigger: always_on` and `description`), then the comment lines, the `# budget` line, and one line per role from step 5. Overwrite the whole file so re-runs stay idempotent. Never omit `trigger: always_on` (Antigravity silently discards rule files in `rules/` without a valid `trigger`).

```markdown
---
trigger: always_on
description: pstack per-role model tier choices for Antigravity (overrides skill defaults)
---
# pstack model configuration for Antigravity. One line per role. Delete a line to fall back to `inherit`.
# defaults: 3
# budget: large (xhigh)
feature, refactoring: inherit
bug-fix: inherit
perf-issue: inherit
hillclimb: inherit
judgment and prose: inherit
arena runners: pro, pro, pro
arena cross-judge pool: pro
swarm workers: inherit
interrogate reviewers: pro, pro, pro
```

## Paths

| Cursor | Antigravity |
| --- | --- |
| `.cursor/skills/`, `~/.cursor/skills/` | `.agents/skills/` (workspace), `~/.gemini/config/skills/` (global, shared across Antigravity App and CLI). |
| `~/.cursor/plugins/`, `.cursor-plugin/plugin.json` | `~/.gemini/config/plugins/` (global), `.agents/plugins/` (workspace), `.antigravity-plugin/plugin.json` (or `plugin.json`). |
| `.cursor/rules/*.mdc`, always-applied rules | `.agents/rules/*.md` (workspace) or `~/.gemini/config/rules/*.md` (global) with YAML frontmatter `trigger: always_on`, or `AGENTS.md` / `GEMINI.md` (plain Markdown, no frontmatter). Antigravity never reads `.mdc` files. |
| `https://github.com/cursor/plugins/blob/main/pstack/<path>` | `<pstack>/<path>` when that file exists. The plugin ships the skills, `docs/guide/`, and `README.md`. Read the local copy and never fetch it. Give the user the URL when they need a link. |
| Transcripts in `~/.cursor/projects/<slug>/agent-transcripts/` | `<appDataDir>/brain/<conversation-id>/.system_generated/logs/transcript.jsonl` (compact) and `transcript_full.jsonl` (full). Use `manage_subagents` (`Action: "list"`) to get active subagent transcript URIs. |

## Cursor-only features

Antigravity has no Cursor Automations, Bugbot, Cursor cloud agents, or Cursor's built-in PR tool. When a step needs one, put one line in your reply, `Skipped in Antigravity: <step>. <reason>.`, then go on to the next step. Do not stop, ask, or retry. When a later step needs what the skipped step made, such as a URL or a key, leave a placeholder and name it in the line.

| Cursor | Antigravity |
| --- | --- |
| Cursor Automations: routines, `update_state` routine calls, `api2.cursor.sh/automations` webhooks, routine wakes, and `SendToUser` secret requests | Skip with the line. |
| Bugbot | Bugbot comments on a GitHub PR are ordinary review threads, so triage them with the forge command (`gh`) that the step gives. Skip a step that starts, waits for, or configures Bugbot when the PR has no Bugbot check or comment. |
| Cursor cloud agents | `environment: "cloud"` maps to `Workspace: "branch"` when available (or a manual git worktree), as in Subagent fields. Skip a step that needs the Cursor cloud agent dashboard or its own remote machine. |
| A built-in PR tool | Use the forge command that the step gives, such as `gh pr create`. That is not a skip, so write no line. |
