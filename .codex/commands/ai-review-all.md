请使用简体中文执行全仓库 AI Review 预览。当前 Codex 会话模型就是 `host-current` 主模型，必须亲自为每个 ReviewUnit 生成符合 `AI-Review/MODEL_PROTOCOL.md` 的主模型投票 JSON。

默认流程：

1. 读取 `AI-Review/SLASH_COMMANDS.md` 和相关设计文档。
2. 调用：
   `.\ai-review.cmd prepare-host --all --dry-run`
   如用户指定 limit，追加 `--limit N`。
3. 读取 `AI-Review/.state/host-current-prepare.json`。
4. 你作为当前会话模型，对其中 `units` 数组逐个审查，生成 JSON 投票文件：
   `AI-Review/.state/host-current-votes.json`
5. 调用：
   `.\ai-review.cmd merge-host --prepare-file AI-Review/.state/host-current-prepare.json --host-current-vote-file AI-Review/.state/host-current-votes.json --dry-run`

要求：

- 投票中的 `model_id` 必须是 `host-current`。
- 投票中的 `model_role` 必须是 `main`。
- 自然语言字段主语言必须是简体中文。
- 不得直接修改原文正文。
