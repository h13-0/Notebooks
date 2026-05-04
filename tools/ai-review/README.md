# ai-review CLI Wrapper

本目录仅放置 AI Review CLI 的说明。真正实现可以是 Python、Node、Rust 或其他语言，但必须暴露统一命令：

```bash
ai-review review --changed --dry-run
ai-review review --changed --apply
ai-review review --resume
ai-review dashboard
ai-review check
```

如果当前配置为 `models.main.mode: host-current`，普通终端 CLI 不能直接假装拥有主模型，必须从 Codex/Cursor 的 `/ai-review` 入口运行，或使用 `--main configured`。
