# Sketch And Judge Rubric

## Candidate Design Package Template

Keep each candidate sketch concise (typically 60–150 lines) so competing options are directly comparable:

```markdown
### Option <A/B/C>: <Short Name>
- **Core bet:** <one sentence on the central structural choice>
- **Caller sketch:** <5–15 lines of real usage>
- **Core types & public signatures:** <actual target-language types/signatures, no bodies>
- **Invariants enforced by construction:** <what bad states become unrepresentable>
- **Weak-model failure mode:** <how a hurried/weaker coding agent is most likely to misuse this API>
- **What this intentionally sacrifices:** <explicit tradeoff>
```

## Cross-Judge Scoring Dimensions

Judge each candidate on evidence, not eloquence:

1. **Module depth (Ousterhout):** Small, clear public surface hiding substantial complexity? Penalize shallow pass-through wrappers and parameter-bag APIs.
2. **Invalid states unrepresentable:** Do types/data structures prevent misuse, or does correctness rely on callers remembering prose rules?
3. **Caller ergonomics:** Does the common case read cleanly in 3–10 lines without boilerplate or leaked internal lifecycle?
4. **Weak-model resilience:** Can a coding agent use this interface correctly from its signature and types alone, without reading implementation internals?
5. **Change & failure containment:** If requirements shift or a dependency fails, is the blast radius localized to this module?
6. **Testability without white-box mocks:** Can callers and implementations be verified through the public contract with real or minimal local substitutes?

## Architectural Red-Flag Checklist

Flag any candidate that exhibits:
- Boolean/mode flags multiplying combinations (`doThing(x, true, false, null)`);
- Parallel state that callers must keep in sync manually;
- Stringly-typed protocols or `any`/`dict[str, Any]` crossing module boundaries where a concrete union/struct fits;
- Error swallowing or ambiguous return values (`None` meaning both "not found" and "failed");
- Speculative plugin/extension layers with only one real caller today.

## Synthesis Discipline

- Pick the simplest winning core; borrow an element from another candidate only if it fits cleanly without adding concepts.
- Record **why** the runner-up was rejected in 2–3 lines so future engineers (and `$how` / `$correct`) preserve the decision context.
