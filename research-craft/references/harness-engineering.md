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
Data sources, coverage, freshness, and provenance:
Regression anchors and rollback:
Human checkpoints:
```

Ask for human judgment only when an unresolved goal, taste choice, material risk, or reserved acceptance decision cannot be settled from the agreed contract. Reuse prior answers and applicable authorization; do not require approval for ordinary steps or manufacture a final sign-off. Prepare independent authorized work before pausing the affected branch.

## Close the verifier loop before scaling

Tool access is not verification capability. Prove a closed loop on a representative task before adding concurrency or authority:

| Link | Required proof |
|---|---|
| Reach | Enter the target state from a declared starting state. |
| Reproduce | Trigger the reported symptom or establish the baseline. |
| Act | Make the bounded change through the real product or system path. |
| Observe | Capture the decisive runtime, UI, trace, metric, or state signal. |
| Compare | Apply predeclared acceptance criteria to before-and-after evidence. |
| Preserve | Link evidence and verifier results to the exact candidate revision. |
| Recover | Resume interrupted work and roll back an accepted change safely. |

Record every missing link as **Human-verification debt** with an owner and next probe. Until the link closes, the human remains the verifier bottleneck; more agents only multiply unchecked output.

## Maintain a feature map from symptom to evidence

Keep a versioned map that lets an agent turn a screenshot, user surface, or vague report into a reproducible path and decisive evidence:

```text
Feature / claim:
User surface / entry:
Preconditions / fixture:
Reproduction steps and expected symptom:
Code entry points / owner:
Decisive sensors:
Regression / acceptance:
Rollback / recovery:
Freshness source / last verified:
```

Generate or reconcile entries from routes, tests, ownership, and telemetry where possible. Keep the map local enough to maintain, test its navigation and evidence links, and mark missing or stale coverage explicitly; a giant stale inventory creates false confidence.

## Make the data boundary observable

An agent cannot recover information that its data path never exposes. Treat data architecture as part of the harness contract, not as passive storage:

- derive storage, indexing, retrieval, and retention from the agent's real access patterns and update cadence
- map decision-critical claims to sources and expose provenance, freshness, permissions, and coverage to the agent and verifier
- distinguish negative evidence from missing data, permission filtering, stale data, and retrieval failure
- test missing, stale, conflicting, and partially available inputs; require abstention or escalation when the evidence boundary cannot support the claim

More context tokens do not repair a blind or unobservable data pipeline.

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
- freeze the task contract and rubric before workers run; keep candidate work independent and judge anonymized outputs when comparing them
- let a parent compare evidence, resolve conflicts, and decide what enters durable memory
- prevent one worker from modifying the evaluator or another worker's evidence
- treat model agreement as a clue, not ground truth; adjudicate disagreements with decisive evidence or a named human checkpoint

Parallelism is useful only when outputs have independent acceptance and merge contracts, and the merge and verification costs remain lower than the saved time.

## Run self-improvement as research

1. **Mine weaknesses:** collect traces and verifier failures; distinguish symptoms such as timeout from causes such as context loss or bad planning.
2. **Bound edits:** name the prompts, workflow nodes, retrieval rules, tools, or scripts allowed to change.
3. **Propose narrowly:** target a recurring failure and list passing behaviors that must remain true.
4. **Evaluate:** use held-in cases for the target weakness and held-out cases for regression.
5. **Accept or reject:** require evidence, preserve rejected candidates and reasons, and keep rollback possible.
6. **Update memory:** promote only causal, reusable findings; do not turn one noisy win into a permanent rule.

Do not call a loop self-improving if it merely retries without persistent failure attribution, an editable boundary, or an acceptance criterion.

## Compile failures into durable rules carefully

Use a promotion pipeline instead of turning every incident into a permanent instruction:

```text
failure evidence
  -> root-cause attribution
  -> candidate rule or playbook item
  -> reproducible regression
  -> independent blind evaluation
  -> promote
  -> monitor
  -> retire or demote
```

Promote only a recurring failure or one high-consequence systemic failure whose cause, reusable boundary, and affected task class are clear. Require target cases, held-out regressions, clean negatives, preserved passing behavior, an owner, and a retirement trigger. Keep one-off symptoms in the error ledger. Retire or narrow a rule when it creates false positives, stale context, duplicated policy, or evaluator gaming.

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

## Earn autonomy by task class

Standing unattended autonomy belongs to a tested task class and evidence regime, not to an agent identity. The tiers separate authority; they are not sequential approval rituals for a task the user has already authorized:

| Tier | Authority |
|---|---|
| Observe / suggest | Inspect, reproduce, and propose; do not mutate. |
| Edit | Make bounded reversible changes; do not publish them. |
| Open PR | Publish a reviewable change with evidence. |
| Self-verified PR | Run the closed verifier loop and attach revision-linked evidence. |
| Auto-merge low-risk | Merge only a qualified, bounded task class with recovery and audit controls. |

Promote using repeated evidence about defect escape, false confidence, verifier coverage, rollback or recovery, blast radius, and auditability—not throughput alone. Preserve sampled review after promotion. Demote after a surprise, evaluator gap, stale feature map, or material context change; keep judgment-heavy and hard-to-reverse classes behind explicit human approval.

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
Verifier closure / human-verification debt:
Feature-map version and freshness:
Verifier, held-out set, and regressions:
Improvement and rollback rules:
Autonomy tier by task class:
Evidence packet, defect escapes, and sampled review:
Human checkpoints:
Next experiment:
```

Sources: Lilian Weng, “Harness Engineering for Self-Improvement,” Lil'Log, 2026-07-04; Andrew Ng, [“AI Engineering Skills Map: Software engineering fundamentals”](https://x.com/AndrewYNg/status/2093388974194872781), 2026-08-29.
