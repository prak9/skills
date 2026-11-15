CLAUDE.md: Field Notes on Getting a Language Model to Write Code You Will Not Rewrite
A Short List of Rules, Earned by Watching the Same Mistakes Twice

Abstract. This file exists because language models make predictable mistakes when they write code. Not random mistakes, just the same ones, over and over, often enough that it was worth writing them down. What follows is not a set of suggestions but a set of rules. The throughline is the same in every section: the model is fast at generating plausible code and slow to notice that plausible is not the same as correct, so the discipline has to come from the process around it.

Index Terms. LLM-assisted programming, code review, software craftsmanship, minimal diffs, debugging, dependency hygiene.

I. READ BEFORE YOU WRITE
The biggest source of bad model-written code is writing before reading the codebase. Read the files you are about to touch; read, not skim. Copy the patterns that already exist, and check the imports to see what the project actually depends on, so you do not reach for axios where everything is fetch. Resolve searchable gaps from the code and tests before asking; do not invent a pattern that contradicts the project.

II. THINK BEFORE YOU CODE
Figure out what you are doing before you type. State material assumptions ("add authentication" is five different things, so name the one you picked) and name the tradeoffs. Point out a simpler approach when it meets the goal. Resolve ordinary gaps with reasonable assumptions; ask only when an unresolved ambiguity materially changes the result, scope, or real risk. Do not silently choose between consequential interpretations or add approval steps for hypothetical risks.

III. SIMPLICITY
Write the minimum code that solves the problem in front of you now, not the minimum that could solve every future version of it. Resist premature abstraction, skip error handling for errors that cannot occur, and hardcode values until there is a real reason to configure them. The test: if the only reason something is abstracted is "in case we need to," you have over-built it.

Do not add unrequested features, flexibility, or configuration. Keep simple single-use logic inline; extract a helper only for reuse, a genuinely complex boundary, or a real concept whose name improves understanding. Keep the main path readable rather than minimizing line count or scattering simple expressions across helpers. Comments explain non-obvious constraints and reasons, not obvious code.

Match defensive handling to actual boundaries, contracts, and known failure modes. Validate untrusted inputs at the owning boundary and pass validated values inward; do not repeatedly revalidate established internal contracts. Do not mask programming errors with broad catches, default values, or silent fallbacks. Fix the cause or expose the failure clearly; necessary recovery must have a concrete scenario and test evidence.

IV. SURGICAL CHANGES
Your diff should be as small as the task allows. Do not touch what you were not asked to touch, match the existing style, and do not reformat; a formatter pass buries the three lines that matter inside three hundred that do not. The test is whether you can justify every changed line by the task. If a line is there because "while I was in there," revert it.

Remove imports, variables, and functions made unused by your own changes. Mention unrelated pre-existing dead code rather than deleting it. For generated artifacts, change the source definition and regenerate through the project's existing command instead of hand-patching derived files; check affected callers when contracts change.

V. VERIFICATION
The gap between code that works and code you think works is testing. When fixing a bug, write the failing test first, watch it fail, then fix it; that is the only proof you fixed the cause and not the symptom. Test behavior that can actually break, not that a constructor sets a field. If something is hard to test, that is information about the design, not permission to skip it.

Do not add redundant unit tests: inspect existing coverage first and extend or parameterize it rather than adding renamed copies with equivalent inputs and assertions. New tests must protect a distinct failure mode, meaningful boundary, or independent regression risk, not merely raise test counts or coverage numbers. Different test layers may legitimately exercise the same code to verify different contracts or integration risks.

Test the real implementation; do not duplicate its algorithm as the test oracle. Derive expected results independently from a contract, calculation, or trusted fixture. Mock only where isolating external dependencies, cost, or nondeterminism is necessary, never the core behavior being verified. Prefer local substitutes to global state changes and restore any necessary changes.

Use the project's established verification commands. Confirm preserved behavior before and after refactoring and cover valid inputs and relevant rejection paths for validation changes. Reuse evidence that already covers the unchanged final code, inputs, environment, and acceptance criteria; do not mechanically rerun checks after a status update or phase transition.

VI. GOAL-DRIVEN EXECUTION
Every task needs a success criterion before code is written. "Add validation" becomes "reject a missing or malformed email, return 400 with a clear message, and test both cases." For substantive multi-step work, state a brief plan with the check that demonstrates each major outcome; trivial reversible changes do not require a plan file or architecture review. Clear goals, boundaries, and acceptance evidence should support autonomous execution, not repeated requests for confirmation.

VII. DEBUGGING
When something breaks, investigate; do not guess. Read the whole error and the stack trace, reproduce the problem before you change anything, and change one thing at a time. Do not paper over an unexpected null with a null check; find out why it is null, or the bug just moves somewhere quieter.

VIII. DEPENDENCIES
Every dependency is permanent code you do not control. Before adding one, ask whether the project or the standard library can already do it with crypto.randomUUID() over a uuid package. When you do add one, say why, so the choice is visible rather than smuggled into the manifest.

IX. COMMUNICATION
Say what you did and why, not just a block of code. Flag concerns even when you did exactly what was asked, and be precise about uncertainty: "I am not sure this library supports streaming" tells the user what to verify; "I think this should work" does not.

X. COMMON FAILURE MODES
A few patterns recur often enough to name: the Kitchen Sink (restructuring half the codebase while you are at it), the Wrong Abstraction (copy-paste twice before you abstract), the Optimistic Path (the happy path handled and the 500 ignored), and the Runaway Refactor (a fix that cascades across files). Catch yourself in any of these and the right move is to stop, not to push through.
