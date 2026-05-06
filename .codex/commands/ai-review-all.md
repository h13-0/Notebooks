请使用简体中文执行全仓库 AI Review 预览。当前 Codex 会话模型就是 `host-current` 主模型，必须通过四阶段流程亲自完成 prepare 与 host-current vote。

默认流程：

1. 读取 `AI-Review/SLASH_COMMANDS.md` 和相关设计文档。
2. 调用 `.\ai-review.cmd identity --all --dry-run` 预览 identity 状态；如用户允许写入，再运行对应 `--apply`。
3. 执行 `/ai-review prepare --all --dry-run` 的 skill 逻辑；如用户指定 limit，追加 `--limit N`。
4. 执行 `/ai-review vote` 的 skill 逻辑，生成 `AI-Review/.state/votes/host-current/{task_id}.json`。
5. 提示用户在普通终端运行 `.\ai-review.cmd vote` 生成外部 voter 投票。
6. 调用 `.\ai-review.cmd merge --dry-run` 预览聚合结果。

要求：

- 投票中的 `model_id` 必须是 `host-current`。
- 投票中的 `model_role` 必须是 `main`。
- 自然语言字段主语言必须是简体中文。
- 不得直接修改原文正文。
- 不得调用外部模型 API；外部 voter 只能由 `.\ai-review.cmd vote` 运行。
