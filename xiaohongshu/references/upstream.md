# 来源与适配边界

运行时基于 https://github.com/autoclaw-cc/xiaohongshu-skills ，固定提交 `b043748282a57e347c52f517dfb59819121134ab`。MIT 许可及版权保留在 `runtime/LICENSE`。本地维护的是固定快照，不在任务执行时自动拉取最新版。

完整吸收五类工作流：登录与会话、搜索和读取、图文/视频/长文发布、互动、复合内容运营。合并为一个渐进加载入口，避免五个 Skill 重复触发。读取图文保留本仓库已有的身份校验、顺序下载、逐页 OCR 和视频 handoff。

运行时保留上游业务操作，必要适配包括：本地二维码、不自动启动服务/浏览器、访问受限不重导航、严格媒体缺失与描述长度检查、本地 Origin 限制、外部写操作显式声明，以及笔记导出。

有意不接入：在聊天中收短信验证码、原始网络/Cookie 日志、主动风控探测、浏览器伪装、限制后换 token/入口、取消即云端保存、凑字数改稿。移除扩展的 cookies/webRequest 权限与日志拦截器，保留上传必要的 debugger 权限。诊断只说明观察到的事实，不照搬上游对平台内部加密/封禁机制的推测。

上游没有完整自动化测试；本地测试验证适配边界和通信，不替代真实账号下的端到端验证。页面 DOM、标题规则、发布入口及平台限制都可能变化。扩展加载/登录/发布分别报告验证状态，不能用 CLI --help 成功冒充已成功发帖。

## 本地验证

在仓库根目录执行：

```bash
xiaohongshu/runtime/.venv/bin/python -m unittest discover -s xiaohongshu/tests -v
node xiaohongshu/tests/test_extension.cjs
python3 -m unittest discover -s read-xiaohongshu/tests -v
python3 .system/skill-creator/scripts/quick_validate.py xiaohongshu
```

覆盖写操作声明、准确笔记身份、最小快照、并发锁、禁止自动启动、二维码本地处理、访问受限停止、正文不截断、缺失素材不跳过、发布超时未知，以及真实本地 WebSocket 握手/路由/网页 Origin 拒绝。Chrome API 使用替身测试；不发布真实内容，不将这些测试称为账号端到端验证。
