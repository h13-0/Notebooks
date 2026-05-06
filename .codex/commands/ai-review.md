请使用简体中文执行 AI Review。当前 Codex 会话模型就是 `host-current` 主模型，必须通过四阶段流程亲自完成 prepare 与 host-current vote。

默认流程：

1. 读取 `AI-Review/SLASH_COMMANDS.md` 和相关设计文档。
2. 调用 `.\ai-review.cmd identity --changed --dry-run`；如果缺少 identity 且用户允许写入，再调用 `.\ai-review.cmd identity --changed --apply`。
3. 执行 `/ai-review prepare --changed --dry-run` 的 skill 逻辑：读取候选 ReviewUnit，补全必要上下文和外部来源，写入或预览 `AI-Review/.state/tasks/{task_id}.json`。
4. 执行 `/ai-review vote` 的 skill 逻辑：读取 `AI-Review/.state/tasks/*.json`，为每个 task 生成符合 `AI-Review/MODEL_PROTOCOL.md` 的主模型投票 JSON，并写入 `AI-Review/.state/votes/host-current/{task_id}.json`。
5. 提示用户在普通终端运行 `.\ai-review.cmd vote` 生成外部 voter 投票。
6. 调用 `.\ai-review.cmd merge --dry-run` 预览聚合结果；只有用户明确要求写入时才使用 `--apply`。

要求：

- 投票中的 `model_id` 必须是 `host-current`。
- 投票中的 `model_role` 必须是 `main`。
- 自然语言字段主语言必须是简体中文。
- 不得直接修改原文正文。
- 不得调用外部模型 API；外部 voter 只能由 `.\ai-review.cmd vote` 运行。
- 写入 task/vote 前后必须检查 `????` 和 `�`，发现疑似编码损坏必须停止。
