# AI Review

#AI-Review

本目录用于保存笔记仓库的 AI Review 设计文档、审查结果、状态文件和 Dashboard。

## 核心目标

1. 按 Markdown 1-6 级标题划分 ReviewUnit。
2. 对每个非空 ReviewUnit 调用主模型和多个投票模型审查。
3. 主模型默认跟随当前 Codex/Cursor 会话模型，即 `host-current`。
4. 主模型拥有投票权限，和其他模型一样进入 `模型权重 × 置信度` 加权评分。
5. 所有自然语言输出主语言必须是简体中文，必要的专业外文单词、路径、命令、API 字段、模型名除外。
6. Correct 段落不生成 issue 文件，但仍在原文插入精简 AI Review 折叠块。
7. 非 Correct 问题生成独立 issue 文件，issue 永不合并、不复用、不跨段落共享。
8. Topic 只写入 issue 文件和 Dashboard 聚合，不在原文反向折叠块中显示。
9. AI Review 不直接修改用户原始正文，只能修改 AI-Review 折叠块、issue 文件、Dashboard 和状态文件。
10. 支持 CLI、Codex CLI、Codex IDE、Cursor 等环境运行。

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

## 原文折叠块示例

有问题：

```markdown
<!-- ai-review:start unit=ru000001 -->
> [!bug]- AI Review `ru000001`
> - [ ] [[AI-Review/Open/ar0001-Major-Loader与MaskROM概念混用|ar0001]]
> `2026-05-04` · 当前主模型/DeepSeek-V4-Pro
<!-- ai-review:end -->
```

Correct：

```markdown
<!-- ai-review:start unit=ru000002 -->
> [!success]- AI Review `ru000002`
> - [[AI-Review/Dashboard|Dashboard]]
> `2026-05-04` · 当前主模型/DeepSeek-V4-Pro
<!-- ai-review:end -->
```

注意：原文折叠块中不显示 topic。topic 只在 issue 文件和 Dashboard 中使用。
