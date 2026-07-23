# Pre-Execution Grill And Readiness Gate

Use this gate to prevent fast execution from creating a persuasive but low-information false-positive loop.

```text
Research context -> Grill one judgment at a time -> Write the readiness map
-> Ready / Not required -> Plan -> Execute -> Verify
```

AI may compress execution cost. Do not let it replace research taste, domain knowledge, or the human judgment that defines what is worth testing.

## Decide Whether The Gate Is Required

Set `Execution readiness` to `Blocked` and run the gate when any condition applies:

- the work is research, optimization, evaluation, strategy, experimentation, data/model work, migration, or another uncertainty-heavy Loop
- the central claim, baseline, data-generating process, evidence quality, pass threshold, or falsifier is unclear
- a quick implementation can produce a polished report, chart, demo, metric, or local improvement without proving useful information
- cost, capacity, scale, safety, irreversibility, or external commitments could change the decision
- the user holds material domain judgment that cannot be recovered from code, documents, or data

Set it to `Not required` only for a clear accepted spec with an observable verifier and no material hidden judgment. Replace the gate table with `N/A: <concrete reason>`.

## Research Before Asking

- Read the supplied sources, relevant code, tests, data notes, benchmarks, and prior failed attempts first.
- Separate facts that can be discovered from judgments only the user or domain owner can make.
- Ask for judgment, not information the agent can look up.
- State contradictions and missing evidence directly; do not convert ambiguity into plausible assumptions.

## Run The Grill

1. Keep `Execution readiness: Blocked`; do not start implementation nodes.
2. Ask one decisive question at a time so each answer can shape the next question.
3. Use 3-5 questions for a narrow uncertainty and up to roughly 20-30 for a deep research review. Stop by readiness, not by quota.
4. Write each material answer into `program.md#execution-readiness-gate` immediately.
5. Label the answer mentally as fact, preference, constraint, hypothesis, or falsifier; route durable items to the matching program section.
6. Challenge answers that conflict with evidence or leave the decision unchanged.
7. If a missing answer would materially change scope, method, or risk, remain `Blocked`. Default only when the choice is reversible and inside negotiable space.

Prefer questions from these groups:

- **Decision and claim:** What decision will this work change? What precise hypothesis is being tested?
- **Evidence:** How was the data generated? What leakage, selection, survivorship, staleness, or measurement failure is plausible?
- **Comparison:** What baseline, counterfactual, incumbent, or null result must the idea beat?
- **Economics and operations:** Which cost, capacity, latency, liquidity, scale, reliability, or maintenance constraint matters in reality?
- **Truth conditions:** What exact result counts as a pass? What observation would disprove the idea or make the work stop?
- **Extension:** If the claim survives, what non-obvious next test distinguishes a real mechanism from a local fit?
- **Taste:** Which judgment depends on lived domain experience, and who retains ownership of it?

Do not ask every question mechanically. Ask the smallest sequence that exposes the decisive assumptions and failure conditions.

## Fill The Readiness Map

When the gate is required, make every field concrete:

| Field | What it must capture |
|---|---|
| Decision this work informs | The action that changes if the result passes or fails |
| Claim / hypothesis | A falsifiable statement, not a theme or desired output |
| Baseline / counterfactual | The comparison that distinguishes improvement from noise |
| Evidence / data quality | Source, data-generating process, freshness, leakage, and known gaps |
| Real constraints | Cost, capacity, time, scale, safety, compatibility, or operational limits |
| Pass condition | A pre-registered threshold tied to the decision |
| Falsifier / stop condition | Evidence that kills, pauses, or redirects the idea |
| Cheapest informative check | The smallest test that can change belief before full execution |
| False-positive loop | The tempting busywork or polished output that could feel like progress without adding information |
| Human judgment retained | The taste/domain decision AI must not silently make |

Set `Execution readiness` to `Ready` only when all fields are concrete, contradictions are resolved or explicitly bounded, and the cheapest informative check is the first relevant node. A generated artifact, completed implementation, or attractive metric is not readiness evidence by itself.

## Keep The Loop Informative

- Pre-register the baseline, pass condition, and falsifier before running the test.
- Prefer a check that can kill the idea over a broad implementation that can only produce more output.
- On every Loop reflection, ask: “What new information changed the plan?” If the answer is none, stop local optimization and revisit the readiness map.
- Treat an invalidated favorite idea as a successful research outcome when the falsifier was sound.
