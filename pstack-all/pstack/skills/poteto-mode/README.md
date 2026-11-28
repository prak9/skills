# poteto-mode 使用手册（pstack v0.15.48）

> **if you want to go fast, go deep first.**
>
> `poteto-mode` 是 `pstack` 的统一入口路由技能：你只需说明**目标与可判定的验收标准**，主对话会自动匹配 22 个 Playbook 之一，按 24 条工程原则拆分任务、委派子代理，并沿真实运行路径验证交付。

---

## 1. 各客户端入口与本机配置

| 客户端 | 调用方式 | 首次配置 | 安装/规则位置 |
|---|---|---|---|
| **Antigravity** | `/poteto-mode <目标>` | `/setup-pstack` | 插件 `~/.gemini/config/plugins/pstack`<br>规则 `~/.gemini/config/rules/pstack-models.md`（`trigger: always_on`） |
| **Codex** | `$pstack:poteto-mode <目标>`（输入 `$poteto-mode` 补全） | `$pstack:setup-pstack` | 原生插件 `pstack@pstack-claude`（`~/.codex/plugins/cache/pstack-claude/pstack/`） |
| **Cursor** | `/poteto-mode <目标>`（可按 `Option+Enter` 设为 Custom Mode） | `/setup-pstack` | `~/.cursor/rules/pstack-models.mdc` |
| **Claude Code** | `/pstack:poteto-mode <目标>` | `/pstack:setup-pstack` | `~/.claude/rules/pstack-models.md` |

> **本机防重复扫描说明**：本仓库同时作为 `~/.codex/skills` 的来源。为避免 Codex 递归扫描 `pstack-all/` 下的三套 harness（162 个 `SKILL.md`），`~/.codex/skills` 采用与 `~/.gemini/config/skills/` 一致的**逐技能软链**，排除 `pstack-all/`；Codex 侧通过原生插件 `pstack@pstack-claude` 加载 `poteto-mode`。

---

## 2. 日常怎么用

### 2.1 写好一句话提示词

不需要写长篇规格书，也不用手动编排技能顺序。最多包含 5 个要素（每项一句话）：

1. **目标**：出了什么问题，或要实现什么。
2. **可判定对错的验收标准**：明确“完成”对应哪条可证伪检查（不要写“改好一点”）。
3. **想看到的证据**：真实命令输出、前后对比数据、真实 UI/CLI 行为或落库结果。
4. **已知线索**：报错日志、复现步骤、失败任务 ID、相关链接。
5. **硬约束**：例如 `repro first`、`don't change any code yet`、`zero behavior change`。

示例：

```text
/poteto-mode 导出 CSV 在昨天发布后少了最后一行，失败任务 ID 4812。先复现再修复。完成标准是 60k 行测试集完整导出，给出修复前后的行数对比。
```

**避坑**：
- 不要在提示词里手动罗列技能流水线（如“先 `/architect` 再 `/arena` 再 `/interrogate`”），Playbook 会自动按顺序编排。
- 初次排查 bug 时，先不要急着塞入自己的原因猜测，避免把排查方向锁死；复杂/嘈杂需求可先让代理复述问题：`/poteto-mode 先用你自己的话复述核心问题，先不要改代码`。

### 2.2 常用短句与切换任务

- **继续推进**：`continue` / `do it` / `keep going until done`
- **切换新任务**（长对话中必须声明，否则会沿用上一个 Playbook）：
  ```text
  /poteto-mode new task. 查清为什么退出登录后缓存条目还在。先不要改代码。
  ```
- **离席挂机**：
  ```text
  /poteto-mode 我先离开，持续推进直到迁移检查显示旧调用方为 0，并记录每步决策日志。
  ```
  大跨度或无人值守任务会自动路由到 `figure-it-out` 与 `show-me-your-work`。

---

## 3. 核心工作机制

### 3.1 执行闭环（Non-negotiables）
1. **先复述目标与最小改动**：首条回复先对齐目标与最小影响范围再动手。
2. **先定义数据结构**：写代码前先明确数据形态；跨边界设计走 `architect`，多路并行走 `swarm`，方案对决走 `arena`，有争议设计走 `interrogate`。
3. **实验优先于空问**：能通过跑实验或写原型解决的分叉，按 `playbooks/prototype.md` 直接验证。
4. **真实面验收**：编译通过或 Mock 绿灯不算完成，必须沿真实运行路径取证；报告中的每个数字遵循 `benchmark-checklist`。
5. **收尾清理**：文本与回复遵循 `unslop` / `technical-writing`，评审前跑 `no-comments`。

### 3.2 主从隔离与子代理
- **主对话**：负责理解目标、匹配 Playbook、把控检查点与最终验收，保护主线程上下文不被大文件输出撑爆。
- **子代理（`poteto-agent`）**：默认每次修复、重试或下一项任务都启动**全新子代理**（带上原始目标、最新约束和前序报告），仅在需要复用未提交改动或运行中进程时才复用旧子代理。
- **模型预算**：通过 `/setup-pstack` 写入规则文件，按角色（编码、评审面板、Worker 等）分配推理档位。

### 3.3 自治边界
- **直接推进**：可逆操作、只读调研、运行测试/评测等直接执行，不无谓打断人类。
- **必须暂停确认**：不可逆写操作（共享分支 force-push、生产发布、删数据、对外发消息）。

---

## 4. 22 个 Playbooks 速查

所有剧本位于 [playbooks/](./playbooks/)，由 `poteto-mode` 自动匹配：

| 分类 | Playbook | 文件 | 适用场景 |
|---|---|---|---|
| **调研与诊断** | Investigation | [investigation.md](./playbooks/investigation.md) | 只读排查、定位机制、不改代码 |
| | Runtime forensics | [runtime-forensics.md](./playbooks/runtime-forensics.md) | 运行时故障、进程/状态取证 |
| | Trace forensics | [trace-forensics.md](./playbooks/trace-forensics.md) | 链路/日志/Trace 深度归因 |
| **开发与重构** | Feature | [feature.md](./playbooks/feature.md) | 新功能设计与实现 |
| | Bug fix | [bug-fix.md](./playbooks/bug-fix.md) | 先复现、定位根因、修复并验证 |
| | Refactoring | [refactoring.md](./playbooks/refactoring.md) | 零行为变更的结构重构 |
| | Prototype | [prototype.md](./playbooks/prototype.md) | 用最小可运行原型验证方案分叉 |
| | Visual parity | [visual-parity.md](./playbooks/visual-parity.md) | UI 视觉对齐与像素/渲染核验 |
| **性能与评测** | Perf issue | [perf-issue.md](./playbooks/perf-issue.md) | 已量化的慢路径分析与优化 |
| | Hillclimb | [hillclimb.md](./playbooks/hillclimb.md) | 面向指标的迭代爬坡优化 |
| | Eval | [eval.md](./playbooks/eval.md) | 评测集构建与回归对照 |
| | Authoring a skill | [authoring-a-skill.md](./playbooks/authoring-a-skill.md) | 编写与迭代 Agent Skill |
| **PR 与交付** | Opening a PR | [opening-a-pr.md](./playbooks/opening-a-pr.md) | 从 worktree 整理提交并创建 PR |
| | Babysit | [babysit.md](./playbooks/babysit.md) | 跟进 PR/Stack 的 CI 与评审直至可合并 |
| | Shipping | [shipping.md](./playbooks/shipping.md) | 绿灯 Stack 的独立核验与合入 |
| | Autopilot-full | [autopilot-full.md](./playbooks/autopilot-full.md) | PR 队列端到端自动驾驶 |
| | Autopilot-stack | [autopilot-stack.md](./playbooks/autopilot-stack.md) | 多 PR 栈自动驾驶 |
| **长程与运维** | Multi-phase plan | [multi-phase-plan.md](./playbooks/multi-phase-plan.md) | 多阶段大工程拆分与推进 |
| | Autonomous run | [autonomous-run.md](./playbooks/autonomous-run.md) | 无人值守/过夜长程执行 |
| | Session pickup | [session-pickup.md](./playbooks/session-pickup.md) | 跨会话恢复上下文与未完成工作 |
| | Pause safely | [pause-safely.md](./playbooks/pause-safely.md) | 安全中断并留下可恢复现场 |
| | Worktree cleanup | [worktree-cleanup.md](./playbooks/worktree-cleanup.md) | 按合并与脏状态安全清理 git worktree |

> 若任务跨度过大或无直接匹配的 Playbook，会自动转入 `figure-it-out`。

---

## 5. 24 条工程原则（Principles）

- **Core（10 条）**：`Laziness Protocol`、`Foundational Thinking`、`Redesign from First Principles`、`Attack the Premise`、`Subtract Before You Add`、`Minimize Reader Load`、`Outcome-Oriented Execution`、`Experience First`、`Exhaust the Design Space`、`Build the Lever`
- **Architecture（6 条）**：`Model the Domain`、`Boundary Discipline`、`Type System Discipline`、`Make Operations Idempotent`、`Migrate Callers Then Delete Legacy APIs`、`Separate Before Serializing Shared State`
- **Verification（5 条）**：`Prove It Works`、`Fix Root Causes`、`Sequence Work into Verifiable Units`、`Test Behavior, Not Implementation`、`Explain the Number`
- **Delegation（2 条）**：`Guard the Context Window`、`Never Block on the Human`
- **Meta（1 条）**：`Encode Lessons in Structure`

---

## 6. 常用配套技能与参考资料

- **需求澄清**：`/sharpen`（把模糊提示词打磨得更深）、`/reframe`（用专业术语重构问题）、`/in-your-own-words`（仅复述理解）
- **纠偏与固化**：`/correct`（把反复出现的错误固化为类型/lint/测试守卫）、`/no-comments`（清理凑数注释与 workaround）
- **验证基础设施**：`/create-verification-skill`（真实验证技能）、`/create-formal-verification-skill`（形式化验证技能）
- **帮助与文档**：`/poteto-help`、完整技能定义 [SKILL.md](./SKILL.md)、官方指南 [docs/guide/02-poteto-mode.md](../../docs/guide/02-poteto-mode.md)
