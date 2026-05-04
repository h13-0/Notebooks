# AI Review Agent Instructions

本仓库使用 AI Review 工作流审查 Obsidian 风格 Markdown 笔记。

## 强制语言规则

所有面向用户的自然语言输出、写入 issue 文件、Dashboard、warning、日志和复查说明，主语言必须使用简体中文。必要的专业外文单词、命令、路径、代码、模型名、API 字段和配置键名可以保留英文。

## 操作前必须阅读

在运行、修改或检查 AI Review 前，先阅读：

1. `AI-Review/README.md`
2. `AI-Review/DESIGN.md`
3. `AI-Review/IMPLEMENTATION.md`
4. `AI-Review/MODEL_PROTOCOL.md`
5. `AI-Review/CONFIG_REFERENCE.md`
6. `.ai-review.yaml`

优先使用 CLI：

```bash
ai-review check
ai-review review --changed --dry-run
ai-review review --changed --apply
ai-review review --resume
ai-review dashboard
```

## 核心规则

1. 不得直接修改笔记正文；
2. 只允许修改 AI-Review 管理的折叠块、issue 文件、Dashboard 和状态文件；
3. 原文折叠块中不得显示 topic；
4. 原文折叠块必须显示当前 ReviewUnit ID；
5. issue 文件必须引用原文块 ID，例如 `[[source.md#^ru000001]]`；
6. issue ID 永不复用、永不合并、永不跨 ReviewUnit 共享；
7. Correct ReviewUnit 不生成 issue 文件；
8. 当前主模型默认参与投票；
9. 主模型投票必须和其他模型一样进入加权评分，并显式写入模型投票表；
10. API key 和 base URL 只允许放在 `.ai-review-secrets.yaml`，不得进入已跟踪文件。
