# Foundation Engineering Contract

Use this contract for Loop mode, unattended repeated jobs, or material effects that need explicit verification and recovery controls. Not having line-by-line supervision does not by itself trigger this contract. Reuse existing bounds and evidence instead of creating a second control document.

## Define The Closed Loop

Map the work to five parts before execution:

| Part | Required definition |
|---|---|
| Intent / setpoint | Observable outcome, non-negotiable bounds, and a PASS condition. |
| Actuator | Executor plus the files, tools, commands, and side effects it may touch. |
| Sensor | Independent checker, selected verification layers, and the raw evidence path. |
| State | Current attempt plus append-only events needed to resume and re-judge it. |
| Controller | Finite budget, iterate rule, stop/escalation rule, and irreversible-action gate. |

The executor may run a checker, but its own claim that work is complete is never terminal evidence. If a material part is missing, bound or block the affected action while continuing authorized discovery and independent work.

## Prevent Blind Loops

Align three granularities for every attempt:

- **Change slice:** the largest behavior or surface the attempt may alter.
- **Verification:** a sensor that observes more frequently or diagnoses more precisely than that slice can fail.
- **Memory event:** one recoverable record of the attempt, result, evidence, changed belief, and next rule; not a token transcript or a coarse “module done” snapshot.

Verification must be finer than the change. If a task can alter a module but the checker can only say “the app starts,” split the task or strengthen the sensors before acting. Increase feedback frequency as change size, uncertainty, or blast radius grows.

## Require An Independent Evidence Path

For each acceptance condition, trace:

```text
condition -> plausible failure -> sensor -> raw evidence -> PASS / FAIL decision
```

- Prefer a deterministic checker whose result does not depend on the maker's narrative: compiler, type checker, schema validator, test, runtime probe, or diff.
- A separate model may judge fuzzy work only against a frozen rubric and inspectable artifacts. It must look for counterexamples, not merely reasons to approve.
- Human review owns irreducible taste, policy, risk, and external commitment. Do not spend it rechecking facts a cheaper deterministic sensor can decide.
- No evidence path means no completion claim. A severity or confidence label without a reproducible failure path is only a hypothesis.

## Descend Judgment To The Cheapest Decisive Sensor

Do not force every check into one universal ladder. Route each failure class to the lowest-cost layer that can actually decide it:

| Failure class | Preferred sensor | Example evidence |
|---|---|---|
| Syntax or buildability | compiler / build | exit code and diagnostics |
| Value shape or static invariant | type checker / static analysis | file, line, expected and actual type |
| Call graph or change impact | references / compatibility analysis | affected symbols and dependents |
| Boundary data | schema / contract / assertion | rejected payload or contract diff |
| Runtime integration or concurrency | real execution / probe / replay | request, trace, timing, or race evidence |
| Behavioral invariant or input space | example, integration, or property test | failing case and reproducible command |
| Rendering or interaction | screenshot, accessibility, or multimodal check | baseline diff and scenario |
| Fuzzy quality | rubric-bound independent model | criterion-by-criterion evidence |
| Taste, policy, or irreversible consequence | retained human decision | named approver and decision record |

More sensors are not automatically better. Build a **judgment coverage map** only for material acceptance conditions: condition, failure class, sensor, evidence owner, and uncovered gap. Call coverage complete when every material condition has a decisive sensor or an explicit human gate. Do not quote a percentage unless the denominator is defined.

## Bound Failure And Irreversibility

- Bound the change surface and side effects using the request and applicable permissions. Ordinary commands and files needed inside that scope do not require individual preapproval unless the environment enforces an allowlist.
- Before a consequential external or hard-to-reverse action, verify that existing authorization covers its target and effect. Ask only when it does not, or when an explicit final gate remains. Cleanup of task-owned disposable files does not create a new human gate.
- Define timeout, retry, rollback, and escalation behavior before execution. A failure without a handling path is an unplanned outcome.
- Archive or remove task-local state after terminal transitions so stale attempts cannot steer the next task.

## Calibrate Without Moving The Goalposts

- Freeze acceptance criteria, rubric, sensor versions, and holdout cases for an attempt. Changing them is a harness change, not evidence that the implementation improved.
- Version a harness change, stage it, replay representative prior cases, test unseen or held-out cases when promoting a reusable rule, then adopt or roll back explicitly.
- When real outcomes arrive later, record the prediction, evaluation date, and actual result. Use the miss to revise the sensor or rule, not to rewrite history.
- If a result passes the checker but fails in reality, reopen the acceptance contract and add the cheapest sensor for the escaped failure class.

## Control Comprehension Debt

A system is not safely owned when its output grows faster than the owner's ability to explain and re-judge it. Preserve a replayable line from intent to change to sensor to evidence to residual risk.

Provide the concise explanation needed to approve, operate, debug, or inherit the result. Use a teach-back only when explicitly required or when a concrete comprehension gap prevents safe operation; ordinary handoff does not require a quiz or a new owner acknowledgment. State material unverified behavior and any genuinely retained decision.
