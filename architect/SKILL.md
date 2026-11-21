---
name: architect
description: Design system boundaries, data structures, and public interfaces through grounded exploration, multi-option interface/type sketches, independent cross-judging, and empirical scrap-and-redo criteria. Use for new subsystems, service boundaries, shared libraries, or major refactors; not for small local bug fixes or prose-only task checklists.
---

# Architect

Spend human and senior-agent judgment on boundaries, data structures, and interfaces—not on verbose upfront implementation plans. Design through concrete type/interface sketches, test competing options, and scrap the sketch immediately when implementation evidence disproves it.

## Scope Gate

Use when introducing a new subsystem, public API, shared package, cross-module boundary, or high-risk refactor. Skip for local single-file fixes where boundaries are already clear.

## Five-Step Closed Loop

### 1. Ground The Problem
Before proposing any design, inspect the affected codebase to establish real responsibilities, invariants, call sites, and historical constraints (use `$how` if the subsystem is unfamiliar, and check `git log`/docs for *why* current boundaries exist). Summarize:
- What job this boundary owns and what it explicitly does NOT own;
- Existing callers, data flow, failure modes, and non-negotiable constraints;
- Open unknowns that require a quick throwaway prototype instead of guessing.

### 2. Interface Sketch Arena
Do not accept the first design by default. Generate **2–3 materially different design packages** (using parallel subagents—ideally across distinct model perspectives when available—or cleanly isolated passes). Each candidate package contains **only** the contract layer, no full implementation:
- **Caller sketch:** realistic call-site code (or a short Tutorial snippet) showing how callers actually use it;
- **Core data structures & types:** key types, state representations, and invariants;
- **Public function/method signatures** and error semantics;
- **Tradeoff brief:** interface depth (deep module vs. shallow pass-through), failure modes on weaker models, and red-flag self-check (see [sketch and judge rubric](references/sketch-and-judge.md)).

Resolve genuinely uncertain runtime/API questions with tiny **throwaway prototypes** rather than debating abstractions on paper.

### 3. Independent Cross-Judge & Synthesize
Have an independent reviewer pass (or distinct model subagent) evaluate all candidate sketches against [the rubric](references/sketch-and-judge.md):
- Compare concept count, caller ergonomics, invalid-state prevention, testability, and blast radius.
- Synthesize one winning sketch (cherry-picking verified strengths only when coherent—never frankensteining incompatible abstractions).
- Present the winning sketch and decisive tradeoffs for human review before broad implementation when the boundary is high-impact or irreversible.

### 4. Implement Against The Sketch
Replace sketch placeholders with real implementation. Treat every deviation from the sketch as a signal: if a function suddenly needs unexpected parameters, hidden shared state, or extra flags, surface that drift explicitly instead of silently patching around it.

### 5. Scrap When Empirical Evidence Disproves The Design
Never defend a bad sketch with sunk-cost patches. **Scrap and redesign from Step 1/2** if implementation triggers any empirical failure signal:
- The same ad-hoc workaround appears across multiple unrelated call sites;
- The type system forces escape hatches (`any`, unsafe casts, suppression comments) to make callers compile;
- Callers must know internal ordering or lifecycle details that the boundary was supposed to hide;
- Mocking or testing the boundary requires reproducing its internals.

## Output
Deliver: (1) Grounding brief & constraints, (2) Winning interface/type sketch + caller example, (3) Key rejected alternative and why, (4) Open prototype checks (if any), and (5) Explicit scrap triggers to watch during implementation.
