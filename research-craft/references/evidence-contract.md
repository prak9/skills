# Evidence Package And Verification Contract

For every report, retain an auditable path from question to claim to source and from claim to final wording. Default lean reports keep supporting passages/locators, dissent, derivations and actual checks in an appendix or existing records. They do not need the native package, hash receipt or package checker. Brief/chat-only work preserves applicable checks inline.

Use the native format below when a full audit package is selected under [report design](research-reporting.md#inputs-and-delivery-weight). An existing project schema can substitute if it preserves these relationships and equivalent checks; do not maintain two hand-edited authorities. All evidence judgments below apply across modes; named files and receipt schemas apply only to the native audit package.

## Evidence Before Prose

Assess **relevance** (does this passage bear on this claim?) separately from **authority** (can this source establish this particular fact?). Preserve supports, contradicts and context distinctly. A source may document its own contract but not prove comparative effectiveness. A press article that repeats a filing is a pointer to the filing, not an independent measurement. Source counts, source-type diversity and discovery diversity diagnose coverage; none mechanically establishes truth.

Preserve actual source text or permitted excerpts with locators, clearly labeled paraphrases, access limits, producing origin and observation/publication dates. Material that was not retrieved cannot be quoted from memory. Authority unknown means limited support, not automatic rejection or permission to assert it confidently. A credible minority counterexample can defeat a broad claim even when many sources repeat it; retain dissent until a substantive resolution is documented.

Evidence statuses describe the claim: supported, conditional, contested, insufficient or contradicted. Confidence low/medium/high is a qualitative assessment with a reason, not a calibrated probability. An unsupported or contested substantive claim cannot be high-confidence fact. A single authoritative record can establish a narrow fact; a vendor benchmark alone cannot establish universal superiority. State these boundaries in the claim and in the memo.

## Native Package v1

```text
research/<topic>/
  research.json       # version, scope/date, genre, report path, original question coverage
  plan.md             # scope, dependencies, channels/opposition, completion and resource bounds
  state.md            # current Known / Gaps / Next; short working window, not a transcript
  sources.csv         # source index; metadata is authoritative here
  sources/s01.md      # excerpts/paraphrase, locators, provenance and access limitations
  claims.csv          # scoped atomic assertions and opposing evidence
  evidence.csv        # claim/source/passage relationships, including dissent
  numbers.csv         # material reported numbers and reproducible calculations; header-only if none
  outline.csv         # section → claim IDs, including consequential unresolved findings
  review.md           # meaningful challenge findings, fixes and remaining limits
  memo.md             # concise reading entry, with scoped claims and direct links
  report.md           # or a dated genre-specific filename declared in research.json
  refresh.md          # what could change, sources/dates, dependencies; no scheduled monitoring
  .verify/review.json # semantic/access checks and exact input fingerprints
```

No empty ceremonial files: if nothing remains to refresh or challenge, explain that briefly. If an existing execution plan owns status, `plan.md` can link it and retain only research-specific scope. Source cards hold content, not duplicate mutable metadata. Optional `findings/` stores reusable atomic conclusions; additional exports or application records are conditional, not default completion gates.

`research.json`: `schema_version: 1`, `genre` (`qa|explainer|comparison|decision|landscape|validation|custom`), `as_of`, `report` (package-relative path), `questions` (nonempty array of `{id, question, status, claim_ids, reason}`). Question status is `answered`, `insufficient` or `open`; answered needs mapped claims, insufficient needs the attempted investigation and remaining consequence in reason, open prevents a complete-package pass. Do not change the original question list to make coverage green.

If an investigation yields no usable sources or passages, keep those CSV headers without invented rows. Record an insufficient claim, attempted channels, the unresolved question and its consequences in the report. An evidence-insufficient result can be complete; unsupported positive assertions cannot.

Use UTF-8 CSV with ordinary CSV quoting, one row per ID, and semicolon-separated ID lists. The checker requires these columns:

| File | Columns |
|---|---|
| sources.csv | `id,title,url,file,type,root,discovery_path,published_at,accessed_at,access,caveat` |
| claims.csv | `id,claim,status,confidence,rationale,limitations,evidence_ids,dissent_ids,excluded_reason` |
| evidence.csv | `id,claim_id,source_id,relation,kind,text,locator,authority,root` |
| numbers.csv | `id,claim_id,value,unit,kind,formula,inputs,source_ids,as_of,tolerance` |
| outline.csv | `section,claim_ids` |

- Source `url` may be an actual URL or identifiable local source; `file` is a nonempty package-relative source card. `access`: `full|partial|blocked|unknown`. Dates can be explicitly `unknown`; the limitation follows dependent claims. Caveats can be combined (`vendor;self-reported`); explain them in the card rather than inventing one exclusive category. Root identifies the producing observation; an evidence row can specify a narrower origin for mixed-source documents. `unknown` origins never count as independence.
- Evidence `relation`: `supports|contradicts|context`; `kind`: `quote|paraphrase`; `authority`: `qualified|limited|unknown`. Each row needs actual text and locator. Context is not supporting evidence. Claims reference evidence IDs; opposing rows must be retained in `dissent_ids` even after a documented resolution. Do not change the archival excerpt to make it entail the claim.
- Claims with unresolved opposing evidence use contested/conditional status and disclose the effect. To resolve a dispute, give the evidence-based reason in rationale/limitations and semantic review; deleting dissent or downgrading its source to evade a gate is invalid. Explicitly excluded findings remain traceable with their exclusion reason; required question answers cannot map only to excluded findings.
- Each material number belongs to a claim and sources. `kind`: `verbatim|derived`. Derived `inputs` is JSON, e.g. `{"a":{"value":100,"source_id":"s01","locator":"table A"},"b":{"value":125,"source_id":"s01","locator":"table B"}}`; `formula` uses names, constants, `+ - * / **` and parentheses, never executable code. Keep unit/period/population compatibility visible in the source and claim. `tolerance` is a declared nonnegative absolute rounding tolerance in the reported unit; it must not mask a wrong calculation. Verbatim values still need passage checks. Missing data is not zero. Shares require an explicit completeness/denominator check; do not sum unrelated percentages.
- Outline sections reference claims from the ledger. Every nonexcluded claim is mapped and linked in the report; each actual section has that heading. Use links such as `[C1](claims.csv)` for claim identity plus a direct source-card/primary-source citation beside the factual statement. Link numbers as `[N1](numbers.csv)` where used. A naked source list does not satisfy claim support. Simple typography may differ, but identifiers and paths must resolve.

## Separate The Checks

1. **Access/provenance:** source exists, relevant content was inspected, access mode and version are honest. URL liveness alone is not support; timeout is not fabrication. A legitimate saved snapshot can preserve evidence from a subsequently dead URL.
2. **Authority and support:** the qualified evidence supports each atomic assertion or the report labels an inference/conditional claim with its premises. Inspect methodology, selection, incentives and origin. Qualified does not mean infallible.
3. **Qualifier preservation:** compare the actual report AND memo against the ledger for subject, period, population, denominator, conditions, uncertainty and causal strength. Restore dropped qualifiers in the prose; do not weaken the ledger to excuse an overclaim.
4. **Construct provenance:** named laws/frameworks/taxonomies have a source or are explicitly labeled this report's proposed framing. Audit concepts that have no claim ID too; fabricated authority can evade ordinary citation checks.
5. **Numbers:** inspect the producer and data vintage, recompute derived values, reconcile units/denominators and complete share groups when claimed. Distinguish numerical consistency from measurement validity.
6. **Coverage and challenge:** original questions, decisive dissent and material limitations survive synthesis. The user can understand or apply the result within its stated conditions. Reviewer agreement is not a substitute for evidence.

For lean delivery, record the meaningful checks and remaining limits in the report; do not manufacture independent review. For a native audit package, write `.verify/review.json` only after performing the checks. It contains `reviewer`, `method` (including self-review/independent/tool and their limits), `input_hashes` (package-relative path → SHA-256), and `checks` (array of `{kind,target,status,reason}`). Required targets: `access` for every source ID; `authority`, `support`, `qualifiers` for every nonexcluded claim ID; `constructs`, `counterevidence`, `numbers` for target `report`. Status `pass|limited|fail`; limited needs a concrete reason carried into relevant claims and the report. Fail or missing checks block a clean handoff, not delivery of honestly labeled partial results. High confidence must not coexist with limited claim checks.

Fingerprint `research.json`, every CSV, every source card, plan/state/review/refresh, report and memo; compute with `sha256sum` or the project tool after writing/reviewing, then retain the receipt. Any change invalidates the affected receipt; do not merely update hashes without rechecking the changed content. One reviewer owns the receipt; concurrent workers own isolated evidence returns.

Run from the Skill's directory:

```bash
python3 scripts/validate_research.py /absolute/path/to/research/topic
```

Exit 0 means structural checks passed and required recorded checks are present/current, possibly with disclosed limits; 1 means violations, 2 unreadable/malformed inputs. The script is read-only, uses no network/model, does not manufacture verdicts, and cannot detect lying semantic judgments, unregistered prose claims/numbers or all misleading figures. Manually inspect those surfaces. Do not call it an independent fact checker or a semantic proof. The example in `evals/report-package/` is a synthetic contract fixture, not real research evidence.
