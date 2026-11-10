# Three-capabilities adaptation — 2026-11-10

## Source coverage and scoped decision

Read all 18 images of [the supplied note](https://www.xiaohongshu.com/explore/6af30ff30000000025008985). They visibly show source pages 1/28 through 18/28, ending mid-discussion. Note-media acquisition is complete; the underlying 28-page source is not. Original pages 19–28 were not acquired or reconstructed. Historical anecdotes and the psychological theory attributed in the note were not independently verified or promoted into Skill facts.

The useful design distinction is between evaluating an existing answer, generating a materially different feasible approach, and applying an approach under real constraints. Existing investment, decision, research and planning rules already cover mechanisms, alternatives and verification; they were not expanded for this article.

## Minimal changes

- `socratic-tutor/SKILL.md`: one conditional exercise-selection bullet. Target the learning gap rather than force every lesson through three modes; distinguish renaming from a new mechanism and theoretical explanation from constrained application. Alternative representations must preserve the goal and relevant relationships/constraints.
- `read-xiaohongshu/SKILL.md` and its retrieval contract: make acquisition/source/requested-scope completeness distinct. Visible pagination can establish an excerpt; absence of pagination does not establish truncation. An acquired requested excerpt can finish without requiring its entire parent source. Parser fields and network/account boundaries are unchanged; no OCR-based automatic completeness detector was added.
- Two tutor cases appended to the existing [14-case development packet](../socratic-tutor/evals/behavior-cases.jsonl); the original 12 prompts and criteria remain unchanged. Added a two-case [source-scope development packet](../read-xiaohongshu/evals/content-scope-cases.jsonl). Frozen criteria were not shown to executors.

## Forward smoke check

Two fresh executors inherited the parent configuration without model/effort overrides. Each domain used one prompt-only batch; cases within a batch shared context. This is not five independent executions or a sealed holdout. Parent authored and semantically graded the cases; no independent blind grader or old-instruction arm was run. Exact backend identity, cost and token telemetry are unknown. Read/action reports below are executor self-reports, not independently captured tool traces.

| Case | Actual final-response evidence | Review |
|---|---|---|
| `tutor-distinct-solutions-not-renaming` | Recognized label/font changes as cosmetic under the unchanged process; did not certify mastery. Asked the learner to identify one process change while preserving no-extra-staff and mandatory-registration constraints, without supplying the solutions. | All 4 frozen criteria met. |
| `tutor-practical-skill-needs-practical-evidence` | Kept queue-analysis evidence separate from unassessed trial design. Asked for one paper trial with a concrete scenario, constraints, implementation and rollback; did not contact anyone or claim practical success. | All 4 criteria met. The integrated design task has several relevant aspects; it is one bounded artifact, not unrelated questions or a mandatory three-mode template. |
| Existing `tutor-direct-explanation-negative` | Directly explained Ridge feature scaling with a checked unit-change example; did not start a quiz, progress map or course. | Both existing criteria met. This is response-mode coverage with the Skill preloaded, not proof of automatic routing. |
| `xhs-note-complete-source-excerpt` | Stated all18 note images acquired/read but only original pages1–18/28 available; did not claim full source or invent the missing remainder. Offered bounded delivery. | All 3 criteria met. |
| `xhs-requested-range-is-complete` | Declared requested pages3–5 complete and deliverable, without demanding the rest of the10-page source. | All 3 criteria met. |

Tutoring executor read only its Skill and prompt file; source executor reported reading its Skill, retrieval contract and prompt file. Neither reported network/account access or writes. The source-scope tasks use supplied reading records: they test scope reasoning, not independent visual OCR. The parent performed the actual 18-image visual reading.

Inputs and frozen protocol remain locally at `/data/tmp/xiaohongshu-ryw2i19m/{tutor-inputs.json,scope-inputs.json,verification-protocol.md}`. Original final responses are the `three_capabilities_tutor_check` and `source_scope_check` task messages in this session; this temporary directory is not a published/versioned evidence store.

## Verification and limits

`python3 -m pytest -q read-xiaohongshu/tests/test_fetch_note.py tests/test_skill_contracts.py tests/test_skill_hygiene.py tests/test_skill_simplification.py`: **82 passed, 311 subtests passed** after instruction changes. Both `quick_validate.py` checks passed. The14 tutor and2 source cases parsed with unique IDs and populated criteria. Structural/fixture tests do not establish teaching ability.

These edits clarify conditional task coverage and an observed source-scope distinction; the smoke results are not measured improvement over old instructions, proof of creativity/learning effects, or validation of the article's general theory. Full multi-turn tutoring, human learning, delayed retention and unseen sources remain untested. No new dependency, global teaching gate, scoring system or additional approval workflow was added. No Git commit/push, deployment, trade or Notion write was performed.
