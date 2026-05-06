请使用简体中文恢复 AI Review。当前 Codex 会话模型作为 `host-current` 主模型。

恢复方式：

1. 读取 `AI-Review/.state/tasks/*.json` 和 `AI-Review/.state/votes/`。
2. 对缺失或 `task_hash` 不一致的 `host-current` vote，重新执行 `/ai-review vote` 的 skill 逻辑。
3. 提示用户重新运行 `.\ai-review.cmd vote`，外部 voter 会按 `task_hash` 跳过已完成投票。
4. 调用 `.\ai-review.cmd merge --dry-run` 预览；用户明确要求写入时再用 `--apply`。
