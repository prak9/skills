# Instruction And Model Migration

Use this reference when a base model, reasoning profile, harness, tool surface, or context system changes and existing prompts, skills, or repository instructions may no longer be the best control surface. Do not run this audit for ordinary tasks.

## Preserve the product contract

Before changing instructions, separate what the system must preserve from how an older model was told to achieve it:

- target outcome and supported task class;
- necessary project or domain facts;
- permissions and externally visible side-effect boundaries;
- completion and acceptance evidence;
- compatibility, safety, and other non-negotiable constraints.

These are the contract. A fixed sequence, repeated reminder, formatting ritual, or broad approval pause is only an implementation choice unless deviation would violate that contract.

## Inventory instructions by role

Classify each instruction under review:

| Role | Default treatment |
|---|---|
| Project or domain fact | Preserve while current; place at the narrowest applicable scope. |
| Permission or safety boundary | Preserve unless the real authority model changes. |
| Completion or evidence criterion | Preserve the observable requirement; allow the model to choose the path. |
| Local convention | Preserve only where consistency has concrete value. |
| Model workaround | Re-test after a model or harness change; remove or narrow when no longer useful. |
| Duplicate, conflicting, or stale rule | Resolve before adding another instruction. |

Record evidence, affected task class, and a retirement trigger for non-obvious model workarounds. Do not require lifecycle metadata for obvious project facts or stable safety boundaries.

## Run the migration as a controlled comparison

Use three checkpoints when practical:

1. **Old baseline:** old model and old instructions.
2. **Model-only baseline:** new model with the old instructions and the same effective reasoning, tools, permissions, and evaluator.
3. **Instruction candidate:** new model with the smallest instruction set that preserves the product contract.

The model-only baseline isolates the model change. The instruction candidate exposes rules that became unnecessary or harmful. If the old model remains supported, also run the candidate instructions on that model before changing a shared repository rule.

Change one instruction or tightly related rule family per attributed comparison. Do not change the evaluator, cases, model, reasoning profile, and prompt in the same comparison and then assign credit to one of them.

## Evaluate observable behavior and cost

Use representative development cases plus untouched acceptance cases. Include clean negatives that should not trigger the skill or rule. Record at least:

- task success and defect escape;
- premature stopping and unnecessary follow-up questions;
- required and forbidden skill activation;
- permission violations and external mutations;
- reference reads, tool calls, retries, and verification breadth;
- latency, tokens, or another stable cost measure when available;
- model, reasoning profile, harness, instruction revision, case-set version, and evaluator identity.

Do not accept a shorter prompt merely because it is shorter. Accept it when it preserves or improves the required behavior and removes measurable overhead, false triggers, conflicts, or maintenance cost. A quality gain may justify more work; record the tradeoff.

## Promote, narrow, or retire

- Promote a new permanent instruction only for a recurring failure or one high-consequence systemic failure with a reproducible cause.
- Prefer the narrowest scope that covers the affected task class.
- Retire or demote a workaround when the target failure no longer reproduces and holdouts do not regress.
- Keep a rule when it protects weaker models that are still supported, or route model-specific guidance explicitly instead of silently breaking them.
- Never turn “audit instructions after a model change” into “audit instructions before every task.”

## Handoff

Report the model and instruction baselines, cases and holdouts, changed rule family, behavioral and cost deltas, preserved contract, regressions, accepted or rejected candidate, and next review or retirement trigger. Keep raw run records outside the instruction files.
