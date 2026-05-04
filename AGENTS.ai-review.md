# AI Review Agent Instructions

所有 agent 在本仓库执行 AI Review 时必须遵守：

1. 主语言使用简体中文。
2. 当前 Codex/Cursor 会话模型默认是主模型 `host-current`。
3. 主模型拥有投票权限，必须输出符合 `AI-Review/MODEL_PROTOCOL.md` 的 JSON 投票。
4. 不得直接修改用户原文正文。
5. 写入必须通过 CLI 权威路径完成。
6. `/ai-review` 只是快捷入口，应调用 CLI。
7. 原文反向折叠块中不显示 topic。
8. issue 文件必须引用原始块 ID，例如 `[[source.md#^ru000001]]`。
9. API key、base URL 等敏感内容只能写入 `.ai-review-secrets.yaml`，不得写入仓库文档。
