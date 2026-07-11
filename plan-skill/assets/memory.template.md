# Memory: <项目名称>

> Durable project memory. Store important findings, reusable knowledge, failed-attempt lessons, and historical execution summaries here.
> `program.md` remains the source of truth for the current plan and node status. Task packages remain the source of truth for detailed execution logs.

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

## 3. 历史执行记录总结

Summarize task-package and checkpoint history. Do not duplicate raw logs; link to them.

| ID | 时间 | 范围 | 结果 | 关键证据 | 经验/后续影响 |
|---|---|---|---|---|---|
| H-001 | `YYYY-MM-DD` | <TASK-NNN、NODE-NNN 或 Checkpoint> | `完成 / 阻塞 / 已取消 / 部分完成` | <证据位置> | <未来需要知道的总结> |

## 4. 失败与回炉记录

Preserve failures that reduce future search space.

| ID | 时间 | 失败/回炉内容 | 根因 | 已排除方案 | 后续规则 |
|---|---|---|---|---|---|
| R-001 | `YYYY-MM-DD` | <失败现象或回炉内容> | <已验证或待验证根因> | <不再重复的方案> | <未来执行规则> |

## 5. 开放知识缺口

Track unknowns that are not current blockers but matter later.

| ID | 状态 | 问题 | 为什么重要 | 验证方式 | 关联计划节点 |
|---|---|---|---|---|---|
| Q-001 | `待验证` | <未知问题> | <影响> | <验证方式> | `NODE-NNN / 无` |

## 6. 更新规则

- 重要发现必须有证据指针，不能只写印象。
- 历史执行总结写结论和影响，不复制完整执行日志。
- 失败记录要写明已排除方案，避免后续重复试错。
- 如果发现已过期，标记为 `已废弃`，不要静默删除。
- 每个完成、阻塞或取消的任务包，至少评估一次是否需要写入本文件；若不需要，在任务包完成回写中说明“不需要”。
