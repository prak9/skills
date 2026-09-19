# Perspective Research Development Cases

`perspective-research-cases.jsonl` contains six visible development cases, frozen before the instruction edits. These are not independent holdouts. Baseline: `c806f8ec54b31a552d3420add7ccaf816734e5dc`; the 28 repository contract tests pass. Unrelated dirty files are outside the candidate.

For forward evaluation, give the executor only the prompt, selected skill and supplied evidence; exclude grading criteria. All cases are self-contained and authorize no network, account access or external mutation. The negative arithmetic case deliberately supplies a skill that should decline its heavier workflow.

Compare baseline and candidate in isolated contexts with the same model, tools and budget. Preserve actual outputs, reference reads, questions, operations and elapsed time; unavailable metrics remain unknown. Grade the stated criteria against behavior, including fabricated consensus, fake conflicts, unsupported synthesis and unnecessary scope expansion. Existing-source summaries and ordinary calculations must remain lightweight.

Accept the instruction change only after local links/frontmatter, repository contracts and scoped rule review pass. Claim behavioral improvement only after forward runs and grading; added cost must have a corresponding evidence or error-reduction benefit. This file is an evaluation packet, not a new runtime checklist or approval gate.

Model forward runs and before/after cost measurements: **not run**. Parsing fixtures and passing structural tests do not establish behavioral improvement.

Local verification: all 47 tests in `python3 -m unittest discover -s tests` pass (the 28-test baseline used only `test_skill_contracts.py`, so counts are not an improvement metric). All four skill frontmatter validations pass; six case IDs are unique and 11 local links in the changed runtime documents resolve. Scoped review covers each case's evidence, scope and completion boundary. An unrelated system-skill whitespace warning from the full worktree check was left untouched; candidate whitespace is checked separately.
