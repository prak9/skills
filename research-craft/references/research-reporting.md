# Research Reports That Can Be Used And Challenged

For standard/deep source research, deliver a complete report, not only an executive summary. Select the shape for the reader's question; respect an explicitly requested format. Headings and block order can change, but the substantive contract below cannot disappear through compression. Brief requests stay brief; chat-only changes the destination, not the requested depth.

## Inputs And Delivery Weight

A natural-language question is sufficient input. Recover audience, purpose, scope/period, supplied sources, prior work, budget and output preferences from context; do not demand a completed form or invent missing budgets. Ask only about consequential choices that cannot be resolved from available evidence.

| Delivery | When | Artifacts |
|---|---|---|
| Inline | Brief or explicitly chat-only | Requested answer/full analysis, citations, counterevidence and verification limits in chat |
| Lean report — default | Standard/deep research without an audit requirement | `report.md` and `memo.md`; source locators, calculations, checks and reopening conditions in the report appendix or existing records |
| Audit package | Explicit machine-checkable evidence request, project requirement, or a concrete need for granular evidence handoff/repeated updates | Native package or equivalent existing schema; explain the need briefly, not a new approval gate |

Preserve necessary source excerpts, raw measurements and failed attempts in every mode; lean delivery means fewer administrative files, not weaker evidence. Split out notes/data when they would obscure the report or be lost on resumption. Do not create blank CSVs, hash receipts or stand-alone status files for a lean report. Do not convert an explicitly requested audit package to lean merely to avoid a failing check.

## Choose A Genre

| Genre | Body must accomplish | Typical useful structure |
|---|---|---|
| `qa` | Resolve connected questions and synthesize their joint implication | Summary → scope/background → question/answer sections → integrated finding → counterevidence/gaps |
| `explainer` | Explain the mechanism and its limits rather than list facts | Summary → needed terms → components and causal/operational path → worked example → variants/failure boundaries → what remains uncertain |
| `comparison` | Compare the same options on consistent axes and expose conditions that change the ranking | Context/constraints → options matrix → evidence and full costs → tradeoffs → conditional conclusion and reversal conditions |
| `decision` | Provide evidence for an explicitly requested real choice, using `decision` for the decision process | Decision/constraints → options and common-axis comparison → conditional recommendation → risks/reversal conditions → authorized next step |
| `landscape` | Give a defensible map, not an arbitrary list of familiar names | Scope/inclusion → categories → comparable profiles → relationships/value chain → trends/coverage limits → update triggers |
| `validation` | Judge a precise claim within a defined domain | Claim and falsifiers → supporting/opposing evidence → measurement/method critique → conditional verdict → what would change it |
| `custom` | Combine the needed functions without repeating sections | Name the chosen functions and check each against the question |

An action-oriented comparison can include a recommendation and a separate decision memo; it does not authorize making or executing the user's decision. An unresolved factual condition calls for a bounded conclusion, not a forced recommendation. Understanding-only research does not need an action plan.

## Common Delivery Contract

1. **Entry summary:** the actual answer, decisive conditions, strongest limitation or counterargument. Write last. Cite its load-bearing claims directly; it must be understandable without opening files.
2. **Scope/background:** what was studied, as-of boundary, why these distinctions matter, inclusions/exclusions and necessary context. Avoid padding with a general history.
3. **Genre-specific analysis:** explain relationships and mechanisms with relevant evidence. Mark whether a connection is observed, inferred or proposed. Identify the reference view before claiming a new or non-consensus insight.
4. **Counterevidence and limits:** strongest opposing case, why it changes or does not change the conclusion, consequential unknowns and conditions that would reverse the verdict. No fabricated objections or mandatory balanced sides.
5. **Implications:** what the findings change for the stated question/decision. Distinguish a research conclusion from an authorized user action. Include a next discriminating step only when useful.
6. **Evidence and verification:** claim-level links, source map with common origins/access limits, report date/version, checks actually performed and unverified scope. Never label a report fully verified from a structural pass.

For persisted standard/deep work, `memo.md` is the concise entry point and the full report is the evidence-based body. The memo may be an understanding summary rather than a decision memo. Do not force a fixed number of findings, numbers, pages or follow-up questions. Link both in the final chat, alongside the substantive answer.

For a worked lean explainer with real sources and explicitly hypothetical arithmetic, see [ablation report](../examples/ablation/report.md) and [memo](../examples/ablation/memo.md). It demonstrates reasoning and delivery, not measured Skill improvement. Adapt its argument structure to the question; do not copy its conclusions. The synthetic audit fixture in `evals/report-package/` serves a different purpose: exercising file contracts.

## Select Blocks By Their Job

| Block family | Use when it adds information | Guardrail |
|---|---|---|
| Frame | Scope, definitions, thesis, reader context, verification status | Do not relabel the user's goal |
| Explain | Mechanism, sequence, example, variants, failure modes, state/flow diagram | An analogy is not evidence; a diagram is not a causal proof |
| Compare | Common-axis matrix, costs, tradeoffs, reversibility, conditional choice | No invented weights or totals; show where rankings change |
| Map | Taxonomy, profiles, positioning, relationships, value chain, history | State inclusion/coverage; missing from search does not mean absent from the field |
| Validate | Falsifiers, evidence for/against, replication, base rates, methodology | Confidence follows support, not vote counts |
| Analyze | Timeline, bottleneck, dependency, residuals, before/after | Accounting differences and sequences alone do not identify causes |
| People | Actual stakeholder evidence, incentives, expertise and conflicts | Simulated personas are search lenses, not interviews |
| Numbers | Metrics, unit economics, market sizing, forecasts, historical series | Retain producer, date, unit, denominator and derivation; no unsupported precision |
| Context | Jurisdiction, geography, technology, history, institutions | Apply conditions to the conclusion rather than add an unrelated appendix |
| Close | Counterarguments, uncertainty, synthesis, reuse and update triggers | No forced action, permanent memory or extra research |

Choose the smallest useful visual: a common-axis table, mechanism diagram, timeline or distribution. Preserve units, denominators, missingness and underlying data. Use narrative for one fact or a simple chain. Do not multiply SWOT, scorecards and matrices that restate the same judgment.

## Synthesize And Challenge

Map sections to claims before drafting, revise the map when findings change, and keep exclusions visible. Pull only the section's evidence into its writing context; revisit original passages for disputes. Preserve important qualifiers in headings, tables, captions and memo, not just buried in a limitations section. Generalizations and derived mechanisms need an explicit inference, not a citation attached to an adjacent fact.

Use five challenge lenses proportionately: factual support, strongest rival, missing coverage, reader usability, and protected dissent. Record consequential defects and their resolution, not ceremonial grades. If another agent is authorized to check, give it actual evidence and the task contract, isolate its judgment from other reviewers, and disclose shared model/source limitations. Otherwise name the check self-review; role names do not make it independent.

When the report itself is the main deliverable, use the available `writing` skill for final expression, preserving citations, definitions, caveats and uncertainty. Then recheck the changed summary and claims. Do not launch code-review-craft for prose review.

## Export And Handoff

Markdown is the default editable source. Generate HTML/PDF/DOCX only when requested or already part of project delivery. Use existing rendering tools; do not install a document stack merely because upstream does. Verify produced files, section/table integrity, citations, footnotes and figures against the same evidence. Keep the memo separate. A successful conversion does not validate conclusions; a missing requested export remains an unfinished deliverable.

For explicit decision walkthroughs, present findings at each relevant fork and let the user decide. Record decided/deferred/blocked only from actual interaction; do not fabricate adoption or require a walkthrough for ordinary research completion.
