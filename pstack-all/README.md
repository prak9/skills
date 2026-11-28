# pstack-all

Standalone mirror of [`cursor/plugins/pstack`](https://github.com/cursor/plugins/tree/main/pstack) with multi-harness plugin distributions for **Cursor**, **Claude Code**, and **Google Antigravity**.

## Structure

- [`pstack/`](./pstack/) — verbatim standalone sync of `cursor/plugins/pstack` (Cursor-native).
- [`adapters/antigravity.md`](./adapters/antigravity.md) — harness adapter mapping Cursor tools, subagents, model tiers, rules, and paths to Antigravity.
- [`harness/pstack/antigravity/`](./harness/pstack/antigravity/) — generated Google Antigravity plugin (`.antigravity-plugin/plugin.json`, `plugin.json`, `skills/`, adapted `agents/`, `assets/logo.png`, `docs/harness/antigravity.md`, `docs/guide/`).
- [`harness/pstack/claude-code/`](./harness/pstack/claude-code/) — generated Claude Code plugin.
- [`scripts/sync-pstack.mjs`](./scripts/sync-pstack.mjs) — sparse-clones `pstack/` from `cursor/plugins`, records [`.pstack-upstream.json`](./.pstack-upstream.json), and regenerates all harness trees.
- [`scripts/generate-pstack-harness-trees.mjs`](./scripts/generate-pstack-harness-trees.mjs) — validates adapter coverage & links and generates both `claude-code` and `antigravity` trees (`--check` for CI).

## Install

### Antigravity

Using the Antigravity CLI:

```bash
git clone https://github.com/qiwihui/pstack-all.git
agy plugin install ./pstack-all/harness/pstack/antigravity
```

Or using the included installer script (no `agy` CLI required):

```bash
# Global install (~/.gemini/config/plugins/pstack)
./scripts/install-antigravity.sh

# Workspace install (<repo>/.agents/plugins/pstack)
./scripts/install-antigravity.sh --workspace /path/to/your/repo

# Symlink for local development
./scripts/install-antigravity.sh --symlink
```

Once installed, start a new Antigravity session and run `/setup-pstack` or `/poteto-mode`.
In Antigravity, `/setup-pstack` writes your model tier overrides to `~/.gemini/config/rules/pstack-models.md` with `trigger: always_on` frontmatter, and every skill with Cursor-specific names points to [the Antigravity adapter](./adapters/antigravity.md).

### Claude Code

```bash
/plugin marketplace add qiwihui/pstack-all
/plugin install pstack@pstack-all
```

### Cursor

Use `pstack/` directly (or add `qiwihui/pstack-all` as a plugin marketplace).

## Syncing from upstream

To pull the latest `pstack` from `cursor/plugins@main` and regenerate the Claude Code and Antigravity harness trees:

```bash
node scripts/sync-pstack.mjs
```

To verify generated trees are up to date (also run in CI):

```bash
node scripts/generate-pstack-harness-trees.mjs --check
```

## License

MIT (see [`pstack/LICENSE`](./pstack/LICENSE)).
