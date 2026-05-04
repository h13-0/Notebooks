# AI Review Skill

该 skill 用于在 Obsidian 风格 Markdown 笔记仓库中执行 AI Review。

## 强制语言规则

所有面向用户的自然语言输出、写入 issue 文件、Dashboard、warning、日志和复查说明，主语言必须使用简体中文。必要的专业外文单词、命令、路径、代码、模型名、API 字段和配置键名可以保留英文。

## 执行前必须阅读

在审查或修改文件前，必须先阅读以下文件：

1. `AI-Review/README.md`
2. `AI-Review/DESIGN.md`
3. `AI-Review/IMPLEMENTATION.md`
4. `AI-Review/MODEL_PROTOCOL.md`
5. `AI-Review/CONFIG_REFERENCE.md`
6. `.ai-review.yaml`

如果这些文件不存在，不要自行发明不兼容规则。应提示用户先放置 AI-Review 压缩包。

## 核心规则

1. 不得直接修改原始笔记正文；
2. 只允许修改 AI Review 管理的折叠块、issue 文件、Dashboard 和状态文件；
3. ReviewUnit 按 Markdown 1-6 级标题划分；
4. 空标题段跳过，不添加 AI Review 块；
5. 每个已审查的非空 ReviewUnit 必须有 AI Review 折叠块；
6. 折叠块必须显示当前 ReviewUnit ID；
7. 折叠块不得显示 topic；
8. issue 文件必须引用原文 ReviewUnit 块 ID，例如 `[[note.md#^ru000001]]`；
9. Correct ReviewUnit 不生成 issue 文件；
10. issue ID 使用 `ar0001` 形式的十六进制 ID，永不复用；
11. issue 永不合并，也不跨 ReviewUnit 共享；
12. 当前主模型默认参与投票；
13. 主模型投票必须和其他模型一样进入加权评分，并显式写入模型投票表；
14. 模型 API key 和 base URL 只允许放入 `.ai-review-secrets.yaml`，不得进入已跟踪文件；
15. 如果 CLI 可用，优先使用 CLI；
16. 如果 CLI 缺失或运行不安全，只能提供 dry-run 级别建议，不应写入文件。

## 推荐 CLI 流程

```bash
ai-review check
ai-review review --changed --dry-run
ai-review review --changed --apply
ai-review review --resume
ai-review dashboard
```

默认审查范围应为 changed files。全仓库审查必须显式使用 `--all`。

## Git 安全要求

执行写入前，主仓库和目标 submodule 必须干净并与 upstream 同步。dirty、未初始化、未同步或 HEAD 与主仓库记录不一致的 submodule 必须跳过并给出 warning。

## 管理块格式

有问题示例：

```markdown
<!-- ai-review:start unit=ru000001 -->
> [!bug]- AI Review `ru000001`
> - [ ] [[AI-Review/Open/ar0001-Major-Loader与MaskROM概念混用|ar0001]]
> `2026-05-04` · GPT-5.5/DeepSeek
<!-- ai-review:end -->
^ru000001
```

正确示例：

```markdown
<!-- ai-review:start unit=ru000002 -->
> [!success]- AI Review `ru000002`
> - [[AI-Review/Dashboard|Dashboard]]
> `2026-05-04` · GPT-5.5/DeepSeek
<!-- ai-review:end -->
^ru000002
```

topic 只允许出现在 issue 文件和 Dashboard 聚合中，绝不能出现在原文折叠块中。
