---
name: lil-log
description: Apply Lilian Weng's harness-engineering lens to design, review, or improve LLM agent runtimes and self-improvement loops. Use when the user asks about harness design, AI agent workflows, recursive/self-improving agents, auto-research systems, context engineering, persistent memory, subagents, eval-driven iteration, evolutionary/program search, reward hacking, or how to turn an agent from a one-shot prompt into a verifiable loop.
---

# Lil'Log Harness Engineering

Use this skill to turn agent work into a harness: the runtime around a base model that controls how it observes, plans, uses tools, stores state, checks results, and improves. Do not summarize the source article unless asked; apply it as an engineering framework.

Core thesis: near-term self-improvement is more likely to come from improving the machinery around models than from models directly editing their own weights. Optimize the loop that gets better answers, not only the answer.

## First Principles

- Treat the harness as software, not a prompt. Specify control flow, tools, state, permissions, evaluation, logs, recovery, and update rules.
- Keep the interface simple and the mechanism inspectable. Prefer plain files, commands, diffs, status records, and deterministic merge/update rules over hidden chat memory.
- Design for evidence before autonomy. The more the harness can change itself, the stronger the held-out evaluation, trace audit, rollback, and permission boundary must be.
- Move humans up the stack. Ask for human judgment at goal, risk, taste, and acceptance points; avoid requiring approval for every ordinary implementation step.

## Canonical Harness Patterns

### 1. Workflow Automation

Use a goal-oriented loop:

```text
goal -> plan -> act/tool -> observe/test -> reflect -> improve -> repeat or stop
```

Make the loop explicit. Define stop criteria, failure criteria, and when the agent should ask the user for clarification. A workflow is weak if it only says "think step by step" and never names the verifier or iteration gate.

### 2. File System as Persistent Memory

Store long-horizon state outside the context window:

- task plans, experiment logs, rollout traces, error records, code diffs, paper notes, benchmark results
- current context/playbook items with IDs and concise descriptions
- previous harness edits, rejected attempts, and passing behaviors that must be preserved

The agent should recover after interruption by reading files and logs, not by depending on chat history.

### 3. Subagents and Backend Jobs

Use parallelism only when it is explicit and inspectable:

- launch isolated hypothesis searches, experiments, or reviews as separate jobs/subagents
- write each output to a file or log with status, inputs, and conclusion
- merge results through a parent process that compares evidence and handles conflicts

Avoid transient subagent outputs that disappear into chat context.

## Context Engineering

Do not append every tool result into context. Build a structured context surface.

- Maintain a playbook of itemized bullets: `(id, description, evidence/source, last updated)`.
- Let trajectories produce new observations, then distill successes and failures into playbook updates.
- Merge updates deterministically. Avoid repeatedly rewriting one giant prompt blob, which causes collapse, accidental deletion, and brevity bias.
- Separate mechanism from content: the context-management procedure is one artifact; the current task context is another.

When designing a context system, specify:

1. What gets written permanently.
2. What gets retrieved for each rollout.
3. What gets summarized, deduplicated, or retired.
4. What evidence justifies a memory update.

## Self-Improvement Loop

Use this propose-evaluate-accept loop for harness changes:

1. **Mine weaknesses.** Collect traces, verifier outcomes, and root-cause records. Distinguish surface failures such as "timeout" from causal mechanisms such as bad planning, missing artifact handoff, context loss, or unsafe tool choice.
2. **Bound the editable surface.** Name exactly which prompts, workflow nodes, tool policies, context rules, or scripts may change. Keep the evaluator, permission layer, secrets, and production safety controls outside the self-edit loop.
3. **Propose narrow edits.** Prefer recurring, addressable failure patterns. Include passing behaviors that must not regress and a log of previously rejected edits.
4. **Validate on held-in and held-out tasks.** Held-in checks whether the target weakness improved; held-out checks whether unrelated behavior regressed.
5. **Accept only with evidence.** Merge qualified edits, keep rejected candidates with reason and trace, and preserve rollback.

Do not call a loop self-improving if it only re-runs with more confidence and no persistent failure analysis or acceptance criterion.

## Choosing an Optimization Level

Use the lowest level that can solve the problem:

| Level | Optimize | Use when | Main risk |
|---|---|---|---|
| Prompt/instructions | Wording and local guidance | Task is narrow and failures are obvious | Brittle prompt tricks |
| Structured context | Retrieval, summaries, playbook items | Long-horizon work loses facts or repeats mistakes | Context bloat or stale memory |
| Workflow | Graph/loop of actions and verifiers | Process order and checkpoints determine success | Overfitting to one workflow |
| Harness code | Runtime logic, tools, state, permissions | Behavior depends on executable orchestration | Broken abstraction boundaries |
| Optimizer/evolution | Search over harness/program candidates | Fitness is cheap, objective, and repeatable | Reward hacking and diversity collapse |
| Model weights | Training or continual learning | Non-parametric changes are insufficient | Stability, safety, and Goodhart failures |

If the evaluator is fuzzy, slow, or gameable, improve the evaluator before increasing autonomy.

## Review Checklist

When reviewing an agent or self-improvement proposal, answer these questions:

- **Goal and verifier:** What exact outcome is optimized? Is the verifier objective, held out, and hard to game?
- **State lifecycle:** What is stored in files? What is kept in context? What expires? What survives interruption?
- **Trace quality:** Can a later agent inspect what happened, why it failed, and which mechanism was implicated?
- **Permission boundary:** Which surfaces can the agent edit? Which safety, evaluator, and deployment controls sit outside the loop?
- **Regression control:** What passing behavior must remain true? What held-out tests catch unknown regressions?
- **Negative results:** Are failed attempts preserved as learning, or silently overwritten by optimistic summaries?
- **Diversity:** Does search keep meaningfully different candidates, or collapse into variants of the current best trick?
- **Long-term health:** Does the reward protect maintainability, ownership boundaries, compatibility, migration cost, and future debugging burden?
- **Human touchpoints:** Where is human judgment required because taste, risk, or long-term value cannot be reduced to a metric?

## Failure Modes to Name Explicitly

- Training-data defaults: stale libraries, old commands, copied formats, or assumptions not grounded in the repo/data.
- Implementation drift: the agent silently replaces the intended method with an easier common solution under pressure.
- Memory degradation: critical details disappear because they were never stored as durable artifacts.
- Over-optimism: noisy or failed experiments are declared successful.
- Weak taste: work is executable but answers the wrong question.
- Reward hacking: the loop learns the judge, tests, or benchmark artifacts instead of the real objective.
- Abstraction breach: a self-editing harness can modify the safety or evaluation layer that is supposed to constrain it.

## Output Shape

For substantial requests, produce a concise harness memo:

```text
Objective:
Base model/task:
Harness loop:
Tools and permissions:
Persistent state:
Context construction:
Eval/verifier:
Improvement loop:
Human checkpoints:
Failure modes:
Next experiment:
```

When the user asks for code changes, implement the smallest harness change that creates a measurable loop, then verify it with a trace or test.

## Source

Distilled from Lilian Weng, "Harness Engineering for Self-Improvement", Lil'Log, July 4, 2026, https://lilianweng.github.io/posts/2026-07-04-harness/
