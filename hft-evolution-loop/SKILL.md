---
name: hft-evolution-loop
description: 在 py 高频期货项目中启动、恢复和推进基于 result.py 每日实盘/模拟底表的离线沙盒自进化优化循环（Evolution Tree）。用于刷新跨日底表与失效切片、在隔离 git worktree 中迭代非 sim/非因子可调面、执行传导早停与滑点费用压测，并维护进化树；不用于纯日报解读（用 hf-futures-analysis）、通用方法论设计（用 hft-rsi-research）或直接修改生产配置。
---

# HFT 离线沙盒自进化循环 (`hft-evolution-loop`)

驱动 `/home/x/py` 中“观测 `result.py` 失效 → 隔离沙盒提案与修改 → 四级漏斗验证 → 进化树沉淀”的闭环执行。

## 硬约束（不可逾越）

1. **锁死控制面**：严禁修改 `sim.py`、`live_fill_*.py`、`sim_fill_policy.py`、`feature.py`、`conf/features_v2.lst`、`conf/features.json`、`cpp/l2factor/`、`exp/evaluator.py`、`analyze/promotion_gate.py`、`conf/stock_prop.csv`、`conf/validation_truth_set.yaml` 及生产 `conf/wintest.conf`。任何越界改动由 `exp/sandbox_guard.py` 硬拦截为 `INVALID_SANDBOX`。
2. **单节点单一可调面**：每次只改 `label_horizon` / `sample_policy` / `preprocess` / `model_selector` / `trade_policy` / `research_recipe` 之一（`combine` 仅限两个已保留/晋级父节点）。
3. **可定制范围与预算**：每次启动或续跑均支持用户直接指定 `--max-nodes`（最大节点数）与 `--max-depth`（最大树深度），传参即实时写入/更新 `tree.json`；用户未指定时，新建默认 ROOT=`dce_t2`、品种池=`eb,eg,pp,l,y,pg`、`max_nodes=10`、`max_depth=3`，续跑沿用原树配置。
4. **永不覆盖与防过拟合**：失败节点绝不覆盖父节点或 Champion，自动记入 `negative_index.jsonl`；`SIM_REAL_RESIDUAL` 切片只做执行核查，禁止触发模型调参；不触碰 `confirm holdout`，不自动上线生产。

## 标准执行步骤

### Step 1：一键刷新底表与读取态势
先运行内置引导脚本（自动刷新 `daily_metrics_ledger.csv` + `failure_slices.jsonl`，若进化树不存在则初始化，已存在则续接）：

```bash
python3 /data/code/skills/hft-evolution-loop/scripts/bootstrap_loop.py \
  --py-root /home/x/py \
  --artifacts-dir /home/x/www/results/202611/artifacts \
  --campaign-dir /home/x/py/docs/research/evolution/t2-core6-20261120 \
  --root-account dce_t2 \
  --symbols eb,eg,pp,l,y,pg \
  --max-nodes 10 --max-depth 3
```
核对输出的剩余预算、Top 失效切片与 `negative_index.jsonl` 历史死路；若预算耗尽或无有效非执行类失效切片，直接停下汇报。

### Step 2：立题并登记进化树节点
从 Top 失效切片提出**可证伪假设**、竞争解释与 `falsifier`，在 `/home/x/py` 中调用 `exp/evolution_tree.py:add_node` 登记节点 `N-00k`（声明 `parent_id`、`branch_type`、`editable_surface`、`touched_files`）。若返回 `INVALID_SANDBOX`，立即放弃该方案并换路线。

### Step 3：隔离沙盒改动与自检
使用 `exp/sandbox_guard.py:create_sandbox_worktree` 在独立 `git worktree` 中完成改动，运行 `check_git_worktree_diff` 确认零越界，并为改动补齐 `pytest` 单测且跑绿。

### Step 4：四级漏斗验证
- **Stage 1（微对照 + 早停）**：跑最小开发窗后执行：
  ```bash
  python3 backtest.py diagnose --input <stage1.json> --mcse <v> --cumulative-trials <N> --markdown
  ```
  未过 Decimal 现金核账、SNR/MCSE 门槛或去最大贡献日转负 → 直接剪枝记 `REJECTED`。
- **Stage 2（多窗 OOS + 滑点/费用压测）**：
  ```bash
  python3 backtest.py stress-test --input <stage2.json> --fee-multiplier 1.2 --slippage-ticks 0.5 --markdown
  ```
  费用 ×1.2、额外 0.5 tick 滑点、联合压测、去最好日与分品种×session 改善比例任一不通过 → 记 `REJECTED`。
- **Stage 3（正式门禁 → 影子晋级）**：`backtest.py finish` + `analyze/promotion_gate.py`（双北极星 `dret` + `avgnwt` + 动态曝光 `effective_k_sigma`）通过后，标为 `PROMOTED_SHADOW`。
- 如需核对实盘成交单保真度，直接跑 `python3 backtest.py fidelity-check --input <fidelity.json> --markdown`。

### Step 5：写回进化树与停止判定
每个节点完成后必须调用 `exp/evolution_tree.py:record_verdict` 写回终态并刷新 `tree.md`，清理临时沙盒 worktree。仅在以下条件停止并总结：达成 `PROMOTED_SHADOW`、节点/深度预算耗尽、连续无效收敛、用户叫停、或需人工审批生产/封存数据。
