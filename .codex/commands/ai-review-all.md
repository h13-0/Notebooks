# /ai-review-all

所有自然语言输出必须以简体中文为主。

执行前读取 AI Review 规范文档，然后调用：

```bash
ai-review review --all --dry-run
```

如果用户明确要求写入全仓库 Review，再调用：

```bash
ai-review review --all --apply
```

不得绕过 CLI 手动写入仓库。
