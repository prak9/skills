# pstack harness trees

This folder is generated from `pstack/` and `adapters/antigravity.md`. Do not edit it by hand.

- Cursor uses `pstack/` directly.
- Claude Code installs `claude-code/`.
- Antigravity installs `antigravity/`.

Each harness tree leaves out Cursor-only directories such as `pstack/automations`. A relative link to a pstack file that a tree leaves out points at that file on GitHub `main` instead.

After syncing `pstack/` or editing `adapters/antigravity.md`, run `node scripts/generate-pstack-harness-trees.mjs` from the repository root and commit the result.
