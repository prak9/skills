# Research Modeling Development Packet

`research-modeling-cases.jsonl` freezes `research-modeling-v1`: visible development cases for hypothesis discrimination, forecast validity, simulation checks, research reuse and thesis resolution. These are not untouched holdouts. Keep the core and instruction-migration suites unchanged.

Baseline for this change: commit `104e62ea1dcbd8632a91aaed13dabf11ecd7da7a`. The working tree also contained unrelated system-skill and investment PDF changes; they are not part of this candidate. Baseline repository contracts: `python3 -m unittest discover -s tests -p 'test_skill_contracts.py'` — 28 passing tests. This is structural evidence, not a model baseline run.

Freeze prompts and criteria before candidate instruction edits. A forward executor receives the prompt, selected skill and necessary evidence, not expected behavior or criteria. For an actual comparison, use isolated contexts with the same model, reasoning, tools and permissions; preserve instruction revisions, raw outputs, actual actions, reference reads, questions, operations, tokens and latency when available. Unknown measurements remain unknown.

Grade every criterion, including correct refusal of unsupported claims and clean negatives that should not trigger extra work. Expected phrases alone are insufficient. Hypothetical inputs do not require browsing or external actions; fail unauthorized writes, trading, training or deployment. Compare reference/operation cost on the same case rather than introducing arbitrary universal quotas.

The existing `evaluate_behavior_cases.py` does not load this packet. Do not report an automated behavior pass from JSON parsing, document checks or manually constructed expected responses. Without independent forward runs and grading, behavioral and cost effects remain **unrun**. This packet does not add an approval gate or require model evaluation for unrelated tasks.

Acceptance for the instruction edit: references and routes resolve, existing contracts pass, the case file parses with unique IDs and actionable criteria, and scoped review checks every case against the proposed rules. Accepting the documentation is not proof of improved model performance. Add independently reserved cases before claiming generalization beyond this development packet.

## Candidate Verification

- `python3 -m unittest discover -s tests`: 42 tests passed after the instruction edits. The baseline's 28 tests used the narrower `test_skill_contracts.py` selection; these counts are not a measured improvement.
- All 16 development cases parse, have unique IDs, reference existing skills and contain three grading criteria each. The 18 local Markdown links in the changed files resolve.
- Scoped `git diff --check` passed. Nine changed runtime documents resolve to the same files through both local Codex and Claude skill-directory symlinks, with matching content hashes. This verifies local deployment, not reload of an already active conversation.
- Model forward runs, behavioral grading and cost comparisons remain **unrun**.
