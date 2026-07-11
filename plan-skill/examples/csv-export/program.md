# Program: demo-cli CSV 导出

- 总状态：`进行中`
- Profile：`Full`
- 计划模式：`Linear`
- Memory：memory.md
- 当前任务包：`tasks/TASK-001-add-export.md`
- 当前计划节点：`NODE-001`
- 最新证据入口：RUN-001
- 下一 Checkpoint：CP-001
- Owner / TL：x
- 最后更新：2026-07-11

## 1. 问题定义

### 背景
CLI 查询结果只能打印到终端，下游报表流程需要 CSV。

### 要解决的问题
无法把查询结果导出为文件。

### 为什么现在做
报表流程本月上线，依赖导出。

### 非目标
- 不做 Excel 导出

## 2. 上下文与 References

### 关键上下文
| ID | 类型 | 内容摘要 | 位置/Ref | 为什么重要 | 状态/新鲜度 |
|---|---|---|---|---|---|
| CTX-001 | code | 查询出口函数 | src/query.py | 导出逻辑挂在此处 | 当前 |

### 代码与运行入口
| ID | 入口 | 路径/命令 | 关联节点 | 备注 |
|---|---|---|---|---|
| REF-001 | 测试 | pytest tests/ | NODE-001 | 全量测试 |

### 外部资料与证据
| ID | 来源 | Ref | 用途 | 获取/核对日期 |
|---|---|---|---|---|
| REF-EXT-001 | RFC 4180 | https://www.rfc-editor.org/rfc/rfc4180 | CSV 转义规则 | 2026-07-11 |

### 人与决策上下文
| ID | 角色/人 | 负责内容 | 何时需要介入 | 联系或记录 |
|---|---|---|---|---|
| OWN-001 | x | 最终验收 | 验收标准变化时 | 本文件 |

## 3. Preferences & Tradeoffs

### Preferences
| ID | Preference | Type | Strength | Scope | Rationale |
|---|---|---|---|---|---|
| PREF-001 | 标准库优先，不新增依赖 | imperative | locked | strategic | 依赖是长期成本 |

### Tradeoffs
| Decision | Option A | Option B | Tradeoff | Choice | Negotiable? |
|---|---|---|---|---|---|
| CSV 实现 | csv 模块 | pandas | 依赖 vs 便利 | csv 模块 | no |

### Locked Constraints & Negotiable Space
| Area | Locked constraints | Negotiable space | Escalation rule |
|---|---|---|---|
| 依赖 | 不新增第三方依赖 | 输出列顺序 | 需要新依赖时先问 |

## 4. 目标与度量

### 目标
| ID | 目标 | 成功度量 | 基线 | 目标值 | 数据来源/观察方式 |
|---|---|---|---:|---:|---|
| G-001 | 支持 CSV 导出 | 导出命令可用且转义正确 | 0 | 1 | pytest |

### 验收标准
| ID | 验收标准 | 验证方法 | 通过条件 | 责任方 |
|---|---|---|---|---|
| A-001 | demo query --csv out.csv 生成合法 CSV | pytest tests/test_export.py | 全部通过 | x |

## 5. 约束

### 硬约束
| ID | 约束 | 适用范围 | 验证/监控方法 |
|---|---|---|---|
| C-001 | 兼容 Python 3.10+ | 全部代码 | CI |

### 风险边界与升级条件
| 情况 | 处理规则 |
|---|---|
| 可逆、局部变更 | AI 自主推进并记录证据 |

## 6. 总体策略

### 策略概述
在查询出口处接 CSV writer，纵向一刀切到 e2e 测试。

### 依赖与切片策略
查询出口 -> exporter 模块 -> CLI 参数 -> e2e 测试

- 切片方式：纵向切片

### 执行原则
- 每个任务包有独立验收证据

## 7. 决策记录
| ID | 状态 | 决策 | 原因/证据 | 影响范围 | 日期 |
|---|---|---|---|---|---|
| D-001 | 已批准 | 用标准库 csv 模块 | PREF-001 | NODE-001 | 2026-07-11 |

## 8. 探索与假设验证
| ID | 状态 | 假设/未知 | 验证方法 | 截止任务包 | 通过/失败后的动作 |
|---|---|---|---|---|---|
| H-001 | 支持 | 查询出口返回可迭代行 | 读 src/query.py 并在 REPL 验证 | TASK-001 | 已确认，直接实现 |

### 探索实现计划
无。假设已通过代码阅读关闭，证据见 memory.md F-001。

## 9. Implementation Plan

### Overview
一个任务包完成导出功能并验收。

### Architecture Decisions
- CSV 逻辑独立为 exporter 模块，便于单测

### Plan Dependency Graph
```text
NODE-001 CSV 导出（进行中）
```

### Node Status
| 节点 | 阶段 | 状态 | 规模 | 任务包 | 目标 | 依赖节点 | 验收/验证入口 | 证据 | 最后更新 |
|---|---|---|---|---|---|---|---|---|---|
| NODE-001 | Phase 1 | `进行中` | `Small` | `tasks/TASK-001-add-export.md` | CSV 导出可用 | 无 | A-001 | RUN-001 | 2026-07-11 |

### Loop Contract
不适用（Linear）。

### Loop State
不适用。

### Memory Sync
| 类型 | 状态 | 来源 | memory.md 位置 | 最后更新 |
|---|---|---|---|---|
| 重要发现 | 已写入 | TASK-001 | memory.md#重要发现 | 2026-07-11 |

### Task List

#### Phase 1
- [ ] NODE-001 / tasks/TASK-001-add-export.md：CSV 导出

### Checkpoints
| Checkpoint | 位置 | 验证要求 | 是否需要人审 |
|---|---|---|---|
| CP-001 | NODE-001 后 | pytest 全绿 + 人工查看输出文件 | 是 |

### Parallelization Opportunities
无。

### Risks and Mitigations
| Risk | Impact | Mitigation |
|---|---|---|
| 字段含逗号/换行时转义错误 | Medium | 用 csv 模块并加转义用例 |

### Open Questions
无。

## 10. 当前状态
- 当前阻塞：无
- 下一步：N-002 CLI 参数
- Memory 待写入：无

## 11. 更新协议
按 plan-skill 更新规则维护：任务包状态变化更新第 9 节；历史与发现写 memory.md。
