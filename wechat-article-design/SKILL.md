---
name: wechat-article-design
description: 将 Markdown 或已有中文长文排成可复制到微信公众号编辑器的内联样式 HTML，提供公众号兼容性校验、主题选择、自定义配色和一键复制预览。用于“公众号排版”“微信文章排版”“把这篇 Markdown 转成公众号 HTML”“生成可粘贴富文本”“gzh 排版”等请求。只负责结构与视觉呈现，不代写文章；普通网页、落地页、PPT、海报或其他社交平台内容不要触发。
---

# WeChat Article Design

把现成文章编译为微信公众号正文片段。优先保住内容，再建立视觉层级，最后用脚本检查平台兼容性；不要把普通网页 HTML 当成公众号 HTML。

## Set the contract

1. 确认输入正文、标题、图片链接、作者信息和交付目录。输入可以是 Markdown 文本或 `.md` 文件。
2. 把用户原文视为内容边界：不得删段、改观点、虚构数字、补作者署名或添加“点赞、在看、转发”等 CTA。用户同时要求写作时，先完成写作并确认正文，再进入排版。
3. 默认交付两个文件：干净正文片段 `{stem}-wechat-{theme}.html`，以及 `{stem}-wechat-{theme}-preview.html` 预览页。
4. 需要直接发布到账号、上传图片或操作微信后台时，先说明本 skill 只生成本地文件；未经明确授权不要登录、上传或发布。

## Read the constraints

- 每次生成或修改正文 HTML 前，读取 `references/platform-contract.md`。它定义正文片段、允许标签、危险样式、图片和验证边界。
- 选择内置主题、比较视觉方向或创建项目级自定义主题时，读取 `references/themes.md`。

这些约束是保守兼容配置，不是微信官方稳定 API。没有在真实公众号编辑器粘贴验证时，不要承诺“绝对不掉格式”。

## Choose one direction

根据文章主导任务选择一套主题：

- 专业观点、行业分析、科技评论：`ink`。
- 教程、清单、方法论、工具测评：`moss`。
- 随笔、人物、文化与生活方式：`paper`。

用户已指定主题就直接采用。用户说“直接排”“一键排版”时自行选择并在交付中说明理由，不再追问。审美方向确实会改变结果且用户没有给偏好时，可以先用两套主题渲染同一短样稿供选择；不要只换颜色却保持完全相同的层级假装是不同方向。

需要自定义风格时，按 `references/themes.md` 创建项目级 JSON 主题文件并传给渲染脚本。不要修改 skill 自身来保存单个项目的品牌设置，不要从参考图复制 Logo、文字或独特构图。

## Render deterministically

优先调用随 skill 提供的渲染器：

```bash
python3 <SKILL_ROOT>/scripts/render_wechat.py article.md --theme ink -o article-wechat-ink.html
```

自定义主题：

```bash
python3 <SKILL_ROOT>/scripts/render_wechat.py article.md --theme-file brand-theme.json -o article-wechat-brand.html
```

渲染器支持标题、二三级章节、段落、显式加粗、`==高亮==`、行内代码、链接、引用、列表、代码块、图片和分割线。遇到 Markdown 表格、脚注、复杂嵌套列表或嵌入式 HTML 时，先在 Markdown 副本中转换为语义等价的简单段落或列表，并让用户能追溯到原文；不要静默遗漏。

标题优先采用代码块外的首个 H1，其次 frontmatter 的 `title`，最后使用命令行或文件名回退值。代码围栏支持至少三个反引号或波浪号及简单语言标签；结束围栏必须同类且不短于开头。块内的 `#`、Markdown 标记与空行保留为代码，未闭合围栏报错。

不要在脚本输出后随手添加 `<div>`、`class`、`<style>` 或交互脚本。需要改视觉时调整主题输入或渲染器，再重新生成完整片段。

## Validate before delivery

对干净正文运行：

```bash
python3 <SKILL_ROOT>/scripts/validate_wechat.py article-wechat-ink.html
```

ERROR 必须清零。逐条检查 WARNING：本地图片路径、外部链接或经验性兼容项可能需要用户在微信素材库中替换或实际粘贴确认。修复后重新运行，不要仅删除校验规则。

然后生成一键复制预览：

```bash
python3 <SKILL_ROOT>/scripts/wrap_preview.py article-wechat-ink.html
```

预览页可以包含浏览器所需的 CSS 和 JavaScript，但被复制的区域只能是已经校验的正文片段。若有浏览器或截图工具，检查窄屏与约 677px 内容宽度下的标题换行、段落节奏、代码溢出、图片比例和强调密度。

## Deliver

交付时给出：

- 干净正文和预览页的可点击路径；
- 采用的主题及一句选择理由；
- 校验结果和仍需人工确认的 warning；
- 操作提示：打开预览页，点击“复制正文”，粘贴到公众号编辑器后再做一次真实预览；
- 未经真实微信编辑器验证时的明确证据边界。

## Provenance

本 skill 借鉴 [gzh-design-skill](https://github.com/isjiamu/gzh-design-skill) 的“组件约束 + 产物校验 + 独立复制预览”工作流。上游采用 AGPL-3.0；本目录未复制其代码、主题或素材，渲染器、主题和校验实现均为本仓库独立实现。
