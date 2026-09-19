# Guided Learning Development Cases

Baseline: `c9f17a9b72da7a684ab9be8fea3268665439535d`. The six cases in `guided-learning-cases.jsonl` were recorded before editing the runtime instructions. These are visible development cases, not held-out evidence. Existing learning-transfer cases concern research model updates and remain unchanged.

Give an executor the selected skill and case prompt without the expected behavior or criteria. All inputs are self-contained; no network, external writes, recruitment or persistent monitoring is authorized. Preserve actual replies, questions, actions and instruction versions. For comparison, use fresh contexts with the same model, tools and budget for baseline and candidate. The switch-to-direct-answer case must honor the latest request even when the prior activity was practice.

Grade behavior rather than phrases: direct answers must remain direct; explicit practice must allow a meaningful attempt with adequate help; feedback must address the actual error; learning claims must not borrow evidence from assisted output quality. Record interaction and read/operation costs; missing measures remain unknown. Do not turn these cases into runtime checklists.

Model behavior and learning outcomes are **not tested** by fixture parsing or repository tests. Forward runs, causal learning effects and before/after cost comparisons remain **not run**. Static review and structural checks only support acceptance of the instruction edit, not improved teaching effectiveness.
