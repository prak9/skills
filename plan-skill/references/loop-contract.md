# Loop Contract

Use this interface only for `Profile: Full` work that must converge through repeated attempts. Read `foundation-contract.md` first. Keep the state finite and machine-readable.

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
| Execution scope | <allowed files, tools, commands, networks, and external writes> |
| Failure signal | <result that triggers reflection> |
| Verifier | <test, metric, review, or scenario> |
| Checker / independence | <who or what judges; why maker self-report cannot decide PASS> |
| Sensor stack / evidence path | <acceptance condition -> failure class -> sensor -> raw evidence -> decision> |
| Granularity alignment | <maximum change slice; finer verification precision/frequency; memory event> |
| Max iterations | <positive integer> |
| Reflect trigger | <when to interpret evidence> |
| Iterate rule | <what may change and what stays fixed> |
| Stop / escalation condition | <budget, safety, or repeated-failure stop> |
| Irreversible gate / recovery | <human gate plus rollback/timeout/retry, or N/A with reason> |
| Evaluator version / calibration | <frozen rubric/sensor version; drift trigger; holdout or N/A with reason> |
| Memory write rule | <every verified attempt gets R; which consequential attempts also become RUN entries> |

Replace `Loop State` with one current-state row:

| Iteration | Node | Step | Hypothesis / plan delta | Verification / evidence path | Latest result | Decision | Next |
|---|---|---|---|---|---|---|---|
| L-001 | NODE-001 | Plan | <current belief or change> | <checker and evidence target> | pending | continue | <next action> |

`L-*` identifies the current attempt. `Loop iteration` counts attempts already started; increment it when an attempt starts, even if the run later fails or becomes invalid.

## Task Interface

For every Loop task:

- set `Plan mode: Loop`;
- set `Loop budget` to a positive integer no greater than program `Max iterations`; it is the maximum attempts this task may start, not prose;
- add `Current Loop Attempt` with the current `L-*` ID.

Use this current-attempt shape. `Change slice` must fit within the program scope; `Checker / evidence` must diagnose more finely than that slice can fail.

| Iteration | Loop step | Node | Change slice | Checker / evidence | Latest result | Reflection | Plan delta | Next |
|---|---|---|---|---|---|---|---|---|
| L-001 | Plan | N-001 | <smallest falsifiable change> | <independent sensor and raw evidence target> | pending | Not run yet | None | Act |

Keep planned actions in `Atomic Plan`. Update only the current attempt here; preserve consequential completed attempts in memory.

## Memory And Transitions

- Record a pre-execution Loop decision as `D-*` when it constrains future work. Do not invent a `RUN-*` before an attempt starts.
- On start, increment `Loop iteration`, set program and task to `Act`, and keep the same `L-*` ID.
- After verification, write one evidence-linked `R-*`, then move to `Pass`, `Reflect`, or `Blocked`.
- Treat a change to acceptance, rubric, sensor, or holdout set as a versioned harness change. Freeze it for the next attempt; do not count moving the goalposts as implementation progress.
- Continue only when the next attempt changes a belief, method, or falsifiable uncertainty.
- A PASS requires the declared independent evidence path. Maker self-report, a broader-than-change smoke check, or an evaluator changed mid-attempt cannot close the loop.
- During `Reflect`, set `Clean state` to `Due` when stale hypotheses, repeated state, or the Clean thresholds are reached; run Clean before handoff or a terminal transition.
- Stop when success, the finite budget, a safety condition, or the escalation condition is reached.
- Run strict validation before execution, handoff, and every terminal transition.
