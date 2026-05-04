# AI Review Slash Commands

#AI-Review

本文件定义 `/ai-review` 在 Codex CLI、Codex IDE、Cursor 等宿主环境中的推荐行为。

## 核心原则

1. `/ai-review` 是快捷入口，不是完整实现。
2. CLI 是唯一权威执行路径。
3. 在 Codex/Cursor 环境中，`/ai-review` 默认使用当前会话模型作为主模型，即 `host-current`。
4. 主模型拥有投票权限，参与 `weight × confidence` 加权评分。
5. 所有自然语言输出主语言必须是简体中文。

## 推荐映射

| Slash Command | CLI 调用 |
|---|---|
| `/ai-review` | `ai-review review --changed --dry-run` |
| `/ai-review apply` | `ai-review review --changed --apply` |
| `/ai-review all` | `ai-review review --all --dry-run` |
| `/ai-review all apply` | `ai-review review --all --apply` |
| `/ai-review resume` | `ai-review review --resume` |
| `/ai-review issue ar0001` | `ai-review review --issue ar0001 --dry-run` |

## host-current 流程

```text
/ai-review
  ↓
当前 Codex/Cursor 会话模型作为主模型
  ↓
CLI 进行 Git 检查、扫描、上下文构建
  ↓
外部 voter 模型通过 API 投票
  ↓
host-current 主模型输出主投票 JSON
  ↓
聚合器按权重和置信度评分
  ↓
CLI dry-run 或事务化写入
```

## 独立 CLI 降级

如果用户不在 Codex/Cursor 环境中运行，并且配置是：

```yaml
models:
  main:
    mode: "host-current"
```

CLI 必须报错并提示：

```text
当前配置要求 host-current 主模型，但当前运行环境没有宿主主模型。
请从 /ai-review 运行，或将 models.main.mode 改为 configured。
```
