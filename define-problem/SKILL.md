---
name: define-problem
description: Turn vague goals, symptoms, requests, metrics, and solution-first ideas into a precise, executable, and testable problem contract. Use when Codex needs to define the real problem, clarify requirements, frame an AI task, identify the target user and context, separate outcomes from proposed solutions, write a problem statement, set success criteria and constraints, distinguish symptoms from causal hypotheses, or decide what should be solved before planning, research, design, or execution. Stop at the problem definition and do not drift into solution design unless the user asks.
---

# Define Problem

Treat problem definition as the scarce judgment step before cheap execution.

```text
vague input -> testable problem contract -> plan or research -> execution -> feedback -> revised definition
```

Do not optimize an answer until the question is good enough to guide action. A fast solution to the wrong problem only produces waste faster.

## Hold the boundary

- Treat a proposed feature, tool, prompt, report, automation, or implementation as a candidate solution, not as the problem itself.
- Let the responsible person choose the valued outcome, acceptable tradeoffs, and constraints. Use AI to structure, challenge, and test that judgment; do not fabricate stakes or preferences.
- Define the problem only as precisely as the next decision requires. Avoid both vague slogans and weeks of analysis before a reversible first step.
- End with a problem contract. Hand off to planning, research, design, or execution only after the contract is accepted or explicitly marked provisional.

## Make the contract agent-legible

- Write so a capable outsider or agent can recover the same outcome, scope, constraints, key terms, and success evidence without hidden organizational context.
- Replace adjectives such as "fast," "robust," or "equivalent" with observable bounds. Separate required behavior from illustrative examples and negotiable preferences.
- Point to authoritative artifacts—current behavior, protocols, schemas, tests, fixtures, or a reference implementation—and state what each one specifies and what it does not.
- Keep unresolved decisions explicit. Do not let an agent silently choose a load-bearing interpretation.
- Stop before work decomposition or implementation design; hand the accepted contract to `plan-skill`.

## Classify the input

First identify what the user actually supplied:

- **Situation:** “Support tickets doubled this month.”
- **Symptom:** “Customers keep asking where their orders are.”
- **Goal:** “Reduce support workload.”
- **Solution:** “Build an AI support bot.”
- **Task:** “Write a bot specification.”
- **Metric target:** “Cut average handle time by 30%.”
- **Defined problem:** a specific actor, current gap, desired outcome, constraints, and success evidence.

Do not silently upgrade one type into another. A symptom does not prove a cause; a metric does not explain why it matters; a requested deliverable does not establish that it solves the underlying need.

## Build the definition

### 1. Recover the outcome

Strip away the proposed solution and ask what change it is meant to create.

- Replace “build X” with “change Y for actor Z.”
- Ask what would still need to improve if X were unavailable.
- Identify why the outcome matters now and which decision it should change.
- Keep the original solution as a hypothesis to evaluate later, not as a locked requirement.

Example: turn “build an automatic weekly report” into “reduce the two hours team leads spend reconciling status and prevent unresolved blockers from reaching Friday unnoticed.”

### 2. Fix the actor and context

Name the primary person, team, customer, operator, or decision owner experiencing the problem. Describe the actual workflow and moment of friction.

- Separate the beneficiary from the buyer, approver, operator, and person bearing the cost.
- Record what the actor does now, what blocks them, what they care about, and what they can ignore.
- Prefer observed behavior, records, examples, and direct statements over an invented persona.
- Split the problem when different actors need incompatible outcomes.

### 3. State the current gap

Describe the gap between current and desired states with available evidence:

- baseline behavior or performance;
- frequency, scale, duration, and affected population;
- practical cost, risk, delay, or missed opportunity;
- evidence quality and important unknowns.

Do not write a suspected cause as an established fact. Label root-cause claims as hypotheses until evidence distinguishes them from plausible rivals.

Clarify any concept whose meaning can change the actor, gap, measurement, or solution space. Give it an operational definition when possible; check whether stakeholders use the same word differently, whether a proposed condition is necessary or merely sufficient, and whether an indicator has silently replaced the outcome it is meant to represent.

### 4. Set constraints and non-goals

Name the boundaries that shape a valid answer:

- time, budget, people, tools, policy, compliance, safety, compatibility, and reversibility;
- hard constraints versus preferences;
- tradeoffs the owner will and will not accept;
- adjacent problems intentionally excluded.

State who bears the downside of a shortcut. A constraint is incomplete when its cost is pushed onto an unnamed user or operator.

### 5. Define success and failure

Make success observable:

- give a baseline, target, measurement method, population, and time window when quantitative evidence is available;
- use a concrete observable behavior when a number would be artificial;
- include guardrails so one metric cannot improve by damaging quality, safety, cost, or another actor;
- state what result would show that the problem was misdefined or not worth solving.

Distinguish the outcome metric from the output. Shipping a dashboard is an output; reducing reconciliation time without increasing missed blockers is an outcome.

### 6. Choose the next validation

List no more than three material assumptions or causal hypotheses. For each, name the cheapest observation that could change the definition.

Prefer a real workflow sample, interview about recent behavior, log query, manual trial, prototype, or small reversible test over a broad opinion survey. Define, test, and revise; do not wait for a perfect first formulation.

## Ask high-information questions

Ask no more than three questions at a time. Prioritize:

1. What outcome or decision must change?
2. Who experiences the problem, in what concrete situation, and what evidence shows it?
3. What counts as success, and which constraint cannot be violated?

Proceed with explicit, conservative assumptions when missing details do not materially change the next step. Stop and ask when guessing would change the actor, objective, acceptable tradeoff, or success test.

## Test the problem quality

Before handoff, verify:

- **Outcome test:** describe a changed condition, not a deliverable.
- **Actor test:** identify one primary actor and a real context.
- **Evidence test:** separate observed facts from interpretations and guesses.
- **Concept test:** keep load-bearing terms stable, observable enough for the next decision, and shared across stakeholders or explicitly preserve their competing meanings.
- **Open-solution test:** allow at least two materially different solution classes.
- **Success test:** let an independent observer decide whether the outcome improved.
- **Constraint test:** expose the real limits, tradeoffs, and non-goals.
- **Falsification test:** name evidence that would revise or retire the definition.
- **Agent-legibility test:** let a capable outsider or agent paraphrase the problem and reach the same scope without extra explanation.

If a test fails, revise the definition instead of compensating with a longer prompt or plan.

## Deliver the problem contract

Lead with the shortest useful problem statement, then supply only the fields needed for action:

```text
Problem statement:
For [actor] in [context], [current state and evidence] causes [material consequence].
We need [desired outcome] by [time horizon], subject to [hard constraints],
without [guardrail violation]. Success means [observable standard].

Current evidence and baseline:
Key terms / operational definitions:
Authoritative behavior references and their limits:
Decision this definition enables:
Hard constraints and negotiable preferences:
Non-goals:
Assumptions / causal hypotheses:
Next cheapest validation:
Open questions:
Status: provisional | validated enough for next step
```

Compress the contract for simple tasks; do not fill fields with boilerplate. Keep evidence, inference, and owner choice visibly separate.

## Hand off deliberately

- Use `plan-skill` after a project problem is defined and implementation must be decomposed.
- Use `research-craft` when a decisive assumption requires controlled investigation.
- Use `judgment-craft` when the problem is defined but a load-bearing concept, premise, crux, tradeoff, or consequential choice remains contestable.

Do not invoke downstream execution merely because the problem can now be stated. Let the user confirm the contract or explicitly authorize the next stage.

## Source

Distilled from the user-provided article *AI 替不了的，是“定义问题”的能力*. Its goal–actor–standard model is extended here with evidence, constraints, non-goals, causal hypotheses, falsification, and iterative validation.
