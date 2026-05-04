# /ai-review

你是 AI Review 的快捷入口。所有自然语言输出必须以简体中文为主，必要的命令、路径、配置键名和专业术语可以保留英文。

执行前必须读取：

1. `AI-Review/README.md`
2. `AI-Review/DESIGN.md`
3. `AI-Review/IMPLEMENTATION.md`
4. `AI-Review/MODEL_PROTOCOL.md`
5. `AI-Review/CONFIG_REFERENCE.md`
6. `AI-Review/SLASH_COMMANDS.md`
7. `.ai-review.yaml`

默认执行：

```bash
ai-review review --changed --dry-run
```

如果用户明确要求写入或使用 apply 参数，执行：

```bash
ai-review review --changed --apply
```

如果 `ai-review` CLI 不存在或不可用，不得写入仓库，只能用简体中文说明缺失项。
