# Research Harness Engineering

Read this adapter when the research object is an LLM agent, workflow, runtime, context system, or self-improvement loop. Apply the core research contract in `SKILL.md`; use the additions here to make the machinery observable and safely editable.

## Core model

Treat the harness as software around the base model:

```text
goal -> plan -> act/tool -> observe -> verify -> update -> repeat or stop
```

The harness controls observation, tools, state, context, permissions, evaluation, recovery, and change acceptance. Improving this loop is often more reliable than asking the model to reason harder or edit its own weights.

## Specify the runtime contract

Before implementation, define:

```text
Objective and base task:
Verifier and held-out cases:
Editable surfaces:
Frozen evaluator / permissions / safety controls:
Control flow and stop conditions:
Tools and authority boundaries:
Persistent artifacts and recovery path:
Context construction and retirement rules:
Regression anchors and rollback:
Human checkpoints:
```

Ask for human judgment at goals, taste, material risk, and acceptance boundaries. Do not require approval for every safe, ordinary step inside an agreed contract.

## Design state for recovery and audit

Store long-horizon state outside the context window:

- plans, run manifests, traces, verifier outcomes, code or prompt diffs, error records, and accepted or rejected changes
- concise playbook items with stable IDs, evidence, source, and update time
- passing behaviors that future edits must preserve
- current run status sufficient to resume after interruption

Separate the context-management mechanism from its current content. For every memory class, specify what is written, retrieved, summarized, deduplicated, retired, and what evidence authorizes an update. Do not continuously rewrite one giant prompt blob.

## Use parallel work only when inspectable

For subagents or backend jobs:

- isolate inputs, permissions, artifact paths, and status
- preserve each result outside transient chat context
- let a parent compare evidence, resolve conflicts, and decide what enters durable memory
- prevent one worker from modifying the evaluator or another worker's evidence

Parallelism is useful only when the merge and verification costs remain lower than the saved time.

## Run self-improvement as research

1. **Mine weaknesses:** collect traces and verifier failures; distinguish symptoms such as timeout from causes such as context loss or bad planning.
2. **Bound edits:** name the prompts, workflow nodes, retrieval rules, tools, or scripts allowed to change.
3. **Propose narrowly:** target a recurring failure and list passing behaviors that must remain true.
4. **Evaluate:** use held-in cases for the target weakness and held-out cases for regression.
5. **Accept or reject:** require evidence, preserve rejected candidates and reasons, and keep rollback possible.
6. **Update memory:** promote only causal, reusable findings; do not turn one noisy win into a permanent rule.

Do not call a loop self-improving if it merely retries without persistent failure attribution, an editable boundary, or an acceptance criterion.

## Choose the lowest effective optimization level

| Level | Optimize | Use when | Main risk |
|---|---|---|---|
| Prompt | Local instructions | Failure is narrow and legible | Brittle prompt tricks |
| Context | Retrieval and playbook | Long work loses or repeats facts | Bloat and stale memory |
| Workflow | Action and verification graph | Order and checkpoints determine success | One-workflow overfit |
| Harness code | Runtime, tools, state, permissions | Behavior depends on executable orchestration | Boundary breakage |
| Search/evolution | Candidate programs or harnesses | Fitness is cheap, repeatable, and trustworthy | Reward hacking and collapse |
| Model weights | Training | Non-parametric changes are insufficient | Stability and safety failures |

If the evaluator is fuzzy, slow, leaked, or gameable, improve it before increasing autonomy or search power.

## Review the system, not only the answer

- **Goal and verifier:** Does the score represent the real outcome, and is it hard to game?
- **Trace quality:** Can a later reviewer reconstruct what happened and why?
- **Permission boundary:** Can a candidate modify the constraint intended to judge it?
- **Regression control:** Which passing behaviors and held-out cases block promotion?
- **Negative results:** Are failures retained with causal attribution?
- **Diversity:** Does search preserve meaningfully different candidates?
- **Long-term health:** Does acceptance account for maintainability, compatibility, ownership, and migration cost?
- **Human role:** Which choices require non-reducible taste, ethics, or risk judgment?

## Failure modes

- stale training-data defaults replace repo-grounded facts
- implementation drifts toward an easier but different method
- critical state disappears because it lived only in context
- noisy runs are narrated as progress
- the system optimizes an easy metric while solving the wrong problem
- the candidate exploits tests, judge quirks, leakage, or artifact formats
- the self-editing surface reaches permissions, safety controls, or the evaluator

## Harness handoff

```text
Objective and base task:
Harness loop:
Editable and frozen surfaces:
Tools and permissions:
Persistent state and context lifecycle:
Verifier, held-out set, and regressions:
Improvement and rollback rules:
Human checkpoints:
Next experiment:
```

Source: Lilian Weng, “Harness Engineering for Self-Improvement,” Lil'Log, 2026-07-04.
