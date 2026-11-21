# Hardening Playbook

## 1. Mining Commands

Start from real repo history rather than hypothetical risks:

```bash
git log -n 40 --oneline
git log --grep="revert\|fix\|hotfix\|workaround" -n 30 --oneline
git grep -nE "eslint-disable|@ts-ignore|@ts-expect-error|type: ignore|noqa|do not remove|DO NOT REMOVE|HACK|WORKAROUND"
```

Cluster findings by **mechanism** (e.g., "unvalidated boundary input", "direct DB call bypassing service layer", "allocation in hot loop"), not by file name.

## 2. Actionable Lint Error Format

A lint rule designed for coding agents must be self-correcting in one turn. Include four elements in every diagnostic:

```text
[RULE_ID][ERROR|WARN] <file>:<line> — <what invariant was violated>
  Why: <concrete failure mode or architectural boundary>
  Fix: Use <exact module/type/function path> instead (see <reference file>).
  Escape: Inline suppression requires reason + expiry + owner approval.
```

- Use `WARN` for soft thresholds (e.g., module cohesion/size prompts) and `ERROR` for hard architectural invariants.
- Never emit vague messages like `"forbidden import"` or `"bad pattern"` without naming the replacement API.

## 3. Ratchet (Diff-Only) Adoption Pattern

When legacy code violates a new rule:
1. Enforce `ERROR` on files/lines touched in `git diff <base>...HEAD` (or on designated suffixes like `*.hot.ts` for zero-allocation hot paths).
2. Optionally track legacy violation count with a monotonic ceiling (`current <= baseline`) so debt can only shrink.
3. Never weaken the rule globally just to avoid touching legacy files.

## 4. Red-Before-Green Verification

Before landing any new lint rule, type constraint, or architectural check:
1. Run it against a historical bad commit (`git show <bad_sha>:<path>`) or a minimal test fixture reproducing the exact past bug.
2. Confirm it fails with the expected diagnostic and replacement guidance (**RED**).
3. Run it against the fixed code and confirm it passes (**GREEN**).

## 5. Prose-to-Machine Rule Ledger

Keep a compact table (in `AGENTS.md` or a linked doc) only while migrating rules out of prose:

| Failure Class | Old Prose Rule | Enforced By | Status |
|---|---|---|---|
| Direct fetch bypassing client | "Always use `apiClient`" | `lint-arch.sh` (`NO_RAW_FETCH`) | Enforced → prose deleted |
| Suppressing TS errors | "Avoid `@ts-ignore`" | CI `no-ts-ignore` diff check | Enforced → prose deleted |

Once a row reaches `Enforced → prose deleted`, remove the prose instruction immediately so agent context stays focused on judgment calls machines cannot enforce.
