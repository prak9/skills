# 搜索、读取与证据

以下命令在 Skill 目录运行，省略解释器前缀时均指 `runtime/.venv/bin/python scripts/xhs.py`。

```bash
runtime/.venv/bin/python scripts/xhs.py list-feeds
runtime/.venv/bin/python scripts/xhs.py search-feeds --keyword "提问能力" --sort-by 最新 --note-type 图文 --publish-time 一周内
runtime/.venv/bin/python scripts/xhs.py get-feed-detail --feed-id NOTE_ID --xsec-token TOKEN
runtime/.venv/bin/python scripts/xhs.py user-profile --user-id USER_ID --xsec-token TOKEN
```

筛选值来自实际 CLI：排序为 综合/最新/最多点赞/最多评论/最多收藏；类型 不限/视频/图文；时间 不限/一天内/一周内/半年内；范围 不限/已看过/未看过/已关注；位置 不限/同城/附近。按用户目的选择，不把推荐流或热门样本当作全平台随机样本。

`feed-id` 与 `xsec-token` 来自用户提供的完整 URL 或本次获准读取的真实结果，保持配对，不编造。token 与签名 URL 只作本地检索输入；交付引用 `https://www.xiaohongshu.com/explore/NOTE_ID`。缺 token 时用户可以在 Chrome 打开准确笔记，再直接导出当前页；不搜索同名文章来替换指定来源。

## 与现有读图 Skill 衔接

```bash
# 已打开目标笔记：不重新导航，不需要复制 Cookie
runtime/.venv/bin/python scripts/xhs.py export-note --feed-id NOTE_ID --out-dir /absolute/new-output

# 有真实 token 且授权导航：访问后导出
runtime/.venv/bin/python scripts/xhs.py export-note --feed-id NOTE_ID --xsec-token TOKEN --out-dir /absolute/new-output
```

导出核对当前 URL 与 note ID，只保存目标笔记状态，不导出全部页面、Cookie 或账户存储。自动调用相邻 `read-xiaohongshu/scripts/fetch_note.py`，输出正文、图片清单和有序图片或视频 handoff。原始快照与签名媒体地址保留在本地输出目录。没有旁边的 reader 则报告缺少依赖，不谎称 OCR 完成。

拿到图片后按 `read-xiaohongshu` 逐页看图；正文 JSON 不等于图片正文，封面不等于视频字幕。图像下载只走公共 CDN，没有下载成功要标记缺页。导出的 `access_mode=html` 是通过浏览器快照解析，补充说明来源为授权 Bridge 会话。

## 评论与失败

默认只返回已加载评论；用户要求更多时使用 `--load-all-comments`，并按目的设置 `--max-comment-items`，需要时加 `--click-more-replies` / `--max-replies-threshold`。评论实际加载数、折叠回复和停止原因都要披露，不因命令名含 all 就声称全部采集。

登录不足、内容删除、身份不匹配、运行环境故障、验证码、频率限制分别报告。一次 404 或 Cookie 存在不足以推断平台内部封禁机制。验证码、访问错误或限流停止该尝试，用户处理后再明确恢复；不采用上游自动换 token/搜索入口恢复路径。不存在已验证的“每三次休息便不会被限流”规则。
