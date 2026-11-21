---
name: teach
description: Explain why a change, design, or subsystem works the way it does—comparing chosen approaches against alternatives, surfacing real tradeoffs, and grounding every claim in actual code and history. Use when asked to teach a mechanism, justify implementation tradeoffs ("why X instead of Y?"), or prove why a new approach beats an old one; not for multi-turn quizzing (use socratic-tutor) or standalone subsystem mapping (use how).
---

# Teach

Build a clear, honest mental model for the user—and cure premature model confidence by forcing real code and history inspection before explaining.

## Scope Gate

Use when the user asks to:
- understand why a solution was implemented one way instead of another (`why X and not Y?`);
- verify whether an agent's design or PR is trustworthy by inspecting its tradeoffs; or
- learn a concrete mechanism in the current codebase or diff with grounded evidence.

Do not use for multi-turn Socratic quizzing (`socratic-tutor`), textbook study sprints (`source-grounded-study`), or pure subsystem mapping without tradeoff/teaching focus (`how`).

## Rule 0: Ground Before Teaching

Never teach from memory, filenames, or assumptions. Before explaining:
1. **Read the actual code/diff** (use `$how` if the mechanism spans an unfamiliar multi-file subsystem).
2. **Check historical intent when relevant** (`git log -S`, `git blame`, commit messages, PRs, or design docs) to answer *why* existing constraints exist—code shows *what* happens, rarely *why* it was written that way.
3. **Verify claims against reality**: if a claim is inferred rather than observed in code or test output, label it explicitly as unverified.

## Two Modes

### 1. Tradeoff & Decision Audit ("Why X instead of Y?")
Structure the explanation around the actual engineering decision:
- **Core problem & constraints:** what invariant, failure mode, or cost drove the choice.
- **Chosen approach vs. strongest alternative(s):** concrete mechanism of each (no strawman alternatives).
- **Real tradeoffs:** what the chosen approach gains, what it sacrifices (complexity, latency, flexibility, coupling), and under what condition the alternative would win.
- **Code evidence:** exact file paths, symbols, and line ranges backing each claim.
- **Honest second look:** if reading the code reveals a flaw or a simpler alternative, say so plainly—never rationalize weak code to defend a prior turn.

### 2. Mechanism Walkthrough ("Teach me how X works")
- **Mental model first:** 1–2 sentences stating the core idea and why it exists.
- **Concrete end-to-end trace:** walk one real input/request through the key files and state transitions in plain prose (snippets only when essential).
- **Load-bearing invariants & gotchas:** what must stay true, what breaks if you violate it, and what would surprise a newcomer.

## Output Standard

Keep prose direct, concrete, and jargon-light. Lead with the mental model or verdict, cite exact files/lines, separate observed facts from inference, and end with the 1–2 sharpest constraints or open risks the reader should remember.
