# 创作与发布

先确认用户要的是本地文稿、网页预览、草稿箱、定时发布还是立即发布。只写文章不碰账号。需要创作/改写时使用 `writing`；参考其他笔记的结构而不复制全文、虚构经历或将来源图片默认当作可再发布素材。

准备 UTF-8 标题、正文文件及获准使用的图片/视频。路径为绝对路径；保持媒体顺序。图文需要图片，视频需要视频，不混合。媒体 URL 须来自用户或已授权可信来源；上游可下载 HTTP(S) 图片，不因没有文件扩展名就丢弃真实图片。下载/上传部分失败时停止，不能少几张图片照样发布。

标题长度用 `runtime/scripts/title_utils.py` 的计算规则预检（非 ASCII 按 UTF-16 码元加权，ASCII 半单位、总长向上取整），这是当前实现口径，页面实际校验优先。一般图文/视频标题上限 20，不凑满、不机械截断、不擅自改已确认文稿。长文编辑器限制另行检查；发布页描述超过 1000 字先修改并确认，不截成 800 字冒充原文。

## 图文/视频

```bash
runtime/.venv/bin/python scripts/xhs.py --write-confirmed fill-publish \
  --title-file /absolute/title.txt --content-file /absolute/body.txt \
  --images /absolute/1.png /absolute/2.png --tags 标签1 标签2 --visibility 公开可见

runtime/.venv/bin/python scripts/xhs.py --write-confirmed fill-publish-video \
  --title-file /absolute/title.txt --content-file /absolute/body.txt \
  --video /absolute/video.mp4 --visibility 公开可见
```

`fill-*` 不点击最终发布，但会上传媒体且可能触发平台自动保存，绝非纯本地预览；先有上传/网页预览授权。预览时核对目标账号、实际标题正文、媒体顺序、标签、可见性、原创声明和定时时区。`--original` 只能用于用户有权声明原创的内容。定时参数是 `--schedule-at` ISO8601，先明确用户时区及页面显示的执行时间，不能把已排期说成已公开。

确认这份最终内容与设置后：

```bash
runtime/.venv/bin/python scripts/xhs.py --write-confirmed click-publish
```

`publish` / `publish-video` 支持相同素材参数的一步发布，仅在用户已经明确批准最终内容和设置时使用，不以快捷方式跳过核对。命令行参数不能替代用户授权。

## 长文

`long-article --title-file ... --content-file ... [--images ...]` 填入并获取模板；`select-template --name ...` 选择真实返回模板；`next-step --content-file /absolute/description.txt` 填入独立发布描述；核对后 `click-publish`。以上均经 `scripts/xhs.py --write-confirmed`，模板不存在要报告失败。

## 取消、草稿与结果

用户取消：停止后续动作。保留已有本地文稿，报告网页是否已填表/上传；不自动 `save-draft`、删除云端内容或登出。只有明确要保存平台草稿时运行 `--write-confirmed save-draft`。

执行后核对成功提示、内容 ID/链接或创作者列表中的实际状态；函数未抛异常不等于外部状态验证。超时或网络中断时结果可能未知，先查证，避免重复发布。安全验证交给用户，不自动点击或绕过。

只读核对入口是 `runtime/.venv/bin/python scripts/xhs.py inspect-page`：读取当前页可见文本、表单文字及笔记链接，不导航、不重新点击。其 `verified:false` 表示证据仍需判断，不是发布失败。它不自动打开创作者列表；当前页证据不足时，请用户在原浏览器核对后再继续。图片顺序与实际视觉预览以浏览器为准，不凭文本宣称已全面验收。视频一步发布尚无可靠成功探测，点击后明确返回 unknown，而非“已发布”。
