# AI Review

#AI-Review

本目录用于保存笔记仓库的 AI Review 结果、状态文件、统计面板和设计文档。

AI Review 的目标是：

1. 按 Markdown 标题段落审查笔记内容；
2. 调用多个 AI 模型进行投票；
3. 根据模型权重、置信度和严重等级阈值生成 Review 结果；
4. 在原 Markdown 标题段后插入精简的 Obsidian 折叠块；
5. 对错误、补充建议、未知问题生成独立 issue 文件；
6. 支持中断恢复、重复运行、手动勾选已修复后复查；
7. 支持 CLI、Cursor、Codex 等环境运行。

## 目录结构

```text
AI-Review/
  Open/           当前仍存在的问题
  Closed/         已修复的问题
  Superseded/     被新问题替代的问题
  Unknown/        无法判断、需要人工确认的问题
  Dashboard.md    自动生成的总览面板

  .state/         机器状态文件，不建议人工编辑
```

## 核心原则

1. AI Review 不直接修改原始正文；
2. AI 只允许修改 AI-Review 折叠块、issue 文件、Dashboard 和状态文件；
3. ReviewUnit 按 1-6 级 Markdown 标题划分；
4. 空标题段跳过，不插入 AI Review 块；
5. issue ID 使用 `ar0001` 形式递增，永不复用；
6. issue 永远不合并、不跨段落复用；
7. Correct 段落不生成 issue 文件；
8. 反向折叠块不显示 topic；
9. issue 文件中必须记录 topic，并引用原文 ReviewUnit 块 ID；
10. API key、base URL 等敏感配置不得进入仓库；
11. 写入前必须检查主仓库和相关 submodule 均干净且与 upstream 同步。

## 原文折叠块示例

有问题时：

```markdown
<!-- ai-review:start unit=ru000001 -->
> [!bug]- AI Review `ru000001`
> - [ ] [[AI-Review/Open/ar0001-Major-Loader与MaskROM概念混用|ar0001]]
> `2026-05-04` · GPT-5.5/DeepSeek
<!-- ai-review:end -->
^ru000001
```

正确时：

```markdown
<!-- ai-review:start unit=ru000002 -->
> [!success]- AI Review `ru000002`
> - [[AI-Review/Dashboard|Dashboard]]
> `2026-05-04` · GPT-5.5/DeepSeek
<!-- ai-review:end -->
^ru000002
```

说明：

- `ru000001` 是 ReviewUnit ID，也是 issue 文件回链到原文时使用的块 ID；
- 反向折叠块中不展示 topic；
- topic 只记录在 issue 文件和 Dashboard 聚合中。
