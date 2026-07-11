# Program: <项目名称>

> 总计划 Source of Truth：定义问题、目标、度量、验收标准、约束、总体策略、依赖与切片策略、决策、探索假设、执行计划和任务包状态。
> 任务执行细节写入 `tasks/TASK-*.md`；本文件维护总状态和每个任务包的状态。

- 总状态：`待开始 / 探索中 / 进行中 / 阻塞 / 待验收 / 完成 / 已取消`
- 当前任务包：`tasks/TASK-NNN-<slug>.md / 无`
- 当前计划节点：`NODE-NNN / 无`
- 下一计划节点：`NODE-NNN / 决策点 / 无`
- Owner / TL：`<姓名或角色>`
- 最后更新：`YYYY-MM-DD`

## 1. 问题定义

### 背景

<当前现状、触发原因、相关用户或系统。>

### 要解决的问题

<明确写出问题，而不是直接写解决方案。>

### 为什么现在做

<风险、机会、成本、依赖或时机。>

### 非目标

- <本轮明确不解决的事项>

## 2. 目标与度量

### 目标

| ID | 目标 | 成功度量 | 基线 | 目标值 | 数据来源/观察方式 |
|---|---|---|---:|---:|---|
| G-001 | <目标> | <指标> | <值> | <值> | <来源> |

### 验收标准

| ID | 验收标准 | 验证方法 | 通过条件 | 责任方 |
|---|---|---|---|---|
| A-001 | <端到端可观察结果> | <测试、演示、日志、人工验收等> | <明确条件> | <角色> |

## 3. 约束

### 硬约束

| ID | 约束 | 适用范围 | 验证/监控方法 |
|---|---|---|---|
| C-001 | <安全、数据、兼容性、延迟、合规等> | <范围> | <方法> |

### 风险边界与升级条件

| 情况 | 处理规则 |
|---|---|
| 可逆、局部、不会改变外部契约 | AI 可自主推进并记录证据 |
| 跨模块、关键假设未验证、引入长期承诺 | 到任务包 Checkpoint 展示 |
| 可能违反硬约束、造成不可逆损失、改变目标或验收标准 | 停止并先征询 |

## 4. 总体策略

### 策略概述

<用几句话说明总体解法、先后顺序和取舍。>

### 依赖与切片策略

```text
<基础依赖> -> <中间能力> -> <用户/系统可观察结果>
```

- 切片方式：`纵向切片 / 水平分层 / 混合`
- 选择原因：<为什么这样切>
- 高风险优先项：<最早验证的风险或假设>

### 执行原则

- <原则，例如先验证最高风险假设>
- <原则，例如每个任务包必须有独立验收证据>
- <原则，例如每 2-3 个任务包设置一个 Checkpoint>

## 5. 决策记录

只记录会影响后续任务包的决定；普通实现细节写入任务包。

| ID | 状态 | 决策 | 原因/证据 | 影响范围 | 日期 |
|---|---|---|---|---|---|
| D-001 | `提议 / 已批准 / 已替代 / 已废弃` | <决定> | <证据或取舍> | <影响> | `YYYY-MM-DD` |

## 6. 探索与假设验证

| ID | 状态 | 假设/未知 | 验证方法 | 截止任务包 | 通过/失败后的动作 |
|---|---|---|---|---|---|
| H-001 | `[待验证]` | <假设或未知> | <实验、代码阅读、原型、用户确认等> | `TASK-NNN` | <动作> |

## 7. Implementation Plan

每个计划节点必须拆为一个任务包。任务包内再拆为原子实现节点。本节维护计划依赖图、每个节点状态、阶段任务清单、Checkpoint、风险和开放问题。

### Overview

<一段话说明本轮要构建什么、为什么这样分阶段、最终如何验收。>

### Architecture Decisions

- <关键决策 1 和原因>
- <关键决策 2 和原因>

### Plan Dependency Graph

```text
NODE-001 Foundation (<status>) 
  -> NODE-002 Core slice (<status>)
      -> NODE-003 Polish / hardening (<status>)
```

### Node Status

| 节点 | 阶段 | 状态 | 规模 | 任务包 | 目标 | 依赖节点 | 验收/验证入口 | 证据 | 最后更新 |
|---|---|---|---|---|---|---|---|---|---|
| NODE-001 | Phase 1: Foundation | `待开始` | `Small / Medium` | `tasks/TASK-001-short-slug.md` | <可观察结果> | `无` | <A-NNN、V-NNN 或命令> | <证据位置> | `YYYY-MM-DD` |

### Task List

#### Phase 1: Foundation

- [ ] NODE-001 / `tasks/TASK-001-short-slug.md`：<基础能力或最高风险假设验证>
- [ ] NODE-002 / `tasks/TASK-002-short-slug.md`：<后续基础节点>

#### Checkpoint: Foundation

- [ ] Tests pass and build is clean.
- [ ] Foundation assumptions are validated or explicitly escalated.

#### Phase 2: Core Features

- [ ] NODE-003 / `tasks/TASK-003-short-slug.md`：<核心纵向切片>
- [ ] NODE-004 / `tasks/TASK-004-short-slug.md`：<核心纵向切片>

#### Checkpoint: Core Features

- [ ] End-to-end core flow works.
- [ ] Node status table and task-package evidence are current.

#### Phase 3: Polish

- [ ] NODE-005 / `tasks/TASK-005-short-slug.md`：<收尾、硬化或文档>

#### Checkpoint: Complete

- [ ] All acceptance criteria are met.
- [ ] All completed nodes have evidence.
- [ ] Ready for human review or release.

### Checkpoints

| Checkpoint | 位置 | 验证要求 | 是否需要人审 |
|---|---|---|---|
| CP-001 | <NODE-001 后或 NODE-001~003 后> | <测试、构建、端到端流或人工验收> | `是 / 否` |

### Parallelization Opportunities

| 工作 | 是否可并行 | 前置条件 | 协调方式 |
|---|---|---|---|
| <节点、任务包或测试/文档工作> | `是 / 否 / 待确认` | <共享契约或依赖> | <文件、接口、Owner 或 Checkpoint> |

### Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| <风险> | `High / Medium / Low` | <缓解策略> |

### Open Questions

- `[待决策]` <需要人输入的问题、可选方案和建议默认值>

## 8. 当前状态

- 当前阻塞：<无；或阻塞说明、Owner、解除条件>
- 当前风险：<无；或风险和控制方式>
- 下一步：<下一个计划节点、任务包或原子节点>
- 下一次需要人判断：<无；或决策点>

## 9. 更新协议

- 新增、阻塞、待验收、完成或取消计划节点/任务包时，必须更新第 7 节的 Plan Dependency Graph、Node Status 和 Task List。
- 目标、度量、验收标准、硬约束或总体策略变化时，必须新增或更新第 2-5 节。
- 假设验证完成时，必须更新第 6 节，并把影响反映到相关任务包。
- 任务包内部原子节点状态只写在对应 `tasks/TASK-*.md`；本文件只写计划节点/任务包级状态。
- 状态为 `完成` 必须有证据位置，不能只写“已实现”。
- 如果需要兼容 `tasks/plan.md` 或 `tasks/todo.md`，只能从本文件和任务包导出，不能作为权威来源。
