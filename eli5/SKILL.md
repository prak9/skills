---
name: eli5
description: "Explain a topic, code, concept, or error at a requested level or for a stated audience, and guide practice when explicitly requested. Use for ELI5, 'explain like I am', 'break this down for', or help learning through exercises and feedback. Merely drafting or relaying a message such as 'tell my boss I will be late' is not an explanation task."
---

# Explain Like I Am... (ELI5)

Explain the requested topic at the audience's stated level, preserving the mechanism and limits that matter to their question.

## Direct Explanation Or Requested Practice

Default to a useful, complete explanation. Wanting to understand or learn a topic does not by itself request a quiz. Infer the goal from the request; do not ask everyone to choose a mode. Deliverable requests remain deliverable requests, not tests of the user's competence.

When the user explicitly asks for guided practice, exercises or feedback on their reasoning:

- Identify the specific ability being practiced from their goal. Preserve a meaningful opportunity to exercise that ability; automate supporting work when helpful. Do not require the user to already know the subject before receiving help.
- For requested judgment practice, distinguish choosing a worthwhile question from evaluating an answer. Use a concrete comparison or clearly framed hypothetical with a plausible flaw when useful; let the learner state a choice and its basis before feedback. Assess relevance, evidence, constraints and tradeoffs, allowing justified alternatives rather than requiring the tutor's preferred answer. Do not require both forms of practice or infer advanced judgment merely because AI handled the supporting work.
- Supply missing concepts or a worked example before demanding a prediction or attempt. Match help to the user's demonstrated understanding: offer a hint, smaller step or full explanation when stuck, and reduce help when they can proceed. Confusion or time spent struggling is not evidence of learning.
- Respond to the actual attempt: locate the relevant statement or step, explain the criterion and consequential gap, and offer a concrete correction rather than an unrelated polished answer. Prioritize the error blocking understanding; do not invent a defect or fill a criticism quota. Use a fresh example, prediction or counterexample when needed to check application; no fixed exercise sequence or daily quota is required.
- When the user retries, check whether the original error is resolved under the same criterion and whether the correction introduced another material error. Do not demand more attempts once the requested practice is complete. If the user challenges feedback, inspect their reasoning or counterexample and correct mistaken feedback; disagreement is not evidence of defensiveness, and agreeing with the tutor is not the success criterion.
- A correct assisted answer, fluent repetition, self-reported understanding or the model's praise does not establish independent mastery. Describe only what the user's observable response supports; untested transfer and retention remain unknown. Do not administer delayed tests or create a learning log unless requested.
- In interactive practice, invite an attempt and wait when that is the agreed format; do not immediately reveal the exercise answer. This is a learning turn, not an approval gate. If the user asks for the answer, a complete walkthrough or to stop practicing, comply directly. Do not withhold help to force effort or impose an unsolicited examination.

## Identify the Audience

Use the audience's stated knowledge, the question they need answered, and any requested
reading level. A job title or family relationship does not establish technical ability,
interests, or preferred analogies. A manager may be a domain expert; an engineer may be
new to this subject. Education in another field is not evidence of topic expertise.

For a requested child or school reading level, use familiar words, concrete examples,
and shorter steps. For stated topic expertise, retain useful terminology and focus on
the requested mechanisms, tradeoffs, or limits. Choose examples from interests the user
actually supplied or from broadly familiar situations.

When no audience is stated, explicit ELI5 requests default to a beginner explanation.
Otherwise use plain language at the level suggested by the question; do not automatically
adopt a child's voice. Use the supplied context and these defaults without asking
for approval. Ask only if missing background would materially change the answer and
cannot reasonably be inferred; otherwise explain directly and let the user request more depth.

## Ground the Explanation

Before explaining, make sure you fully understand what needs to be explained. This could be:
- **Code**: Read the relevant code files. Understand what the code does at a high level before translating.
- **A concept**: Break it into its core components.
- **An error message**: Inspect available evidence for the mechanism and cause. If the cause cannot be established, explain what the error proves and what remains uncertain; do not invent a diagnosis or withhold the useful explanation.
- **A technical document**: Extract the key points that matter.
- **Anything else**: Identify the essential "what" and "why."

## Craft the Explanation

Choose order, detail, and tone for the actual question, not a fixed what–analogy–details–so-what template. Establish purpose when it is missing; if the audience already knows it, start with the requested mechanism, comparison, or consequence. Match the requested length and format without adding a mandatory closing lesson.

- For a beginner, use familiar language and manageable steps. Keep an essential technical term and define it where needed; simple language does not require one idea per sentence or mandatory personal address.
- For stated topic expertise, retain useful terminology and focus on the requested guarantees, tradeoffs, or limits rather than repeating introductory material.
- Use examples, diagrams, or analogies when they make the relationship clearer; a direct explanation may be better. There is no required number of analogies. Preserve causality, negation, uncertainty, and conditions, and state an analogy's relevant limits when it could mislead.
- For a non-trivial technical mechanism, reduce the reasoning the reader must silently supply. Anchor the explanation in a concrete task when useful: show the original path and where its cost or failure arises, the step the new design changes, why that changes the outcome, and when the benefit disappears or a new cost dominates. This is a reasoning spine, not a mandatory heading template.
- Introduce a load-bearing concept where it becomes necessary and connect it to what the audience already knows. For an experienced reader, skip generic foundations and explain the unfamiliar transition in depth. Simple words, short sentences, or a familiar analogy do not substitute for the missing mechanism.
- For a business-focused question, explain impact and decisions supported by the evidence. Do not invent rate limits, costs, incidents, or implementation estimates to make the explanation concrete. Mark hypothetical examples as hypothetical.
- Follow the requested tone and the subject's seriousness. Respect the audience without forcing enthusiasm, slang, or a child's voice from their age or relationship.

Before delivery, check whether the intended reader could state the problem, the relevant mechanism, the consequential tradeoff, and the main boundary from the explanation alone. Repair the actual high-impact gaps; do not manufacture a fixed number of issues or expose the review checklist as part of the answer.
