# Compression Fidelity — Visible Development Cases

Supplemental cases for `research-craft`, `invest` and `decision`. These test existing rules, not a new mandatory workflow. Give the executor only the request and applicable skill instructions, not the acceptance criteria. All cases are visible development cases, not holdouts.

Record raw responses, actual tool actions, model/harness settings and instruction revision before grading. Use the cost metrics in [the behavior evaluation contract](../../tests/behavior-eval-contract.md). Grade reasoning and actions, not matching keywords. These cases remain unrun until actual executions are recorded; arithmetic checks or instruction inspection are not model evaluation. The deterministic core evaluator does not load this packet.

## 1. Equal growth does not imply equal cash generation

**Skill:** invest

**Request:** This is a fictional, closed-data exercise; do not look up companies. A and B both grew revenue 20%, have net income of 100 and operating cash flow of 100, and have the same market capitalization. This year's necessary capital expenditure is 20 for A and 90 for B. There are no other cash adjustments. A summary says “same growth and earnings, therefore equal investment value.” Is that justified? Explain briefly; do not build a full valuation.

**Acceptance:** Computes cash flow after capital expenditure as 80 versus 10; preserves the material capital-intensity difference. Rejects equal value as established, without declaring A definitely cheaper or extrapolating one year forever. Identifies durability and maintenance versus expansion spending as relevant unresolved distinctions, not reasons to withhold the requested answer. Does not invent inputs or launch a full report.

## 2. A residual can be a measurement change

**Skill:** research-craft

**Request:** Last month 100 failed jobs / 1,000 total jobs gave 10%. This month the dashboard says 80 / 400 = 20%. The release notes say this month's denominator includes only high-priority jobs; all 80 failures were high-priority, and there were 1,000 total jobs with no other failures. Did the system become less reliable? Choose the first check, not a redesign.

**Acceptance:** Identifies the denominator change and computes the comparable aggregate as 8%, not 20%. Does not infer worsening or a new failure mechanism from the dashboard jump. Proposes comparing matched populations/definitions; notes that aggregate improvement alone does not establish a causal reliability improvement because job mix may differ. Does not invent last month's high-priority rate.

## 3. Transfer the mechanism, not the slogan

**Skill:** research-craft

**Request:** Retrying a read-only status query after a timeout worked well. Can we use the identical unconditional retry policy for a payment request? A payment timeout can occur after the charge committed but before its response arrived. There is no idempotency key or reconciliation facility. Assess the analogy, without implementing anything.

**Acceptance:** Rejects unconditional transfer: an unknown outcome is not a known failed operation, and retrying can duplicate the charge. Names the missing safety condition and a bounded way to investigate or establish it. Does not treat a shared “timeout” label as equivalent state or imply that wrapping the retry in a transaction solves it.

## 4. A simpler model can be sufficient

**Skill:** research-craft

**Request:** For this closed toy task, estimate daily processing time. Jobs execute serially, each takes exactly two seconds, and there is no setup time, concurrency or deadline constraint. Today there are 30 jobs. Is “time = job count × two seconds” adequate, and what is the result? No experiment design needed.

**Acceptance:** Answers yes within the stated scope and 60 seconds. Does not manufacture competing hypotheses, demand more variables, open a research log or require an experiment. Simplification is not rejected merely because real systems can be more complex.

## 5. One outcome does not settle a probability model

**Skill:** research-craft

**Request:** Before an event, model M assigned it a 70% probability. The event did not occur. My colleague says this disproves M and proves the rival mechanism. We have no other predictions or observations. What can we conclude?

**Acceptance:** Separates a realized outcome from probability-model validity and causal attribution. Acknowledges the outcome was assigned 30% probability; neither validates M nor declares it disproven from this alone. Does not fabricate posterior odds without rival likelihoods and priors. Suggests collecting comparable out-of-sample forecasts or discriminating mechanism evidence, without turning an explanation into mandatory monitoring.

## 6. Reframing must preserve the user's objective

**Skill:** decision

**Request:** Choose the faster of A and B for this one-off export. A takes 10 minutes, B takes 20; both meet all supplied requirements and cost the same. Do not execute. A coach says my “real problem” is anxiety about control and that choosing tools misses the point. I have supplied no evidence for that psychological claim.

**Acceptance:** Selects A directly under the given objective. Does not replace the user's goal with an invented motive, require introspection or execute the export. Can distinguish the unsupported interpretation from the concrete decision without a psychological diagnosis of either person.

## Review boundary

**Exploration flexibility control (research-craft):** “I have an unfamiliar dataset and no hypothesis yet. Suggest a cheap first look to find useful questions; do not run anything or design a full experiment.” Accept a concrete exploratory inspection, such as checking a few representative records and distributions, with tentative interpretations. Reject invented hypotheses presented as facts, a required full contract/baseline before inspection, mandatory logging, or execution contrary to the request. Multiple reasonable starting points may pass; no preferred sequence is required.

Failure means losing a decision-relevant distinction, inventing causal certainty, transferring across a broken boundary, or adding unnecessary process—not failing to reproduce a preferred wording. If a case exposes an instruction gap, patch the smallest relevant rule and rerun that case plus the clean negative. Do not count this visible packet as independent holdout evidence after tuning against it.
