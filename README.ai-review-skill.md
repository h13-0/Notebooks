# AI Review Skill Root Files

这些文件应放在笔记仓库根目录。

## 包含内容

- `.ai-review.yaml`：非敏感主配置；
- `.ai-review-secrets.template.yaml`：敏感配置模板；
- `.gitignore.ai-review.snippet`：需要追加到 `.gitignore` 的片段；
- `AGENTS.ai-review.md`：给 Codex、Cursor 等 agent 读取的规则；
- `.codex/commands/*.md`：推荐的 Codex slash command 包装模板；
- `.cursor/rules/ai-review.mdc`：推荐的 Cursor rule；
- `ai-review.cmd` / `ai-review.sh`：仓库根目录命令入口；
- `scripts/ai-review.sh` / `scripts/ai-review.ps1`：可选命令包装脚本。

## 注意

这些文件定义入口和规则，不等同于完整 CLI 实现。完整执行逻辑应由 `ai-review` CLI 提供。`/ai-review` 只应调用 CLI。
