# Financial Evidence And Claim Audit

Use for filing extraction, material evidence disputes, citation repair, or the final claim check in Full research. This supplements the shared source rules; it is not another mandatory multi-agent workflow, evidence database or reason to defer feasible research.

## Locate Before Extracting

Resolve the issuer, original document, version and period before taking a number. Inspect the document inventory or table of contents, locate the relevant statement/section, then read the original passage, table headers and qualifying notes. Search snippets identify where to read; a truncated result does not establish what the rest of a table or Q&A says. Retrieve missing context when it can change the claim.

If an available tool exposes structured statements or XBRL, use them to locate standard financial rows efficiently, then check the material context: concept/row meaning, period start/end or instant, consolidated versus segment dimensions, currency, scale, sign and amendments. Machine extraction confidence is not source reliability. When extraction conflicts with the original, resolve against the original; a new number requires rechecking dependent calculations, not just changing the citation. Do not infer a fiscal quarter from a filing date, or a standalone quarter from a year-to-date column without an explicit same-basis subtraction.

Use only tools actually available. Document-local section/table refs belong to the issuer/document/version that produced them; obtain fresh refs when that identity changes. Do not guess or reuse another filing's ref. Keep an original public link or a permitted original-file locator alongside internal retrieval IDs so the delivered citation remains usable outside the tool session. A missing parser field, failed request or absent search hit is not zero or proof of nondisclosure. Change to an available original-document route rather than mechanically retrying or claiming nonexistent tool access.

## Preserve The Evidence-To-Calculation Chain

Reuse the memo's evidence records and [data contract](data-contract.md). Preserve the original value and label separately from normalized/derived values, with explicit conversion/subtraction formulas and cited inputs. Unit conversion is allowed when the basis is known; never guess it to complete a table.

Locators should match the evidence type, for example:

- **Narrative:** original filing/accession or report identity, date, Item/heading/page and the relevant qualification.
- **Statement/table:** original document plus statement/table, rows, column periods and units; inspect footnotes when material.
- **XBRL:** filing/accession, concept, period and dimensions; the API result alone may omit important narrative context.
- **Call/interview:** original recording or publisher transcript, date and available timecode/section; distinguish an analyst's question, management's answer and a prepared statement. A premise inside a question is not management guidance.

These are locator semantics, not required invented fields or a new JSON schema. Missing location details stay missing. Put original citations next to the claims, including summary/table claims; a full source inventory is supplementary.

## Check Support Before Repairing Prose

For each thesis-bearing claim or flagged material statement, compare its actual words and model use with the cited original—not only the existence of a URL. Check subject, amount, scope, time, certainty, attribution and causal strength. Two individually supported facts do not prove a stronger identity, allocation or causal link: “bought GPUs” plus “customer expanded” does not establish those GPUs' customer, use or contracted revenue. A valid derived ratio need not appear verbatim in the source if the cited numerator, denominator and formula support it.

Resolve the issue according to evidence, without a mandatory status table in the user report:

| Evidence state | Proportionate response |
|---|---|
| Supported as written or transparently derived | Preserve the useful claim and calculation; no rewrite to satisfy style preferences |
| Supported, but cited locator is wrong/coarse | Verify the precise original passage and fix/add its locator; preserve the claim if scope and meaning are unchanged |
| Cited source contradicts the claim | Correct the claim and affected model/summary; do not average incompatible facts or just add “possibly” |
| Source accessible but does not support the asserted fact/link | Complete the relevant feasible check; remove an unsupported factual premise and its model effect if still unsupported. A separate hypothesis may remain explicitly unproven, not a hidden base-case input |
| Source unavailable, truncated or ambiguous | State access/interpretation limits, pursue feasible alternatives, and bound the conclusion; neither mark the business claim false nor invent a verification pass |

For a suspected citation defect, first inspect the already cited original and its relevant context. If support lies elsewhere in the same filing, verify and cite that location. Support found in a different report is **new evidence**: verify issuer, date, period and scope before adding it; never silently pretend it was in the old source. Rechecking evidence may strengthen, narrow or reject a claim; an audit label or agreement between agents is not independent proof.

Fix the cause before the wording. A wrong anchor usually needs a citation patch; a false unit, unsupported customer assignment or misread forward statement needs factual/model correction. Do not preserve an invented order amount merely by prefixing it with “may.” Preserve legitimate conditional estimates with their assumptions and sensitivity; not every uncertain forecast is a fabricated fact. Leave unaffected analysis intact and recheck the changed passage and dependent calculations/conclusions. Do not force a rewrite, another reviewer or a full re-audit when existing evidence resolves the issue.

## Close The Research, Not Just The Formatting

Check the final thesis and executive summary against the supported model and original evidence. A narrower body must not leave a stronger headline, target or “market missed this” claim behind. Distinguish completed research, unresolved evidence and investment attractiveness: “worth further study” does not mean “mispriced,” while unresolved value does not erase the useful work completed. Name the decisive missing evidence and reopening condition without moving an accessible current check into an indefinite follow-up list.

Automated format/arithmetic checks can verify locators' shape and calculations, not that a source exists or entails the claim. Report what was actually read or tested. No audit process guarantees an error-free report or changes the authorization required for publishing, archiving or trading.

## Design Provenance And Adaptation

Adapted from the local `dayu-agent` checkout at commit `2115c86d5a9027bb51cbbc8a4d0175080732e4e6`: `dayu/config/prompts/base/tools.md`, `base/fact_rules.md`, `tasks/confirm_evidence_violations.md`, and the implemented `dayu/services/internal/write_pipeline/chapter_audit_coordinator.py` and `audit_evidence_rewriter.py`. Its `company_facets.py` and `tasks/infer_company_facets.md` also inform Mode A's business-model/constraint lens. Upstream: [Dayu](https://github.com/noho/dayu-agent). These are design sources, not issuer evidence or a runtime dependency.

Retain grounded retrieval, claim-level confirmation, source-aware repair and conditional research focus. Do not import the long fixed template, fixed search/tag quotas, mandatory write/audit/confirm/repair stages, rigid formatting, blanket ban on unit conversion, or the qualitative-screening template's ban on valuation. The available tools and the current user's investment request govern execution.
