# AI Review Agent Guide

#AI-Review

本文件面向 Codex、Cursor 等 agent，说明在本仓库执行 AI Review 时需要遵守的额外约束。

## 核心规则

1. 自然语言输出默认使用简体中文。
2. 在 Codex/Cursor 环境中，当前会话模型默认就是主模型 `host-current`。
3. 主模型必须输出符合 `AI-Review/MODEL_PROTOCOL.md` 的投票 JSON。
4. 不得直接修改用户原始正文；只允许通过 AI Review 既定流程维护 `AI-Review/` 产物和原文中的 AI Review 折叠块。
5. `/ai-review` 只是快捷入口，权威执行路径仍是 CLI 与 skill 的组合工作流。
6. issue 文件必须引用原始块 ID，例如 `[[source.md#^ru000001]]`。
7. 原文折叠块中不显示 `topic`；`topic` 只写入 issue 和 Dashboard。
8. API key、base URL 等敏感内容只能写入 `.ai-review-secrets.yaml`，不得写入仓库文档。

## 仓库内入口位置

- `AI-Review/README.md`：面向使用者的总览与日常操作说明。
- `AI-Review/SLASH_COMMANDS.md`：`/ai-review` 快捷入口与宿主环境行为约定。
- `AI-Review/DESIGN.md`：设计约束与数据流。
- `AI-Review/IMPLEMENTATION.md`：实现约束与 CLI/skill 分工。
- `AI-Review/CONFIG_REFERENCE.md`：配置说明。
- `skills/ai-review/SKILL.md` 与 `.codex/skills/ai-review/SKILL.md`：实际执行时的 skill 规则副本。

## 根目录保留项

以下文件仍保留在仓库根目录，因为它们是运行入口或配置，而不是面向用户暴露的说明文档：

- `.ai-review.yaml`
- `.ai-review-secrets.template.yaml`
- `.gitignore.ai-review.snippet`
- `ai-review.cmd`
- `ai-review.sh`
- `scripts/ai-review.ps1`
- `scripts/ai-review.sh`
