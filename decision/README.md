# Decision

一个遵循开放 Agent Skills 结构的中文决策一体化技能，内含问题定义、决策枢纽识别、证据验证与执行复盘流程。

## 内容

- `SKILL.md`：触发范围、工作流、输出结构和质量检查。
- `references/framework.md`：详细方法论。
- `references/scoring-rubric.md`：评分锚点和阈值。
- `assets/decision-worksheet.md`：可填写工作表。
- `assets/decision-report-template.md`：正式报告模板。
- `scripts/score_options.py`：确定性加权评分脚本。
- `evals/`：示例测试提示和质量量表。
- `agents/openai.yaml`：ChatGPT/Codex 可选 UI 元数据。

## 本地安装示例

将整个 `decision` 文件夹复制到以下任一位置：

- 用户级：`$HOME/.agents/skills/decision`
- 仓库级：`<repo>/.agents/skills/decision`

然后在支持 Agent Skills 的宿主中显式调用，或让宿主根据 `description` 自动匹配。

## 评分脚本

```bash
python scripts/score_options.py assets/sample-score-input.json
python scripts/score_options.py assets/sample-score-input.json --format json
```

脚本仅使用 Python 标准库，会校验：

- 权重是否合计 100；
- 评分是否在 1–5；
- 每个方案是否覆盖全部维度；
- 是否触发硬性否决项。
