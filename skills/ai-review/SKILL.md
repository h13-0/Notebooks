# AI Review Skill

## 目标

在笔记仓库中执行 AI Review：按 Markdown 标题段审查，调用主模型和多个 voter 模型投票，生成 Obsidian 反向折叠块、issue 文件和 Dashboard。

## 强制规则

1. 所有自然语言输出主语言必须是简体中文。
2. 必要的专业外文单词、路径、命令、代码、API 字段、模型名可以保留原文。
3. 在 Codex/Cursor 环境中，`/ai-review` 默认使用当前会话模型作为主模型，即 `host-current`。
4. 主模型默认拥有投票权限，参与 `模型权重 × 置信度` 加权评分。
5. CLI 是唯一权威执行路径；slash command 只是快捷入口。
6. AI Review 不得直接修改原文正文，只能修改 AI-Review 折叠块、issue 文件、Dashboard 和状态文件。
7. issue 永远不合并、不复用、不跨段落共享。
8. 原文折叠块不显示 topic；topic 只写入 issue 文件和 Dashboard。
9. CLI 构建上下文时必须解析 Obsidian 引用，必要时把 `[[note#Heading]]` 和 `[[note#^blockid]]` 对应段落拼接给模型。
10. 当前宿主主模型 `host-current` 在必要时必须联网查询权威资料，并在投票 JSON 的 `external_sources` 中列出来源。
11. 外部 voter 应优先使用流式请求；超时语义应按“空闲超时”处理，不能把持续输出但总耗时较长的响应误判为无响应。
12. 推荐使用 `prepare / vote / merge` 三阶段流程；`host-current` 与外部模型都必须把结果写入 `AI-Review/.state/votes/{model_id}/{task_id}.json`，聚合阶段不再区分主模型和投票模型。
13. 执行 `/ai-review` 时，如果需要当前 Codex/Cursor 会话模型参与投票，应先运行 `ai-review prepare ...`，读取 `.state/tasks/*.json`，逐个生成符合 `AI-Review/MODEL_PROTOCOL.md` 的 JSON，并写入 `.state/votes/host-current/*.json`。
14. 已失败或未成功返回协议 JSON 的外部模型不得写入 vote 文件，不得被转成 `Unknown`。

## 必读文档

执行前应读取：

1. `AI-Review/README.md`
2. `AI-Review/DESIGN.md`
3. `AI-Review/IMPLEMENTATION.md`
4. `AI-Review/MODEL_PROTOCOL.md`
5. `AI-Review/CONFIG_REFERENCE.md`
6. `AI-Review/SLASH_COMMANDS.md`

## 推荐入口

```bash
ai-review review --changed --dry-run
ai-review review --changed --apply
ai-review review --all --limit 20
ai-review review --resume
ai-review prepare --changed --dry-run
ai-review vote
ai-review merge --dry-run
```

在 Codex/Cursor 中，推荐使用 `/ai-review` 快捷入口。
