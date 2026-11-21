---
name: architect
description: Design system boundaries, data structures, and public interfaces through grounded exploration, multi-option interface/type sketches, independent cross-judging, and empirical scrap-and-redo criteria. Use for new subsystems, service boundaries, shared libraries, or major refactors; not for small local bug fixes or prose-only task checklists.
---

# Architect

Spend human and senior-agent judgment on boundaries, data structures, and interfaces—not on verbose upfront implementation plans. Trace every system the change touches, sketch competing shapes before writing code, pick the shape where **each piece of state has one owner, each task has one way to do it, and callers need to know least**, and scrap the sketch immediately if implementation evidence disproves it.

## Scope Gate

Use for `/architect`, `"architect this"`, `"design this"`, or non-trivial work (new subsystem, public API, shared package, cross-module boundary, major refactor) where jumping straight to code would lock in the wrong shape. Skip for local single-file fixes where boundaries are already clear.

## Five-Step Closed Loop

### 1. Ground The Problem
Trace every system the change touches before sketching (use `$how` for unfamiliar subsystems, and check `git log`/docs for historical *why*). Summarize:
- What job this boundary owns and what it explicitly does NOT own;
- Existing callers, state owners, data flow, failure modes, and non-negotiable constraints;
- Open unknowns best settled by a tiny throwaway prototype instead of guessing.

### 2. Sketch Competing Shapes (2-Sketch Default / Arena for Large or Contested Designs)
Do not accept the first shape by default. Each candidate package contains **only** the contract layer (caller sketch, core data structures/types, public signatures, error semantics, and a short rationale naming alternatives considered and rejected—no full implementation).

- **Standard boundary:** sketch **two materially different shapes** and compare them directly.
- **Large or contested design (Arena mode):** run the full **Frame → Fan out → Cross-judge → Pick a base → Graft** loop from [sketch and judge rubric](references/sketch-and-judge.md):
  1. **Frame:** derive 3–6 concrete, gradeable criteria for *this* task as the picker's rubric (**candidates see only the task and shared grounding, not the rubric**). Give each candidate an isolated output path (worktree or scratch dir).
  2. **Fan out:** spawn `N` parallel candidates in one turn (across distinct models when available); if one drops out, proceed with `N-1` and note it.

### 3. Cross-Judge, Pick A Base, And Hand-Graft
Score every candidate **criterion by criterion** (not holistic feel), pairing your read with an independent read-only cross-judge (preferring a different model/vendor when available) scored by path label:
- **Agreement** confirms the base; **disagreement** signals bias or an ambiguous rubric—read both rationales before deciding.
- **Pick the base** a future maintainer can extend most easily without breaking invariants; on a tie, prefer the cleaner boundary or smaller API.
- **Hand-graft** 1–2 concrete strengths from losing candidates under one coherent mental model (never paste mechanically).
- **Convergence vs. wild divergence:** if candidates converge on one shape, ship the consensus with no graft; if they wildly diverge, Framing was under-specified—**reframe and re-run** rather than averaging the divergence.

Present the winning sketch and decisive tradeoffs for human review before broad implementation when the boundary is high-impact or irreversible.

### 4. Implement Against The Sketch
Replace sketch placeholders with real implementation and stay in the loop as it fills in. Treat every deviation from the sketch as a signal: if a function suddenly needs unexpected parameters, hidden shared state, or extra flags, surface that drift explicitly instead of silently patching around it.

### 5. Scrap When Empirical Evidence Disproves The Design
Never defend a bad sketch with sunk-cost patches. **Scrap and redesign from Step 1/2** if implementation triggers any empirical failure signal:
- The same ad-hoc workaround appears across multiple unrelated call sites;
- The type system forces escape hatches (`any`, unsafe casts, suppression comments) to make callers compile;
- Callers must know internal ordering or lifecycle details that the boundary was supposed to hide;
- Mocking or testing the boundary requires reproducing its internals.

## Output
Deliver: (1) Grounding brief & constraints, (2) Winning interface/type sketch + caller example, (3) Synthesis note (chosen base and why, cross-judge verdict or skipped reason, each graft with source candidate, rejected alternatives, any convergence or dropouts), (4) Open prototype checks (if any), and (5) Explicit scrap triggers to watch during implementation.
