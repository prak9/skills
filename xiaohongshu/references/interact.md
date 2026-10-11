# 评论、回复、点赞与收藏

“帮我写评论”默认只交付草稿；“发这条评论”需有明确对象和已批准内容。用户已明确批准时不重复审批。读文章、做竞品研究不附带点赞收藏权限；批量任务需要限定目标与内容，不能自行群发。

```bash
runtime/.venv/bin/python scripts/xhs.py --write-confirmed post-comment \
  --feed-id NOTE_ID --xsec-token TOKEN --content "用户批准的评论"
runtime/.venv/bin/python scripts/xhs.py --write-confirmed reply-comment \
  --feed-id NOTE_ID --xsec-token TOKEN --comment-id COMMENT_ID --content "用户批准的回复"
runtime/.venv/bin/python scripts/xhs.py --write-confirmed like-feed --feed-id NOTE_ID --xsec-token TOKEN
runtime/.venv/bin/python scripts/xhs.py --write-confirmed favorite-feed --feed-id NOTE_ID --xsec-token TOKEN
```

回复优先用真实 `comment-id`；只给 `user-id` 时确认对应哪条评论，不能误回同一用户的另一条。取消点赞加 `--unlike`，取消收藏加 `--unfavorite`。虽然上游按目标状态实现点赞收藏，也要核对返回状态；发送评论结果未知时先查看评论区，不重复发送。

页面验证、限流、发送被拒绝都停止并如实报告；不猜“敏感词”就是唯一原因，不自行改写用户批准内容再发。无需强制所有互动间隔相同，也不把节奏调整当成绕过限制手段。
