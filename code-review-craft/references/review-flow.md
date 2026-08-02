# Review Flow And Collaboration

Use this reference for author-facing review, approval decisions, large or multi-file changes, and review-process conflicts. Treat review as a throughput-and-quality system: reduce waiting and wasted work without lowering the acceptance bar.

## Set The Standard

The decision target is net code health, not perfection and not comment count.

- Approve when the change is a definite improvement or safe preservation of the system and no required issue remains.
- Do not block on personal taste, speculative future generality, or polish that does not change the standard.
- Do not accept a known degradation on a promise to clean it up later. If the change exposes pre-existing debt outside its scope, record a concrete follow-up owner and artifact instead of expanding the review indefinitely.
- Let technical facts, measured data, repository rules, and established principles decide. If multiple options remain equally valid, accept the author's choice.

## Make The Change Reviewable

Check this before detailed line comments:

- The description says **what** changes and **why**, including material tradeoffs or limitations, and still matches the final diff.
- The change is one coherent step, not an arbitrary line-count target. It leaves the system usable and supplies enough context to understand any new API through a real use.
- Related tests travel with behavior. Test-only preparation may precede risky refactoring when it establishes a trustworthy baseline.
- Mechanical refactoring, reformatting, generated churn, feature behavior, and cleanup are separated when mixing them obscures semantics or rollback.
- Each stacked change is independently buildable, reviewable, and safe to land in order.

When the change is too broad to understand confidently, do not simulate coverage. Request a split and suggest boundaries such as preparatory tests, behavior-preserving refactor, one vertical behavior, schema/interface, implementation, configuration/rollout, or generated mechanical change.

## Navigate For Fast Feedback

1. Read the description and broad diff. Decide whether the change should exist and is aimed at the right system.
2. Find the main design, interface, state transition, or high-risk file. Review it before leaf helpers and formatting.
3. Send a load-bearing scope or design objection as soon as it is evidenced, with the reason and a viable next direction.
4. Continue through every assigned human-written line only after the direction survives. Use tests first when they are the clearest behavioral map.
5. State review coverage. When review is intentionally split, name the files or dimensions covered and the specialist still needed.

Optimize response latency rather than pretending the entire review must complete in one silent batch. A preliminary response must say it is preliminary and give the author an immediate next action; it cannot grant approval.

## Write Actionable Comments

Address the code and consequence, not the author. Explain why when the reason is not obvious from a cited standard or failing check.

Choose the least prescriptive form that still unblocks the fix:

- Name the violated behavior or invariant and let the author choose the implementation when several repairs are valid.
- Give a direction, example, or patch only when ambiguity or repeated failure makes it more helpful.
- If code required an explanation during review, prefer clarifying the code, type, name, structure, documentation, or durable comment. A review-thread explanation disappears from future readers.

Label intent separately from severity:

| Label | Author action | Approval effect |
|---|---|---|
| Required | Resolve or rebut with decisive evidence | blocks |
| Optional / Consider | Use judgment | does not block |
| Nit | Minor polish | does not block |
| FYI | No action expected | does not block |

Praise a concrete practice and why it helped when reinforcement would make the next change better. Avoid generic approval theater.

## Respond To Pushback

First test whether the author is right; proximity to the code may reveal facts the reviewer missed. If their evidence resolves the concern, say so and retire it.

If the concern remains, restate the author's argument fairly, identify the unresolved invariant or tradeoff, and provide the missing evidence. Distinguish “we value different outcomes” from “one option violates a fact or standard.” Stay courteous and move contentious discussion to a higher-bandwidth channel when text is looping; write the resulting decision back to the review record.

Escalate to an owner, maintainer, specialist, technical lead, or team decision when consensus fails. Do not let a change stall indefinitely through repeated restatement.

## Keep Review Fast Without Making It Shallow

- Respond at a natural work breakpoint rather than interrupting every focused task, but avoid unowned review queues.
- If a full review cannot happen promptly, acknowledge it, name when or who can review, or provide the broad design response that enables progress.
- Approve with comments only when all unresolved comments are explicitly nonblocking. Never use it to hide uncertainty about an unreviewed critical path.
- Treat “deadline” as a constraint, not evidence. Only a genuine high-consequence emergency justifies narrowing the immediate bar to correctness and containment.
- After an emergency change, require the deferred design, maintainability, tests, and cleanup review. A normal launch desire, end of sprint, or sunk effort is not an emergency.

## Source

This contract adapts the review-process principles in [Google Engineering Practices](https://github.com/google/eng-practices/tree/master/review), including its reviewer and change-author guides. The upstream repository is licensed under [CC BY 3.0](https://github.com/google/eng-practices/blob/master/LICENSE). This skill adds evidence gates, calibrated severities, and AI-review boundaries for the current workflow.
