# YouTube 字幕提取与归档

此分支用于 YouTube 全文/字幕归档；普通时间点问答直接用 `watch`。先读该 Skill；复用其下载、解析和导出器，不建立第二套抓取实现。

## 获取与语言核对

```bash
python3 "<WATCH_DIR>/scripts/watch.py" "<VIDEO_URL>" \
  --detail transcript --no-whisper --no-print-transcript --out-dir "<EVIDENCE_DIR>"
```

- 优先已有原始字幕，无需为有字幕的视频下载整段媒体或配置 ASR。`--no-print-transcript` 只隐藏控制台全文，不裁剪本地文件。读取完整文件或分段读取，不用截断的工具输出代表全文。
- 核对 `info` 的标题、作者、发布日期、时长、`language`、`available_subtitles` 和实际 `subtitle_info`。明确需要某轨时加 `--subtitle-lang zh` / `en`；默认轨不保证就是源语言，缺少源语言字段时必须保留未知。请求语言不可用后的 fallback 不能称为所请求语言。
- `manual` 表示上传字幕轨，不保证人工逐字校对，也可能是译文；`automatic`、机器翻译轨和 ASR 应各自注明。视频标题、说明和字幕语言不能单独证明实际口语语言。
- 平台要求登录、限流或安全验证时保留现有证据、明确阻塞；不用绕过方案或无止境重试。无字幕时再判断已有授权的 ASR 是否可用；不能从简介补造讲话。

## 落盘、复用与完整性

`watch` 保存 `transcript.json`（元信息、segments、来源、原始字幕位置、范围与诊断）、`transcript.txt`（所取文字）和 `transcript.md`（时间戳与说明）。保留原始 VTT；去重后的文本不是原始证据的替代物。元信息是白名单投影，不公开整份 yt-dlp 响应、签名媒体地址或认证信息。

已有证据不重新下载。可离线重导出旧 `transcript.json`：

```bash
python3 "<WATCH_DIR>/scripts/export_transcript.py" "<SAVED_TRANSCRIPT_JSON>" \
  --out-dir "<EXPORT_DIR>"
```

若已取到另一个字幕轨或修复了解析器，使用原始 VTT 与**同一视频**的缓存元信息重放：

```bash
python3 "<WATCH_DIR>/scripts/export_transcript.py" "<CAPTIONS_VTT>" \
  --info-json "<SOURCE_INFO_JSON>" --subtitle-lang zh --subtitle-kind manual \
  --out-dir "<EXPORT_DIR>"
```

语言和类型按实际轨填写，不照抄示例。没有原始 VTT 时，旧 JSON 无法恢复已经丢掉的台词。导出器退出 `0` 表示非空且记录范围处理完整，`4` 表示部分/缺失/完整性未知，仍保留产物；不是允许全文分发或已完成 Notion 写入的标志。

`complete` 只针对 `completeness_scope`：字幕文件解析完，不等于所有讲话都有字幕。核对片段数、首尾时间、解析错误、已知失败区间；字幕前后空白不自动算静音或缺词。损坏 cue 标为 `partial`，无法定位的错误不能编造缺失时间。`coverage.speech_verified=false` 提醒尚未逐段对照音频。完整视频内容还涉及关键画面，按正文提示查图表；仅字幕提取不声称视觉覆盖。

## 交付

沿用 [delivery.md](delivery.md) 的交付范围与授权，不在这里重复判断。提取成功和可交付全文分开；已批准摘要替代后直接归档，不再次问同一问题。全文、译文和摘要名称必须与实际一致；Notion 归档保留来源、时间戳、轨道类型和缺失说明，写完读回验证。纯本机路径不等于 Notion 附件。
