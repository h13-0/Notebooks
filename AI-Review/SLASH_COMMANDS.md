# AI Review Slash Commands

#AI-Review

本文档定义 `/ai-review` 快捷入口的推荐行为。

## 核心原则

1. `/ai-review` 是快捷入口，不是完整实现；
2. `/ai-review` 必须调用 `ai-review` CLI；
3. CLI 是唯一权威执行路径；
4. agent 不应绕过 CLI 手动批量修改笔记、issue、Dashboard 或 `.state`；
5. 如果 CLI 不存在或不可用，agent 只能给出 dry-run 级别建议，不应写入仓库。

## 推荐命令映射

| 快捷命令 | CLI 命令 | 含义 |
|---|---|---|
| `/ai-review` | `ai-review review --changed --dry-run` | 默认审查 Git 变更范围，只预览不写入 |
| `/ai-review apply` | `ai-review review --changed --apply` | 审查 Git 变更范围并写入 |
| `/ai-review all` | `ai-review review --all --dry-run` | 全仓库预览审查 |
| `/ai-review all apply` | `ai-review review --all --apply` | 全仓库审查并写入 |
| `/ai-review resume` | `ai-review review --resume` | 从上次中断状态恢复 |
| `/ai-review issue ar0001` | `ai-review review --issue ar0001 --dry-run` | 复查指定 issue |
| `/ai-review dashboard` | `ai-review dashboard` | 重新生成 Dashboard |
| `/ai-review check` | `ai-review check` | 只执行环境和 Git 检查 |

## Codex CLI / Codex IDE 建议

自定义 slash command 应只做三件事：

1. 读取 `AI-Review/README.md`、`DESIGN.md`、`IMPLEMENTATION.md`、`MODEL_PROTOCOL.md`、`CONFIG_REFERENCE.md` 和本文件；
2. 根据用户输入选择对应 CLI 命令；
3. 执行 CLI，并用简体中文汇总结果。

不要把完整 Review 逻辑写进 slash command prompt。

## Cursor 建议

Cursor 中建议通过 Rules 或终端命令调用 CLI：

```bash
ai-review review --changed --dry-run
ai-review review --changed --apply
ai-review review --resume
```

如果 Cursor agent 发现 `ai-review` CLI 不存在，应停止写入并提示用户先安装或实现 CLI。

## 输出语言

无论在 Codex、Cursor、CLI 还是其他 agent 环境下，面向用户的自然语言主语言必须是简体中文。必要的命令、路径、配置字段、模型名和 API 字段可以保留英文。
