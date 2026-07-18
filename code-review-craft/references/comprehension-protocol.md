# Code Comprehension Protocol

Use this protocol when the code is unfamiliar, crosses files or services, or carries material risk. Stop reading only when the explain-back gate can be passed with evidence.

## Read in layers

1. **Repository contract:** read `AGENTS.md`, `CLAUDE.md`, contributor guidance, manifests, and relevant architecture notes.
2. **Change boundary:** inspect the base, diff, renamed files, generated files, dependency changes, and configuration changes.
3. **Whole files:** read each changed file in full. A correct-looking hunk can violate setup, cleanup, ordering, or file-level invariants.
4. **Call graph:** find direct callers, callees, implementations, interfaces, callbacks, event consumers, and public exports.
5. **Data and state:** locate schemas, migrations, serialization, caches, state machines, transactions, and ownership rules.
6. **Behavioral evidence:** read existing tests before judging coverage; inspect fixtures, failure assertions, logs, metrics, and runtime configuration.
7. **History:** use blame or prior commits only when intent, a surprising pattern, or a compatibility constraint remains unclear.

Prefer `rg` and repository-native navigation. Do not infer behavior from a filename or function name when the implementation is available.

## Build five maps

### Control-flow map

Record entry, branch conditions, calls, loops, async boundaries, exit paths, and error propagation. Check whether every acquired resource and partially completed operation has a matching cleanup or recovery path.

### Data-flow map

Track origin, validation, normalization, transformation, storage, and exposure. Mark trust changes and lossy conversions. Verify units, encodings, time zones, nullability, numeric precision, and default values.

### State map

List valid states and transitions. Check duplicate delivery, retry, cancellation, timeout, interruption, reordering, and restart. For concurrent code, identify the synchronization or idempotency mechanism rather than assuming one exists.

### Dependency map

Separate project-owned behavior from framework, library, service, database, and operating-system behavior. Verify uncertain dependency semantics from installed code or primary documentation when the review depends on them.

### Observability map

Determine how success, degradation, and failure become visible. Inspect return values, exceptions, logs, metrics, traces, alerts, audit records, and user-facing errors. A failure that cannot be detected or diagnosed is an operational defect even when the happy path works.

## State the invariants

Write invariants in falsifiable form:

- every accepted request produces at most one charge;
- a failed migration leaves the old schema readable;
- authorization is checked before data lookup;
- cancellation releases the lock and preserves durable state;
- cache content never outlives the source version it represents.

Avoid vague statements such as “the flow is safe.” Name the property, scope, and failure condition.

## Pass the explain-back gate

Explain the system without paraphrasing every line:

```text
Purpose and contract:
Entry points and callers:
Input and validation:
Control and state transitions:
Outputs and side effects:
Invariants and trust boundaries:
Failure, retry, and recovery:
Observability:
Material uncertainty:
```

Use concrete names from the code. If a field, branch, or dependency remains unexplained and could change the verdict, continue reading.

## Probe the hard boundaries

Choose probes that fit the system:

- zero, one, maximum, overflow, negative, null, missing, malformed, and duplicate input;
- first run, repeated run, upgrade, downgrade, restart, and partial rollout;
- timeout before and after the irreversible step;
- concurrent create/update/delete and out-of-order events;
- dependency returns stale, partial, slow, malformed, unauthorized, or successful-but-not-durable results;
- clock changes, time zones, encoding boundaries, locale, precision, and large payloads;
- permission changes between check and use;
- cleanup failure after the primary operation succeeds or fails.

Do not run a large generic checklist blindly. Select the few boundaries that threaten the named invariants.

## Avoid false comprehension

Reject these shortcuts:

- “The diff is small, so the risk is small.”
- “The tests pass, so the behavior is correct.”
- “This resembles a familiar pattern, so the framework handles the rest.”
- “The Agent wrote the implementation, so reviewing the summary is enough.”
- “I can describe each function, so I understand the system.”

Comprehension means predicting behavior under changed conditions and explaining why, not recognizing syntax.
