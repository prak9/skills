# Experiment Reporting — Visible Development Cases

These are unrun behavioral fixtures, not claims of model evaluation. Give an executor the request, applicable instructions and supplied inputs; capture outputs/artifacts and grade against the criteria. Use authorized local temporary output locations, never production data or external writes.

| Input / task | Observable acceptance criteria |
|---|---|
| Summarize an experiment: baseline success 40/100, candidate 44/100 on the same fixed set. Only counts exist. | Reports +4 percentage points and +10% relative; retains counts as the available supporting table, states item-level evidence is missing, invents no rows or paired uncertainty. |
| Baseline net PnL -10, candidate +5; another baseline is 0. Compare. | Reports +15 absolute for the first pair; no misleading negative or infinite percentage improvement. Zero baseline relative change is N/A. |
| Baseline IDs a,b,c; candidate IDs a,b,d. Rows include outcomes, one excluded case and a failed third arm. Deliver a paired comparison. | Exposes unmatched IDs and exclusions, uses explicit paired scope, retains failed-arm status; does not silently compare different populations as paired. Supporting tables reproduce the displayed metrics. |
| Two groups: baseline 9/10 and 10/100; candidate 8/10 and 12/100. Give total and group results. | Totals 19/110 vs 20/110; no unweighted mean of group rates presented as overall success. Group deterioration is visible; no unsupported causal attribution. |
| Report a completed local experiment with provided resolved configs, task outcomes and run logs; candidate changes one parameter. | Preserves full configs, shows the change and fixed baseline, supplies keyed bottom tables/dictionary and reproducible summary, links raw evidence. Any charts use the same data. Does not invent additional experiments or mandatory approval. |
| Explain what an existing result field means; no experiment comparison requested. | Answers narrowly; no demand for baseline, full configs, bottom-table bundle or mandatory charts. |
