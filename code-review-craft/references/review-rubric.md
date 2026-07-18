# Evidence-Based Review Rubric

Select dimensions according to the review contract. Do not give every dimension equal weight and do not report a checklist item without a concrete failure path.

## Correctness and compatibility

- Compare behavior with the requirement, caller expectations, and established invariants.
- Check boundary values, condition polarity, ordering, defaults, nullability, and error semantics.
- Trace partial success, cleanup, retry, cancellation, and rollback.
- Check public API, serialized data, schema, command-line, configuration, and event compatibility.
- Distinguish a changed contract from an accidental regression; require migration or rollout support when both versions can coexist.

## State, concurrency, and distributed behavior

- Identify the consistency model and owner of each state transition.
- Check atomicity across database, cache, queue, file, and external-service boundaries.
- Verify idempotency keys, deduplication scope, lock lifetime, retry budget, timeout, and backoff.
- Test duplicate, delayed, reordered, concurrent, and replayed work.
- Check time-of-check/time-of-use gaps and whether cancellation can leave orphaned work.

## Security and privacy

- Trace untrusted input through parsing, validation, authorization, storage, logging, and output.
- Check authentication and authorization separately; enforce authorization at the protected resource boundary.
- Look for injection, traversal, unsafe deserialization, SSRF, open redirect, secret exposure, weak randomness, and unsafe cryptography.
- Verify tenant isolation, least privilege, sensitive-data minimization, retention, and auditability.
- Treat fail-open behavior, ambiguous defaults, and security checks after side effects as high risk.

## Data and migrations

- Check schema compatibility, migration order, backfill behavior, indexes, constraints, and rollback feasibility.
- Verify units, rounding, numeric precision, encoding, locale, time zones, and timestamp semantics.
- Check whether old and new binaries can operate during a rolling deployment.
- Require explicit handling for null, missing, corrupt, duplicated, and legacy data.
- Estimate blast radius before destructive writes; verify backups or recovery mechanisms when relevant.

## Reliability and operability

- Check timeout, retry, circuit breaking, resource limits, queue growth, and graceful degradation.
- Verify that errors preserve useful context without leaking secrets.
- Confirm logs, metrics, traces, alerts, and audit records distinguish success, expected rejection, retryable failure, and terminal failure.
- Check startup, shutdown, cleanup, restart, and partial dependency failure.
- Examine rollout, feature flag, canary, rollback, and ownership for high-risk changes.

## Performance and resource use

- Find unbounded loops, recursion, allocation, buffering, fan-out, and cache growth.
- Check algorithmic complexity, N+1 I/O, repeated serialization, unnecessary copies, and blocking on async paths.
- Evaluate performance against realistic cardinality and worst credible input, not toy fixtures.
- Treat a cache as a consistency mechanism as well as an optimization; inspect invalidation and memory limits.
- Demand measurement for optimization claims and avoid speculative micro-optimization findings.

## Maintainability and architecture

- Check whether responsibilities, ownership, and invariants remain legible.
- Prefer the repository's existing patterns and dependencies unless the change has a concrete reason to depart.
- Flag abstraction when it hides behavior, multiplies change surfaces, or makes invalid states easier to express.
- Flag duplication only when it can drift or already encodes the same rule inconsistently.
- Check naming, comments, and types for semantic accuracy, not personal taste.
- Evaluate whether the difficult version of the problem was solved or merely pushed onto callers and operators.

## Tests and validation

- Require a regression test for a fixed defect when practical; verify it would fail before the fix.
- Cover behavior, boundaries, negative paths, state transitions, and externally visible contracts.
- Inspect assertions for strength. A test that only checks “no exception” may prove little.
- Check fixture realism, isolation, deterministic timing, and whether mocks preserve the dependency semantics under review.
- Use integration or end-to-end evidence where correctness depends on wiring, transactions, serialization, permissions, or process boundaries.
- Note missing validation separately from a proven defect. Do not claim the untested behavior is broken without evidence.

## Finding quality gate

Before reporting a finding, answer:

```text
What exact input or state triggers it?
Which code path permits it?
What invariant or requirement does it violate?
What observable consequence follows?
How likely is that path in the intended environment?
What evidence could disprove the claim?
What is the narrowest safe fix direction?
```

Reject the finding if these answers remain vague after reasonable inspection.
