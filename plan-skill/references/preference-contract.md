# Preference And Tradeoff Contract

Use this contract when several valid solutions differ on a tradeoff, an inferred preference could change implementation, or a requested method may conflict with the underlying objective. A plan is not only a sequence of actions; it is an objective plus the bounds within which the agent may optimize.

## Find The Crux

1. Read repository instructions, rules, skills, specs, and accepted decisions before asking for preferences already recorded there.
2. Identify the one to three decisions or assumptions that could materially change architecture, cost, latency, safety, scope, acceptance, or whether to proceed.
3. Separate discoverable facts from human preferences. Research facts; ask only for judgment that cannot be inferred safely.
4. When judgment is missing, ask one Socratic question at a time and present the concrete tradeoff. Stop when the solution space is bounded enough to proceed.

Do not turn preference discovery into a questionnaire. If two choices lead to effectively the same implementation, the preference is not planning state.

## Classify Material Preferences

Classify only preferences that change execution:

| Axis | Values | Planning rule |
|---|---|---|
| Scope | Strategic / Tactical | Inherit firm or repository defaults; record project-specific priorities or overrides in the program. |
| Form | Declarative / Imperative | State the outcome and bound when the method is open; lock the method only where path sensitivity or standardization matters. |
| Strength | Locked / Negotiable | Escalate before violating a lock; delegate choices inside negotiable space. |

- **Strategic** preferences apply across projects and normally live in repository instructions, rules, or skills. Reference them instead of copying them into every plan.
- **Tactical** preferences apply to this project or task. They may specialize a strategic default; do not silently contradict one.
- **Declarative** preferences name what to optimize and include any threshold that makes an otherwise acceptable result fail. Leave implementation freedom where multiple methods can meet the objective.
- **Imperative** preferences prescribe a method, interface, sequence, or process. Use them for the critical, fragile, high-stakes, or deliberately standardized part of the work, not as a default for every detail.

Treat the common “critical minority imperative, remainder declarative” split as a heuristic, not a quota.

## Build The Contract

Record the smallest useful preference contract:

- **Strategic defaults:** authoritative repository or firm preferences that apply.
- **Tactical objective:** the project-specific outcome or quality to optimize when valid solutions differ.
- **Imperative bounds:** non-negotiable method, interface, threshold, or process, paired with its rationale.
- **Negotiable space:** choices the agent may make without approval.
- **Material assumptions:** inferred preferences whose failure would change the plan.
- **Escalate when:** a preference conflicts, a bound must move, or evidence reveals an option materially better at the stated objective.

Use stable `PREF-*` IDs in Full only when tasks must reference several preferences or a preference decision must survive handoff. Keep a Lite contract inline.

## Resolve Tension

- Rank the tradeoff instead of asking for an unqualified “best” design. Add measurable bounds when words such as fast, safe, scalable, or simple could admit materially different answers.
- Pair an imperative bound with the objective it serves. If the prescribed path appears dominated on that objective, surface the alternative and its evidence; do not silently override the bound.
- Let a tactical preference override a strategic default only when the authority to do so is explicit. Otherwise record the conflict and escalate.
- Omit speculative future features. Preserve only the present interface or invariant that future interoperability actually requires.
- In Loop mode, make the verifier measure the declared objective and make reflection revisit any assumption or preference contradicted by evidence.
