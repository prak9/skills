# Clean Contract

Clean is a periodic compression and alignment pass over durable planning state. It reduces the state needed to resume work without deleting facts, evidence, or useful history.

## Triggers

Use Clean when one of these materially impairs recovery:

- when accumulated nodes or consequential runs make recovery materially harder; use a numeric cadence only if the project explicitly sets one;
- when `program.md`, the active task, `memory.md`, or referenced living docs duplicate, contradict, or obscure the current state;
- when a plan exceeds its context budget or added concepts no longer earn their maintenance cost;
- when generated output is no longer traceable from intent through change and evidence, or the owner cannot explain the active system well enough to re-judge it;
- during Loop `Reflect` when stale hypotheses or repeated attempts make the next action harder to recover.

Do not run Clean on every update or create metadata for an already concise, consistent Lite plan. Handoff and terminal transitions need a state consistency check, not an extra cleanup ceremony. Existing plans with `Clean state` / `Last clean` remain compatible: an outstanding `Due` must be resolved, and an opted-in terminal plan still records a dated pass or `N/A`. `Not run` is not evidence of a completed check.

## Procedure

1. Scan `program.md`, the active task, `memory.md`, and only the referenced living docs or evidence needed to reconcile current state.
2. Re-establish authority: one owner for each status, decision, constraint, next action, and evidence pointer.
3. Distill repeated observations into the smallest decision or finding that still changes future work.
4. Retire stale or superseded state with a stable-ID pointer and reason; remove duplicate prose and completed operational detail already preserved by evidence.
5. Update cross-references and any existing Clean metadata, then run strict validation. When explicitly adopting tracked Clean, add both fields together.

## Preserve And Retire

Preserve:

- outcome, locked constraints, acceptance criteria, current blocker, and next action;
- the replayable path from intent to change, sensor, evidence, decision, and residual risk;
- stable `D-*`, `F-*`, and `RUN-*` IDs that still affect work;
- every triggered `R-*` reflection with its scope, evidence, wrong/right feedback, and successor or distillation pointer;
- raw code, tests, CI, logs, external records, and links needed to verify a claim;
- the reason and successor pointer for a superseded decision or finding.

Retire or compress:

- duplicated status views, ordinary progress, chat narrative, and raw logs already represented by evidence; do not treat unique `R-*` learning as ordinary progress;
- stale hypotheses, obsolete next steps, and superseded entries after their replacement is linked;
- abstractions, sections, or concepts whose only justification is possible future use.

Never rewrite raw evidence to make the plan look cleaner. Markdown summarizes and points to evidence; it does not replace it.

## Completion Bar

Clean is complete only when:

- authoritative plan, task, memory, and referenced living docs agree;
- work can resume from `program.md`, the active task, and only their referenced memory/evidence;
- a responsible owner can explain and re-judge the active result without reconstructing hidden chat history;
- stable IDs and evidence links still resolve, with no material fact silently lost;
- duplicate or stale state is removed or explicitly retired;
- line count, retrieval surface, and concept count do not increase except for triggered reflection entries or another concrete reason;
- `scripts/validate_plan.py --strict <project-root>` passes.

For opted-in metadata, set `Clean state` to `Not due` and `Last clean` to a date plus evidence pointer, or `N/A` after a no-op check. Existing `N/A: <concrete reason>` records remain valid. Do not add those fields solely to close an otherwise aligned Lite plan.
