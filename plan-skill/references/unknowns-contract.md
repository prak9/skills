# Unknowns Discovery Contract

Use this contract when the map in the request, prompt, or plan may omit territory that can change execution. Common triggers are an unfamiliar codebase or domain, tacit taste, a long-horizon implementation, or a request for a blind-spot pass, prototype, interview, or implementation notes.

## Use Four Search Lenses

| Lens | Meaning | Route |
|---|---|---|
| Known knowns | Explicit facts, preferences, and accepted evidence | Put only execution-relevant items in context, constraints, or acceptance; verify drift-prone claims. |
| Known unknowns | Questions already recognized but unanswered | Resolve from evidence, assign the cheapest validation node, or name the missing human judgment and block. |
| Unknown knowns | Tacit criteria someone recognizes when shown but cannot yet state | Surface them with contrasting prototypes, concrete references, or one-at-a-time interviews. |
| Unknown unknowns | Relevant factors nobody has considered yet | Run a blind-spot pass across the real territory; once found, reclassify and route them. |

Use the taxonomy to search, not to build a permanent four-bucket inventory. An unknown unknown cannot be recorded before discovery. Once discovered, it becomes an assumption, question, finding, decision, risk, blocker, or reflection in the existing authoritative state.

## Before Implementation

1. Record the user's starting point: what they know, what they have tried, and where their judgment is weak or tacit.
2. Inspect the territory before refining the map: relevant code, tests, configuration, history, runtime evidence, documents, and external constraints.
3. Run a **blind-spot pass** when the territory is unfamiliar. Check hidden conventions, prior art, integration boundaries, failure paths, operations, security, rollout, and what expert reviewers would ask.
4. Use cheap contrastive prototypes or brainstorms when the user will know the right answer only after seeing alternatives. Keep them disposable until the direction is chosen.
5. Prefer concrete references over lengthy description; source code is the strongest reference when semantics or interaction details matter.
6. Interview one consequential question at a time. Prioritize answers that change architecture, data shape, UX flow, risk, acceptance, or whether to proceed.
7. Lead the implementation plan with decisions most likely to change. Put the cheapest belief-changing check before broad construction.

Stop discovery when each material unknown is resolved, explicitly bounded, or assigned a resolution path. Exhaustive certainty is not the goal.

## During Implementation

When implementation exposes an edge case, constraint, or contradiction:

1. Classify it as a discoverable fact, human preference, or new risk.
2. Investigate facts in the territory before guessing.
3. If the choice is reversible and inside negotiable space, take the conservative option and record the assumption, evidence, and reversal condition in the active node.
4. If it can change scope, architecture, acceptance, risk, an imperative bound, or an external commitment, stop or update the plan and escalate the retained human decision.
5. Close the attempt with an `R-*` reflection that records the deviation and the next operational rule.

In Lite, use `program.md`; in Full or Loop, use the active task package and `memory.md`. Do not create a parallel `implementation-notes.md` when those artifacts already own the state. A temporary note is acceptable only outside a durable plan and must be distilled or discarded before handoff.

## After Implementation

- Package the result as an explainer when reviewers need the same context, prototype, decisions, deviations, and evidence that resolved the original unknowns.
- Use a short reviewer quiz or teach-back only when human understanding is part of safe approval, operation, or ownership. It complements verification; it does not replace tests.
- Ask what new information changed the plan, what remained tacit, and which lesson should become a durable rule. Store only learning that will change future execution.
- If the result is wrong despite passing its verifier, treat that as evidence that the map or acceptance contract omitted a material unknown and reopen the cheapest relevant discovery step.
