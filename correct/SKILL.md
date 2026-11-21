---
name: correct
description: Turn recurring coding defects, reverts, review interventions, and crutch comments into permanent architectural, type, lint, or test guardrails; also audit diffs for workaround/suppression comments and prune obsolete prose rules. Use for /correct or when hardening a codebase after repeated mistakes, not for routine one-off bug fixes or generic code review.
---

# Correct

Every repeated manual intervention is a system design signal. Assume every contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Design the repo so a change that looks right from one file is right for the whole repo—and delete prose rules once machines enforce them.

## Scope Gate

Use this skill when:
- mining recent commits, reverts, PR reviews, agent instruction files, or workaround comments for recurring failure modes (`>= 2` instances, or one high-consequence systemic failure);
- converting an identified mistake class into permanent codebase guardrails; or
- auditing a diff or module for crutch comments and suppression directives (`no-comments` submode).

Do not invent lint rules for one-off typos or speculative edge cases.

## Hardening Hierarchy (Inverted Pyramid)

Always harden at the highest feasible layer—never default to adding prose to `AGENTS.md`:

1. **Architecture / data structure** — give each piece of state one owner and each task one supported way; hide internals so the wrong import fails; replace hand-synced lists with one source of truth; delete old ways and dead code an agent would copy.
2. **Type system / schema** — make bad states unrepresentable at compile/validation time with zero runtime escape hatches.
3. **Lint / static check in CI** — if bad code still compiles, add a lint/CI check whose error names the exact file, type, or function to use instead. If the pattern is already common in legacy code, fail only when a change adds more.
4. **Targeted regression test** — test the behavior when static checks cannot express it; fix or delete any test that still passes when the behavior breaks, or fails when only internals change.
5. **Prose instruction** — last resort, only for judgment calls. Nothing fails when an agent skips prose.

## Workflow

1. **Harvest recurring failures.** Inspect recent `git log`, `revert` commits, PR review threads, `AGENTS.md`/`CLAUDE.md`, and workaround comments (`TODO`, `HACK`, `do not remove`, `eslint-disable`, `@ts-ignore`, `noqa`). Group mistakes into classes; a class counts once it has happened twice (or once for a high-consequence systemic failure).
2. **Fix the most frequent classes now (one commit each).** Test layers 1 → 5 in order and follow [the hardening playbook](references/hardening-playbook.md):
   - **Actionable error message:** state what failed AND name the exact file, type, helper, or API to use instead.
   - **Ratchet legacy code:** enforce strictly on added/changed lines or new files when legacy debt is widespread.
   - **Red-before-green proof:** prove each new check fails on a real past mistake commit or faithful reproduction before passing on the fixed code; run the exact same command locally and in CI.
   - **Scoped exceptions:** exceptions go on the offending line with a concrete reason, an expiry date, and human approval.
3. **Maintain and prune the rule table.** Keep a table in the agent instruction file pairing each rule with what enforces it. When corrected, fix the mistake and add the rule. **If the rule was already there and nothing enforces it, that is a repeat—fix it at the highest level in the same change.** Drop a prose rule once its mistake can no longer happen.

## `no-comments` Audit Submode

When asked to audit comments in a diff or subsystem:
- Treat suppression directives (`eslint-disable`, `@ts-ignore`, `type: ignore`, `noqa`) and workaround/constraint comments (`do not remove`, `must call X before Y`) as guilty until proven necessary.
- Convert constraint comments into types, runtime assertions, tests, or lint rules; remove comments that merely narrate obvious code or excuse bad structure.
- Keep comments that document genuine non-obvious external constraints (hardware quirks, vendor API bugs, regulatory/protocol invariants) that cannot be expressed in code.

## Deliverable

Report each mistake class with its evidence, the hardening level picked, why a higher level did not work, red-before-green verification output, and any prose rules deleted.
