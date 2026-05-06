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

| Slash Command | 行为 |
|---|---|
| `/ai-review` | `identity --changed --dry-run` → `/ai-review prepare --changed --dry-run` → `/ai-review vote` 生成 `findings[]` → `ai-review vote` → `ai-review merge --dry-run` |
| `/ai-review apply` | `identity --changed --apply` → `/ai-review prepare --changed --apply` → `/ai-review vote` → `ai-review vote` → `ai-review merge --apply` |
| `/ai-review all` | `identity --all --dry-run` → `/ai-review prepare --all --dry-run` → `/ai-review vote` → `ai-review vote` → `ai-review merge --dry-run` |
| `/ai-review all apply` | `identity --all --apply` → `/ai-review prepare --all --apply` → `/ai-review vote` → `ai-review vote` → `ai-review merge --apply` |
| `/ai-review issue ar0001` | `/ai-review prepare --issue ar0001 --dry-run` → `/ai-review vote` → `ai-review merge --dry-run` |

## host-current 流程

```text
/ai-review
  ↓
当前 Codex/Cursor 会话模型作为主模型
  ↓
CLI identity 校验或写入稳定 ReviewUnit ID
  ↓
/ai-review prepare skill 写入 .state/tasks
  ↓
/ai-review vote skill 写入 .state/votes/host-current，其中包含 findings[]
  ↓
普通终端 ai-review vote 调用外部 voter，对每个 finding 投 support/oppose/skip
  ↓
聚合器按权重和置信度评分
  ↓
ai-review merge dry-run 或事务化写入
```

## 独立 CLI 降级

如果用户不在 Codex/Cursor 环境中运行，普通 CLI 只能执行 `identity`、确定性 `prepare` 辅助、外部 `vote`、`merge`、`dashboard` 和 `check`。`host-current` 投票必须由 `/ai-review vote` skill 写入。
