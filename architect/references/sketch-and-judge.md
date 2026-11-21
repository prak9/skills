# Sketch, Arena, And Cross-Judge Rubric

## Candidate Design Package Template

Keep each candidate sketch concise (typically 60–150 lines) so competing options are directly comparable:

```markdown
### Option <A/B/C>: <Short Name>
- **Core bet:** <one sentence on the central structural choice>
- **Caller sketch:** <5–15 lines of real usage>
- **Core types & public signatures:** <actual target-language types/signatures, no bodies>
- **State ownership & invariants:** <who owns each piece of state; what bad states become unrepresentable>
- **Weak-model failure mode:** <how a hurried/weaker coding agent is most likely to misuse this API>
- **Considered & rejected:** <alternatives considered and why rejected>
```

## Arena Framing & Isolation Rules (For Large / Contested Designs)

1. **Blind rubric:** write 3–6 task-specific, gradeable criteria before fan-out, and keep them with the picker/judge only. Candidates receive only the task, shared grounding path, and their isolated output path (a git worktree where possible, otherwise `/tmp/arena-<slug>/candidate-<n>/`).
2. **Parallel fan-out:** launch all candidates in one turn. Record dropouts explicitly and continue with `N-1` if at least two candidates return.
3. **Independent cross-judge:** spawn one read-only judge (preferring a different model/vendor from the parent when available) to score each candidate **by path label** on every rubric criterion and recommend a base.

## Default Scoring Dimensions

Adapt 3–6 criteria to the task; default dimensions are:

1. **Single state ownership:** does every piece of state have exactly one clear owner?
2. **One way to do it:** is there one obvious, idiomatic path for each task without competing APIs?
3. **Minimal caller knowledge (Ousterhout deep module):** small, clear public surface hiding substantial complexity? Penalize shallow pass-through wrappers and parameter-bag APIs.
4. **Invalid states unrepresentable:** do types/data structures prevent misuse, or does correctness rely on callers remembering prose rules?
5. **Weak-model resilience:** can a coding agent use this interface correctly from its signature and types alone, without reading implementation internals?
6. **Change containment & testability:** localized blast radius and testable through the public contract without white-box mocks?

## Architectural Red-Flag Checklist

Flag any candidate that exhibits:
- Boolean/mode flags multiplying combinations (`doThing(x, true, false, null)`);
- Parallel state that callers must keep in sync manually;
- Stringly-typed protocols or `any`/`dict[str, Any]` crossing module boundaries where a concrete union/struct fits;
- Error swallowing or ambiguous return values (`None` meaning both "not found" and "failed");
- Speculative plugin/extension layers with only one real caller today.

## Pick, Hand-Graft, And Divergence Rules

- **Criterion-by-criterion pick:** read every candidate end to end and score each criterion before comparing with the cross-judge. If you and the cross-judge disagree on the base, re-read both rationales to resolve bias or rubric ambiguity before deciding.
- **Tie-breaker:** prefer the cleaner boundary or smaller API surface.
- **Hand-graft (not paste):** inspect losing candidates once more for 1–2 strengths worth porting; redesign each graft into the winning base under one coherent mental model.
- **Convergence:** if candidates independently converge on one shape, ship the consensus without forcing unnecessary grafts.
- **Wild divergence:** if candidates solve fundamentally different problems, Framing was under-specified—reframe and re-run rather than averaging incompatible designs.
- **Post-verify feedback:** if verification or implementation uncovers a flaw the arena missed, either Framing was wrong (reframe) or a losing candidate caught it and the graft was missed—do not paper over it.
