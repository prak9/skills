---
name: correct
description: Turn recurring coding defects, reverts, review interventions, and crutch comments into permanent architectural, type, lint, or test guardrails; also audit diffs for workaround/suppression comments and prune obsolete prose rules. Use when hardening a codebase after repeated mistakes, not for routine one-off bug fixes or generic code review.
---

# Correct

Every repeated manual intervention is a system design signal. Turn recurring mistakes into deterministic checks so future agents and engineers cannot repeat them—and delete prose rules once machines enforce them.

## Scope Gate

Use this skill when:
- mining recent commits, reverts, PR reviews, agent instruction files, or workaround comments for recurring failure modes (`>= 2` instances, or one high-consequence systemic failure);
- converting an identified mistake class into permanent codebase guardrails; or
- auditing a diff or module for crutch comments and suppression directives (`no-comments` submode).

Do not invent lint rules for one-off typos or speculative edge cases.

## Hardening Hierarchy (Inverted Pyramid)

Always harden at the highest feasible layer—never default to adding prose to `AGENTS.md`:

1. **Architecture / data structure** — make the invalid state or wrong call path unrepresentable.
2. **Type system / schema** — enforce invariants at compile/validation time with zero runtime escape hatches.
3. **Lint / static check in CI** — catch the pattern deterministically before review.
4. **Targeted regression test** — lock runtime invariants when static checks cannot express them.
5. **Prose instruction** — last resort only when none of the above can catch the failure.

## Workflow

1. **Harvest recurring failures.** Inspect recent `git log`, `revert` commits, PR review threads, `AGENTS.md`/`CLAUDE.md`, and workaround comments (`TODO`, `HACK`, `do not remove`, `eslint-disable`, `@ts-ignore`, `noqa`). Cluster by root cause; require `>= 2` real occurrences (or one high-severity failure) before creating a new rule.
2. **Select the highest layer.** For each cluster, test layers 1 → 5 in order and justify why higher layers were insufficient if you drop down.
3. **Build actionable, diff-scoped checks.** When writing a lint/CI rule, follow [the hardening playbook](references/hardening-playbook.md):
   - **Actionable error message:** state what failed AND name the exact file, type, helper, or API the agent should use instead.
   - **Ratchet legacy code:** if the bad pattern is widespread in old files, enforce strictly on added/changed lines or new files so CI adopts immediately without a massive rewrite.
   - **Red-before-green proof:** verify the new check actually fails on a historical real bug commit or faithful reproduction before passing on the fixed code.
   - **Scoped exceptions:** any inline suppression must live on the exact line with a concrete reason, expiry/review condition, and explicit human approval.
4. **Prune obsolete prose.** Maintain a lightweight mapping between prose rules in `AGENTS.md`/skill files and the machine check enforcing them. Once architecture, types, or lint make a mistake impossible, **delete the redundant prose rule** to keep instruction context sharp.

## `no-comments` Audit Submode

When asked to audit comments in a diff or subsystem:
- Treat suppression directives (`eslint-disable`, `@ts-ignore`, `type: ignore`, `noqa`) and workaround/constraint comments (`do not remove`, `must call X before Y`) as guilty until proven necessary.
- Convert constraint comments into types, runtime assertions, tests, or lint rules; remove comments that merely narrate obvious code or excuse bad structure.
- Keep comments that document genuine non-obvious external constraints (hardware quirks, vendor API bugs, regulatory/protocol invariants) that cannot be expressed in code.

## Deliverable

Report per failure cluster: root cause & historical evidence → chosen hardening layer → implemented check/refactor → red-before-green verification output → prose rules deleted (if any).
