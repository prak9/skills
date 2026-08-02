# Node Reflection Contract

Turn execution into a feedback loop. Close every completed atomic node and every decision checkpoint with an evidence-linked `R-*` reflection before selecting the next action.

## Close Every Node

After verification, record one reflection with this shape:

| Field | Requirement |
|---|---|
| Scope | Name the task and atomic node or decision checkpoint. |
| Evidence | Cite the verifier, run, diff, incident, or observation that supports the reflection. |
| Wrong / changed | State the failed expectation, retired assumption, unnecessary action, or `None: <why the expectation held>`. |
| Right / preserve | State the useful pattern and the boundary within which it should be repeated. |
| Next rule | Convert the lesson into a concrete change to the next action, verifier, constraint, or reusable rule. |

Do not advance to the next node until its predecessor has evidence and an `R-*` entry. A passing result still needs reflection: name what worked and why it should remain. A failed attempt or key decision gets a reflection even when no node closes.

## Separate Log From State

- In Lite, keep the authoritative `Reflection Log` in `program.md`; the Plan row points to its `R-*` entry.
- In Full and Loop, keep the authoritative `Reflections` ledger in `memory.md`; each completed task node points to its `R-*` entry.
- Keep status, evidence, and reflection in their existing authoritative locations. Do not copy progress prose into the reflection ledger.
- Record decision-relevant summaries, not a hidden chain-of-thought transcript. Preserve observable evidence, changed beliefs, and operational lessons without narrating private token-by-token reasoning.

## Make Feedback Useful

- Replace “this was wrong” with the expectation, the contradicting evidence, and the retired rule.
- Replace “this was right” with the successful pattern, its boundary, and the next context where it should be reused.
- Distinguish outcome luck from process quality. A passing test does not vindicate an unsupported assumption; a failed experiment can still validate a good falsification process.
- Update the plan immediately when a reflection changes scope, order, verifier, preference, or risk. If it changes a durable project rule, distill it into `D-*` or `F-*` and link the originating `R-*`.
- In Loop mode, create one `R-*` for every verified attempt; create `RUN-*` only for attempts whose raw execution details remain consequential.
- If reality contradicts a passing checker, record the escaped failure class and revise the acceptance or sensor contract. Do not reinterpret the same evidence as success.
- If a rubric, sensor, or holdout set changes, record it as a versioned harness decision and re-evaluate affected claims; do not hide evaluator drift inside an implementation reflection.

## Preserve Learning

Use stable, append-only `R-*` IDs. Clean may merge repeated lessons into a durable decision or finding and mark reflections as distilled or superseded, but it must retain each node's scope, evidence, wrong/right feedback, and successor pointer. Remove chat narrative and duplicated progress, not unique learning.
