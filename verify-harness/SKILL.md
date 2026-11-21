---
name: verify-harness
description: Build or maintain an agent-friendly self-verification harness for a software repository—combining a compact Feature Map (user-visible features, entry points, verification commands) and a composable verification CLI. Use when setting up repeatable end-to-end verification infrastructure for a project, not for writing one-off unit tests.
---

# Verify Harness

Verification is the highest-leverage multiplier for autonomous coding agents. Prefer giving agents **repeatable tools and a concise Feature Map** over long Markdown instructions that force them to improvise fragile one-off scripts every session.

## Scope Gate

Use when a repository is iterated on frequently and agents repeatedly struggle with setup, auth, seeding test state, driving UI/API flows, or capturing proof (logs, screenshots, traces). Skip for tiny single-file scripts where a standard test command already gives full end-to-end confidence.

## Two Core Assets

### 1. Agent-Friendly Verification CLI
Wrap repetitive operational and verification steps (start/stop, seed fixtures, auth, trigger flows, inspect state, capture screenshots/traces) into one small repo-local CLI (e.g., `scripts/verify` or `tools/devctl`). Follow all six design standards (details in [CLI & Feature Map guide](references/cli-and-feature-map.md)):

1. **Deep, composable modules** — high-level subcommands that hide plumbing while remaining pipeable.
2. **`--dry-run` on destructive/mutating commands** — safe preview before touching state or external systems.
3. **Progressive disclosure via subcommands** — group capabilities logically (`auth`, `seed`, `run`, `inspect`) instead of one flag-soup entrypoint.
4. **Self-correcting error messages** — on failure, print the concrete cause AND the exact next command or fix the agent should run.
5. **Rich `--help`** — concise examples and expected outputs right in CLI help so agents self-discover without reading source.
6. **Machine-readable output (`--json`)** — stable structured stdout for assertions and parsing, keeping diagnostics on stderr.

### 2. Feature Map (Materialized Repo Memory)
Generate and maintain a lightweight `references/features/` index (or `docs/feature-map.md` in the target repo) mapping:
- Each user-visible feature or critical workflow;
- How a user/caller reaches it (URL/route, CLI command, API endpoint, owning files);
- The exact verification command and observable pass signal (stdout JSON, HTTP check, screenshot, trace).

This gives future agents immediate orientation at minimal token cost.

## Workflow

1. **Audit verification friction.** Identify where agents currently burn turns or fail to prove changes (server startup, auth tokens, DB fixtures, browser driving, log inspection).
2. **Design the minimal CLI surface.** Pick the smallest subcommand set that closes the real end-to-end loop; verify it uses existing repo runtimes (Python/Node/Bash) with zero unnecessary dependencies.
3. **Implement and dogfood.** Build the CLI, test `--help`, `--dry-run`, `--json`, and at least one intentional failure path to verify the error message actually guides recovery.
4. **Generate/refresh the Feature Map.** Scan routes, entry points, and tests to populate the map; verify every listed command actually runs.
5. **Document maintenance.** Define the lightweight trigger for updating the Feature Map and CLI whenever a new feature or flow lands.

## Deliverable

Deliver the working CLI, Feature Map, and a real end-to-end verification run proving an agent can reproduce and verify a representative workflow in one command.
