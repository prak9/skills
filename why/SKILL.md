---
name: why
description: Answer "why does X work this way", "why did we pick Y", design rationale, regressions, postmortems, or data-backed thresholds from the historical record (git commits, PRs, issues, docs). Returns a cited read on decisions and tradeoffs. Use how for runtime behavior.
---

# Why

Answer from the historical record, not the code alone. Code shows *what* happens today, rarely *why* it was written that way.

## Workflow

1. **Trace the record.** Inspect the git commits (`git log -S`, `git log -L`, `git blame`), PR discussions, issue threads, design docs, and postmortems that introduced the target and each subsequent change. Follow external trackers/docs if the git trail is thin.
2. **Separate record from inference.** Cite exact commits, PR numbers, dates, and what the authors actually wrote. Explicitly label any reasoning of your own as an **inference**.
3. **Name the gaps.** State plainly what the record does not answer instead of inventing a plausible backstory.

Pair with `$how` when the user also needs the current runtime execution path.
