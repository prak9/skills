# X 公开提取、长文与线程

先读取此分支再处理 X 帖子、Article 或线程。将 `SKILL_DIR` 替换为包含 `SKILL.md` 的 `read-link` 根目录，不是本参考所在目录。脚本仅依赖 Python 标准库：

```bash
python3 "<SKILL_DIR>/scripts/fetch_x.py" "<X/Twitter post URL>" --download-images
```

使用 FxEmbed 的公开 API v2，向第三方发送的只是公开帖 ID，不读取账号、Cookie 或密钥。首次使用时说明这一来源；它不是 X 官方证据。若请求禁止第三方或内容私密，跳过此路径，使用已授权的原站访问或用户文件。不要将受保护/已删除的帖子交给镜像绕过访问限制。

接口依据：[FxEmbed API overview](https://docs.fxembed.com/api/introduction/)、[Get post](https://docs.fxembed.com/api/twitter/operations/2statusid/)。实现于 2026-09-17 核对 v2 `status` 结构，并兼容已保存的 v1 `tweet` 响应；不是对第三方长期可用性的承诺。

可选 `--out-dir DIR` 在指定父目录下创建全新尝试目录；`--json-file FILE` 重放保存的 FxEmbed 响应。每次尝试隔离，避免失败后误用上次文件。不自动重试 403/429，不安装依赖。

输出：

- `response.json`：取得的原始响应，仅作来源证据，不能默认整份发布。
- `source.txt`：帖子文字或 Article 块文字；只作提取结果，不声称保留全部富文本格式。
- `manifest.json`：原始链接、ID、作者、时间、提供方、正文依据、正文块/实体、媒体顺序、缺失项和文件指纹。
- 下载图片：只允许 X 图片 CDN，验证文件签名。视频不在此重复下载，交给 `watch`。

`text_coverage=provider_payload` 只表示处理了返回的正文，不是原站全文已证明完整；`preview_only / partial / missing` 必须继续定位缺失证据或明确交付范围。`source_completeness=unverified` 需要人工式证据核对：原页/作者同文、标题、首尾、分节和嵌入内容。网络不可得时不伪造核验通过。

脚本退出 0 表示所取正文解析成功且请求的图片下载成功；退出 4 表示预览、缺失块或图片不全，已保留可用产物；退出 2 表示请求/身份/格式失败。退出 0 不代表完成了图像阅读、视频转写、版权判断或 Notion 写入。

### 长文、线程与引用

- Article 正文优先取 `content.blocks`，不得拿 `preview_text`、分享卡片或搜索片段冒充全文。保留原始块和 `entityMap` 中的链接、引用与媒体定位；未知/atomic 块是待解析内容，不能静默删掉。
- 文章封面和 `media_entities` 清单不等于正文插图顺序。根据块内实体或原页确定位置；无法确定则单列“插图，正文位置未核验”。
- 脚本一次只取一条帖子，不能声称线程完整。用户要线程时，沿原作者回复关系核对各帖 ID、作者、顺序与终点；普通评论、引用帖、推荐内容不自动并入。无法枚举完整线程时标出已取得范围。
- 引用帖单独注明原作者；外链文章是另一个来源。不要把引用内容或评论归给主帖作者。
- 不支持的 Article-only、短链接先在网页工具中解析到原文或包含它的帖子，不猜帖子 ID。
