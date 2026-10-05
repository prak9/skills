# Research Delivery Acceptance Cases

These are behavioral evaluation specifications, not recorded successful model runs. Use actual task traces and artifacts to judge them; do not score keyword presence as research quality. Compare variants on the same source/tool conditions and keep held-out tasks separate from instruction tuning.

| Case | Prompt / controlled condition | Required behavior / failure discriminator |
|---|---|---|
| Understanding, not a decision | “深入研究某技术的工作机制、适用边界和争议，给完整报告。” | Explainer with mechanisms, worked example, boundaries, evidence and memo; no forced action fork or downgrade because no purchase is pending |
| Complete output | “完整调研这个领域，按 deepdive 方式交付。” | Genre-appropriate report, memo and traceable evidence in the appropriate delivery weight, not just a five-line summary, search log or experiment template |
| Lean deep research | “深入解释机制与争议，保存完整报告即可。” | Complete report and memo with traceable evidence appendix; no automatic CSV/receipt scaffolding or reduction of analytical depth |
| Explicit audit output | “给完整机器可检查证据包。” | Native audit package or equivalent requested schema and its checks; do not substitute lean output to avoid validation |
| Common-axis comparison | Compare tools whose reported prices use different regions, editions and workload units | Normalize only compatible values; retain missing terms and conditional ranking; no fabricated comparable totals |
| One primary fact | A current official document directly defines a narrow versioned property | Adequate scoped answer without inventing three independent sources; no extrapolation from official price to product superiority |
| Protected dissent | Many secondary articles repeat one announcement; one original study contradicts a load-bearing claim | Recover origins and retain the dissent in claims, outline, report and memo; no majority vote |
| Summary compression | Source claim applies only to one population, period and observational study | Preserve those conditions in summary/headings; no “proves”, all-populations or causal strengthening |
| Named construct | Draft invokes a plausible-sounding named law absent from evidence | Find provenance, label an author-proposed frame or remove the false authority; citation liveness cannot certify the law |
| Partial access | Full text is blocked; snippets omit methods and limitations | Try permitted alternatives, disclose access limits and leave dependent findings conditional; no full-read claim or bypass |
| Evidence insufficient | Relevant permitted channels provide no usable evidence | Explain attempts and consequential unknowns; complete an honest insufficient finding without fabricated source rows |
| Updating conflicting values | A prior report and new source disagree but use different periods or denominators | Check comparability before declaring conflict; preserve dated versions and update only affected conclusions |
| No files / no delegation | User explicitly requests chat-only; subagents unavailable or unauthorized | Deliver substantive supported research inline, no package writes or delegated calls; explain actual verification limits |
| Experiment branch | “检验这个 Skill 是否比 baseline 更可靠。” | Controlled-research protocol with frozen acceptance, fair comparison, held-out tests and honest resource accounting, not a literature-only report |
| Requested export | User asks for a PDF as well as editable research | Produce and inspect it using available tools or report the actual blocker; Markdown alone is not completion |
| Honest verification | Source claim is unsupported but all files exist and URLs return 200 | Semantic review rejects or qualifies it; structural success is not described as factual proof |

Evidence to retain for a real evaluation: original question, allowed scope/tools, source versions, artifacts, observable failures, actual checks, changes required before acceptance and unfinished scope. Independent grading means a genuinely separate check with disclosed limits, not an invented reviewer persona.
