# Executable Specification Contract

Use this contract when several agents must work from one definition, when implementation is being ported or rewritten, or when prose alone cannot prove behavioral equivalence.

## Build A Layered Oracle

Record only the layers the work needs, and name their authority:

1. **Outcome:** the user-visible or system-visible condition that must change.
2. **Bounds:** compatibility, safety, performance, policy, and non-goals that cannot be violated.
3. **Semantic contract:** invariants, state transitions, input/output behavior, error behavior, ordering, and side effects.
4. **Reference evidence:** protocols, schemas, fixtures, tests, current implementation, traces, or production examples.
5. **Executable acceptance:** commands and scenarios whose raw output lets an independent checker decide.
6. **Work interfaces:** ownership, inputs, outputs, dependencies, and merge boundaries for each agent.
7. **Unknowns:** unresolved choices, cheapest resolution, and the point at which an agent must stop rather than guess.

Do not turn every preference into an implementation instruction. Lock the behavior and fragile boundaries; leave the method negotiable where several designs can satisfy them.

## Treat Reference Behavior As Evidence

A working implementation can be the richest available specification, but it is not automatically the desired design or complete truth.

- State which behaviors must be preserved and which existing quirks are bugs, undefined, or intentionally retired.
- Port or translate relevant tests and fixtures, then run them against both implementations when possible.
- Add a differential harness for outputs, errors, state changes, ordering, serialization, and externally visible side effects that matter.
- Use representative and boundary inputs; a shared happy-path test suite is only a partial claim.
- Record every intentional difference with its owner, reason, acceptance evidence, and compatibility impact.
- Keep performance equivalence separate from functional equivalence; define budgets and measurement protocols explicitly when performance matters.

Reference code answers "what happens today." The problem contract answers "what must be true." When they conflict, surface the conflict instead of silently choosing one.

## Write An Independent Work Packet

Each agent-owned task should let a capable executor and checker proceed without private chat history:

```text
Objective and non-goals:
Owned surface and forbidden surface:
Inputs, outputs, and interface contracts:
Specification sources and what each governs:
Dependencies and downstream consumers:
Locked behavior and negotiable implementation space:
Acceptance conditions and exact verification:
Expected evidence artifacts:
Known unknowns and escalation trigger:
Completion and handoff destination:
```

Align granularity: the task slice must be smaller than the verifier's ability to localize failure. Split a packet when its checker can only report "something in this module is wrong."

## Completion Gate

Do not call the specification ready until:

- two independent readers can paraphrase the same required behavior and scope;
- each agent packet has explicit inputs, outputs, ownership, and acceptance evidence;
- authoritative references and their limits are named;
- behavior-preserving work has a translated or differential verification path;
- intentional differences and unresolved decisions are visible; and
- no terminal claim depends only on the executor's self-report.
