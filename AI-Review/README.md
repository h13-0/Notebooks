# AI Review

#AI-Review

AI Review 用于对本笔记仓库中的 Markdown 段落进行自动审查。它会按标题切分笔记内容，结合 Obsidian 引用上下文和多个模型投票结果，给出正确性、补充建议、潜在错误和需要人工确认的问题。

这个目录同时保存审查结果、问题列表、Dashboard 和运行状态。普通笔记阅读者主要查看 `Dashboard.md`、源文中的 AI Review 折叠块，以及 `Open/`、`Unknown/` 里的 issue。

## 功能简介

AI Review 会做这些事：

1. 按 Markdown 标题把笔记切分成 ReviewUnit。
2. 解析当前段落里的 Obsidian 链接，例如 `[[note#Heading]]` 和 `[[note#^blockid]]`，把被引用段落作为上下文提供给模型。
3. 让当前 Codex/Cursor 会话模型和外部模型分别投票。
4. 聚合所有成功投票，得到最终等级。
5. 在源文中写入简短的 AI Review 折叠块。
6. 对非 Correct 的结论生成独立 issue 文件。
7. 生成 `Dashboard.md`，汇总当前问题、Unknown 项和主题分布。

AI Review 不会直接改写你的正文、标题、代码块或表格。它只维护 AI Review 折叠块、issue 文件、Dashboard 和 `.state/` 状态文件。

## 如何查看

常用入口：

- `Dashboard.md`：总览当前审查状态。
- `Open/`：当前仍需要处理的问题。
- `Unknown/`：模型无法判断、需要人工确认的问题。
- `Closed/`：已经修复并关闭的问题。
- `Superseded/`：被新问题替代的旧 issue。

源文中的 AI Review 折叠块会显示该段的审查状态：

```markdown
<!-- ai-review:start unit=ru000001 -->
> [!bug]- AI Review `ru000001`
> - [ ] [[AI-Review/Open/ar0001-Major-example|ar0001]]
> `2026-05-05`
<!-- ai-review:end -->
```

Correct 段落通常只保留一个简短状态和 Dashboard 链接：

```markdown
<!-- ai-review:start unit=ru000002 -->
> [!success]- AI Review `ru000002`
> - [[AI-Review/Dashboard|Dashboard]]
> `2026-05-05`
<!-- ai-review:end -->
```

## 如何使用

在仓库根目录运行：

```powershell
.\ai-review.cmd prepare --changed
.\ai-review.cmd vote
.\ai-review.cmd merge --dry-run
```

确认聚合结果无误后写入：

```powershell
.\ai-review.cmd merge --apply
```

审查全仓库或限制数量：

```powershell
.\ai-review.cmd prepare --all --limit 20
.\ai-review.cmd vote
.\ai-review.cmd merge --dry-run
```

只预览将生成哪些 task，不写入队列：

```powershell
.\ai-review.cmd prepare --all --limit 20 --dry-run
```

如果在 Codex/Cursor 中通过 `/ai-review` 使用，当前会话模型应读取 `AI-Review/.state/tasks/*.json`，并把自己的投票写入：

```text
AI-Review/.state/votes/host-current/{task_id}.json
```

外部模型投票写入：

```text
AI-Review/.state/votes/{model_id}/{task_id}.json
```

`vote` 可被中断和恢复。重新运行时，hash 一致且已经完成的投票会自动跳过。

## 详细规则

### ReviewUnit

ReviewUnit 是最小审查单位：

1. 一个标题及其下方正文构成一个 ReviewUnit，直到下一个同级或更高级标题前结束。
2. 空标题段不会生成 ReviewUnit。
3. 每个 ReviewUnit 有稳定 ID，例如 `ru000001`。
4. 内容 hash 用于判断该段是否需要重新投票。

### 等级

| 等级 | 含义 |
|---|---|
| Correct | 内容正确 |
| Enhance | 建议补充或表述更严谨 |
| Minor | 轻微错误或不严谨 |
| Major | 明显错误，可能误导理解 |
| Critical | 严重错误，核心结论错误 |
| Unknown | 无法判断，需要人工确认 |

失败、超时或返回格式错误的模型不会参与投票，也不会被自动转成 `Unknown`。

### Issue 生命周期

1. `Open`：当前仍存在的问题。
2. `Closed`：问题已经修复。
3. `Superseded`：旧问题被新问题替代。
4. `Unknown`：需要人工确认。

issue 不合并、不复用、不跨 ReviewUnit 共享。Correct 段落不生成 issue。

### 人工备注

issue 文件中会保留人工备注区：

```markdown
<!-- user-notes:start -->

<!-- user-notes:end -->
```

AI Review 不会覆盖或删除这里的内容。

### 扫描范围

AI Review 默认不会把自身目录、skill、工具实现和 IDE 配置作为普通笔记审查对象。具体黑名单在 `.ai-review.yaml` 的 `scan.exclude_paths` 中配置。

## 维护文档

用户通常只需要读本文件和 `Dashboard.md`。更底层的规则和实现细节在：

- `DESIGN.md`：设计规范。
- `CONFIG_REFERENCE.md`：配置说明。
- `MODEL_PROTOCOL.md`：模型投票 JSON 协议。
- `IMPLEMENTATION.md`：实现说明。
- `SLASH_COMMANDS.md`：命令入口说明。
