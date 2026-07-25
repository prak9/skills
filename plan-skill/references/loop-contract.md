# Loop Contract

Use this interface only for `Profile: Full` work that must converge through repeated attempts. Keep the state finite and machine-readable.

## Program Interface

Set:

- `Plan mode: Loop`
- `Loop state` to exactly one of `Goal`, `Plan`, `Act`, `Verify`, `Reflect`, `Iterate`, `Pass`, or `Blocked`
- `Loop iteration` to `<started>/<max>`, such as `0/3`

Replace `Loop Contract` with this exact field set:

| Field | Content |
|---|---|
| Loop goal | <result the loop must converge to> |
| Success criteria | <verifiable PASS condition> |
| Failure signal | <result that triggers reflection> |
| Verifier | <test, metric, review, or scenario> |
| Max iterations | <positive integer> |
| Reflect trigger | <when to interpret evidence> |
| Iterate rule | <what may change and what stays fixed> |
| Stop / escalation condition | <budget, safety, or repeated-failure stop> |
| Memory write rule | <which consequential attempts become RUN entries> |

Replace `Loop State` with one current-state row:

| Iteration | Node | Step | Hypothesis / plan delta | Verification | Latest result | Decision | Next |
|---|---|---|---|---|---|---|---|
| L-001 | NODE-001 | Plan | <current belief or change> | <verifier> | pending | continue | <next action> |

`L-*` identifies the current attempt. `Loop iteration` counts attempts already started; increment it when an attempt starts, even if the run later fails or becomes invalid.

## Task Interface

For every Loop task:

- set `Plan mode: Loop`;
- set `Loop budget` to a positive integer no greater than program `Max iterations`; it is the maximum attempts this task may start, not prose;
- add `Current Loop Attempt` with the current `L-*` ID.

Use this current-attempt shape:

| Iteration | Loop step | Node | Attempt | Verification result | Reflection | Plan delta | Next |
|---|---|---|---|---|---|---|---|
| L-001 | Plan | N-001 | <attempt> | pending | Not run yet | None | Act |

Keep planned actions in `Atomic Plan`. Update only the current attempt here; preserve consequential completed attempts in memory.

## Memory And Transitions

- Record a pre-execution Loop decision as `D-*` when it constrains future work. Do not invent a `RUN-*` before an attempt starts.
- On start, increment `Loop iteration`, set program and task to `Act`, and keep the same `L-*` ID.
- After verification, move to `Pass`, `Reflect`, or `Blocked`; cite raw evidence.
- Continue only when the next attempt changes a belief, method, or falsifiable uncertainty.
- Stop when success, the finite budget, a safety condition, or the escalation condition is reached.
- Run strict validation before execution, handoff, and every terminal transition.
