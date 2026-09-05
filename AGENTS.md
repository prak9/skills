# AGENTS.md: Field Notes on Code Worth Keeping

These are repository-wide engineering defaults. Apply them only when they are relevant to the current task and its risk. The user's explicit task instructions override workflow preferences here; actual permission and safety boundaries remain in force. Task-specific skills add specialized guidance. Do not turn a past model failure into a universal workflow.

## Read before writing

Read the files you will change and enough callers, tests, configuration, and history to understand the behavior you are preserving. Follow established project patterns and dependencies. If no pattern exists, investigate first. Ask one focused question only when the unresolved choice could materially change behavior, risk, or acceptance and cannot be inferred safely; otherwise state the assumption and proceed.

## Define the contract when it matters

For nontrivial, cross-file, high-risk, or hard-to-reverse work, identify the intended outcome, authorized change surface, completion evidence, and conditions that require stopping or user judgment. A small reversible edit does not need a ceremonial plan.

## Keep the solution simple and surgical

Write the minimum code that satisfies the current contract. Reuse existing configuration and abstractions. Add a new abstraction, option, dependency, or error path only for a present requirement or realistic failure mode, not a hypothetical future.

Keep the diff as small as the task allows. Match the existing style, avoid unrelated cleanup and reformatting, and be able to connect every changed line to the requested outcome.

## Verify in proportion to impact

Use the narrowest meaningful check that can fail when the intended behavior is wrong. For a bug, establish a failing reproduction before changing code when practical, and add a regression test when it protects observable behavior. Broaden verification for public interfaces, data, security, concurrency, migrations, production behavior, or wide blast radius. Do not add implementation-mirroring tests or rerun broad checks after the relevant evidence is already decisive unless a new change, failure, or unresolved concern justifies it.

If something is difficult to verify, treat that as design information. State what was verified, what was not, and why.

## Debug from evidence

Read the full error and stack trace, reproduce the problem, form a testable hypothesis, and change one relevant variable at a time. Do not hide an unexplained failure with a defensive check; find the cause or explicitly bound the remaining uncertainty.

## Treat dependencies as lasting commitments

Before adding a dependency, check whether the standard library or an existing project dependency already solves the problem. If a new dependency is justified, state the concrete value and relevant maintenance, security, or operational cost.

## Communicate decisions and uncertainty

Report what changed, why, the verification evidence, and any material residual risk. Distinguish known facts from assumptions. Raise concerns that affect correctness or the user's decision; omit speculative warnings and process narration that do not change the result.

## Correct scope drift without abandoning the task

Watch for the Kitchen Sink, Wrong Abstraction, Optimistic Path, and Runaway Refactor. When one appears, stop expanding the change, return to the smallest valid solution, and continue. Stop the task itself only for a real blocker, a required permission, or a choice that materially changes scope.

## Establish engineering context selectively

For material architecture, data, AI-application, or production changes, establish the project phase and the workload, latency, availability, consistency, cost, security, data-lifecycle, observability, degradation, and rollback constraints that can change the design. Choose the simplest architecture that satisfies the current contract and name the measured condition that would justify evolving it.
