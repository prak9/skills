# TASK-001: CSV 导出

- Status: `进行中`
- Plan mode: `Linear`
- Program: ../program.md
- Plan node: NODE-001
- Context refs: CTX-001 / REF-001
- Preference refs: PREF-001
- Owner: AI
- Created: 2026-07-11
- Updated: 2026-07-11

## Task 1: CSV 导出

**Description:** 在查询出口接入 exporter 模块，支持 demo query --csv out.csv，输出符合 RFC 4180。

**Acceptance criteria:**

- [ ] --csv 参数生成文件，内容与查询结果一致
- [ ] 含逗号、引号、换行的字段转义正确

**Verification:**

- [ ] Tests pass: pytest tests/test_export.py
- [ ] Build succeeds: 不适用（纯 Python，无构建步骤）
- [ ] Manual check: 导出一次真实查询并用报表流程打开

**Dependencies:** None

**Context/Refs:** CTX-001 / REF-001

**Preference refs:** PREF-001

**Locked constraints:** 不新增第三方依赖

**Negotiable space:** 输出列顺序、exporter 内部结构

**Files likely touched:**

- src/exporter.py
- tests/test_export.py

**Estimated scope:** `Small`

## Atomic Implementation Plan

| Node | Status | Depends on | Action | Likely touched | Verification | Evidence | If verification fails |
|---|---|---|---|---|---|---|---|
| N-001 | `完成` | None | 写 exporter 模块与转义用例 | src/exporter.py | pytest tests/test_export.py | RUN-001 | 修转义逻辑后重跑 |
| N-002 | `待开始` | N-001 | CLI 加 --csv 参数 | src/cli.py | pytest tests/test_cli.py | 待运行 | 回退参数解析 |

## Verification Matrix

| Check | Covers | Method/command | Pass condition | Status | Evidence |
|---|---|---|---|---|---|
| V-001 | N-001 | pytest tests/test_export.py | 全部通过含转义用例 | `完成` | RUN-001 |
| V-002 | N-002 | pytest tests/test_cli.py | 全部通过 | `待验证` | 待运行 |

## Checkpoint

| Checkpoint | Covers | Requirements | Human review |
|---|---|---|---|
| CP-001 | N-001 N-002 | pytest 全绿 + 人工查看导出文件 | Yes |

## Current Loop Attempt

不适用（Linear）。

## Latest Execution Snapshot

| Field | Value |
|---|---|
| Snapshot ID | E-001 |
| Time | 2026-07-11 |
| Node | N-001 |
| Type | test |
| Latest action | exporter 模块与转义用例完成并通过 |
| Latest result | passed |
| Evidence | RUN-001 |
| Memory refs | RUN-001 / F-001 |
| Next | N-002 CLI 参数 |

## Escalation

Show a checkpoint before continuing when:

- 验证失败或需要改验收标准

Stop and ask first when:

- 需要新增第三方依赖（触碰 PREF-001）

## Risks and Rollback

| Risk | Impact | Prevention/detection | Rollback or containment |
|---|---|---|---|
| 转义错误破坏下游报表 | Medium | 转义用例 + 人工验收 | 回退 exporter 提交 |

## Standing Checklist

### Per Task

- [ ] Acceptance criteria are met and tied to evidence: 待 N-002 完成后确认。
- [x] Runtime behavior was verified, not only compiled or typechecked: RUN-001 覆盖 exporter 转义行为。
- [x] New behavior is covered by tests that fail without the change and pass with it: RUN-001。
- [ ] Existing tests still pass; no regression signal is ignored: 待 N-002 后跑全量 pytest。
- [x] Relevant edge cases and error paths are handled or recorded as known risk: 逗号、引号、换行已覆盖。
- [x] Changes are scoped to this task; no unrelated refactors are included。
- [x] No duplicated business logic, dead code, debug output, or commented-out blocks were left behind。
- [ ] Linting and formatting pass: 待 N-002 后执行。

### Per Feature / Risky Change

- [x] Integration points are accounted for: 仅 CLI 参数和 exporter，无迁移、config 或 feature flag。
- [ ] Public interfaces, APIs, user-facing behavior, and durable architecture decisions are documented when changed: 待 CLI 帮助文本确认。
- [x] Security implications are reviewed for untrusted input, auth, and data handling: 本地文件写出仅使用用户显式路径，无 auth/data access 变化。
- [x] Observability is in place for new critical paths: N/A: CLI 本地导出无长期服务路径。
- [x] Rollback or containment path is defined for risky changes: 回退 exporter/CLI 提交。
- [ ] Human review is complete before merge, deploy, or acceptance when required: CP-001 需要人审。

## Pre-completion Red Team

Answer all four questions before moving this package to `待验收` or `完成`.

| # | Question | Answer |
|---|---|---|
| RT-1 | If the deliverable were actually broken, would the evidence above still pass? | 待任务收尾时作答 |
| RT-2 | What was NOT verified? | 待任务收尾时作答 |
| RT-3 | Does the result solve the original problem in ../program.md#1-问题定义? | 待任务收尾时作答 |
| RT-4 | Single most likely post-delivery failure path? | 待任务收尾时作答 |

## Completion Writeback

When this task package is done, update ../program.md node status and evidence, and write to ../memory.md:

- Memory writeback: RUN-001 / F-001 已写入；完成时补 CHG 与 H 条目并跑提炼
- Final result: 待完成
- Completed: 待完成
