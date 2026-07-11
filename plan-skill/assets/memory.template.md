# Memory: <项目名称>

> Durable project memory. Store important findings, reusable knowledge, CHANGELOG entries, run-log summaries, failed-attempt lessons, and historical execution summaries here.
> `program.md` remains the source of truth for current plan and latest node status only. Task packages keep active execution state only.

- 最后更新：`YYYY-MM-DD`
- 对应 Program：`program.md`

## 1. 重要发现

Only keep findings that should affect future planning or implementation.

| ID | 状态 | 发现 | 影响 | 证据 | 来源 | 日期 |
|---|---|---|---|---|---|---|
| F-001 | `有效 / 已废弃 / 待验证` | <重要事实、系统行为、约束、隐藏依赖或失败原因> | <对后续计划/实现的影响> | <测试、日志、提交、报告或任务包记录> | <TASK-NNN / L-NNN / Checkpoint> | `YYYY-MM-DD` |

## 2. 知识库沉淀

Reusable knowledge that future agents should apply.

| ID | 类别 | 知识 | 适用场景 | 反例/边界 | 证据 |
|---|---|---|---|---|---|
| K-001 | `实现 / 测试 / 架构 / 产品 / 运维 / 数据 / 流程` | <可复用知识> | <何时使用> | <何时不适用> | <证据链接或任务包> |

## 3. 变更记录（Changelog）

Meaningful changes to plan, implementation, interfaces, dependencies, acceptance criteria, or decisions. Do not create a separate CHANGELOG file unless explicitly requested.

| ID | 时间 | 类型 | 范围 | 变更摘要 | 原因/触发 | 证据 | 影响 |
|---|---|---|---|---|---|---|---|
| CHG-001 | `YYYY-MM-DD` | `plan / code / test / docs / decision / dependency / release` | <NODE-NNN、TASK-NNN、模块或接口> | <发生了什么变化> | <为什么改> | <提交、任务包、测试、评审或记录> | <对后续计划/使用者的影响> |

## 4. 运行日志

Runtime logs are distilled records of execution, verification, rollout, rollback, manual acceptance, or Loop attempts. Link raw terminal output, CI logs, screenshots, or artifacts instead of pasting large logs.

| ID | 时间 | 范围 | 类型 | 动作 | 结果 | 证据 | 后续 | 提炼 |
|---|---|---|---|---|---|---|---|---|
| RUN-001 | `YYYY-MM-DD` | <TASK-NNN、NODE-NNN、L-NNN 或命令> | `implementation / test / build / verify / rollout / rollback / manual acceptance / loop` | <做了什么> | `passed / failed / partial / blocked` | <日志、命令输出、CI、截图、报告或任务包> | <下一步或无> | `待提炼 / 不需要 / 产出的 K-R-PL-F ID` |

## 5. 历史执行记录总结

Summarize task-package and checkpoint history. Do not duplicate raw logs; link to them.

| ID | 时间 | 范围 | 结果 | 关键证据 | 经验/后续影响 |
|---|---|---|---|---|---|
| H-001 | `YYYY-MM-DD` | <TASK-NNN、NODE-NNN 或 Checkpoint> | `完成 / 阻塞 / 已取消 / 部分完成` | <RUN-NNN、CHG-NNN、测试或提交> | <未来需要知道的总结> |

## 6. 失败与回炉记录

Preserve failures that reduce future search space.

| ID | 时间 | 失败/回炉内容 | 根因 | 已排除方案 | 后续规则 |
|---|---|---|---|---|---|
| R-001 | `YYYY-MM-DD` | <失败现象或回炉内容> | <已验证或待验证根因> | <不再重复的方案> | <未来执行规则> |

## 7. 开放知识缺口

Track unknowns that are not current blockers but matter later.

| ID | 状态 | 问题 | 为什么重要 | 验证方式 | 关联计划节点 |
|---|---|---|---|---|---|
| Q-001 | `待验证` | <未知问题> | <影响> | <验证方式> | `NODE-NNN / 无` |

## 8. Preference Learning

Capture what execution taught about preferences, tradeoffs, locked constraints, or negotiable space.

| ID | Learned preference | Previous assumption | Evidence | Scope | Promote to default? |
|---|---|---|---|---|---|
| PL-001 | <what we now know matters> | <old assumption or blank> | <RUN-NNN、CHG-NNN、TASK-NNN 或 review> | `strategic / tactical` | `yes / no / later` |

## 9. 提炼与整理（Reflection & Curation）

本文件是不断演化的操作手册（ACE 式），不是重写对象。执行写痕迹（RUN），反思提经验（K/R/PL/F），整理只做带 ID 的增量修订。

触发时机：任务包完成/阻塞/取消时，或 `待提炼` 的运行日志达到 5 条时。

程序：

1. Reflect：逐条审阅 `待提炼` 的 RUN/R 条目，从成功和失败中提取经验。
2. Curate：新增或修订带 ID 的 K/R/PL/F 条目；不重写本文件其他内容。
3. 回标来源：RUN 条目的 `提炼` 列填入产出条目的 ID，或 `不需要`。
4. Compact：已提炼的整段执行历史可压缩为一条 H-NNN 总结；被替代的条目标 `已废弃`，不删除。

反模式：

- 简短偏置（brevity bias）：把具体经验压成空泛原则。提炼产出的条目必须保留触发条件、适用场景、反例/边界和证据指针；写不出适用场景的经验不入库。
- 上下文坍缩（context collapse）：靠重写全文来"整理"。只允许按 ID 增改单条；合并重复条目时保留幸存 ID，被并入条目标 `已废弃` 并指向幸存条目。

## 10. 更新规则

- 重要发现必须有证据指针，不能只写印象。
- Preference Learning 只记录会改变未来计划或任务执行方式的偏好学习。
- CHANGELOG 只记录有后续影响的变更，不记录普通编辑流水账。
- 运行日志写摘要和证据指针，不复制完整终端输出或大段 CI 日志。
- 历史执行总结写结论和影响，不复制完整运行日志。
- 失败记录要写明已排除方案，避免后续重复试错。
- 如果发现已过期，标记为 `已废弃`，不要静默删除。
- 每个完成、阻塞或取消的任务包，至少评估一次是否需要写入本文件的 CHG/RUN/F/K/H/R/PL 区域；若不需要，在任务包完成回写中说明“不需要”。
