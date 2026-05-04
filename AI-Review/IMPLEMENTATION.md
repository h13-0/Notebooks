# AI Review Implementation Plan

#AI-Review

## 1. 运行环境

AI Review skill 必须支持：

1. CLI；
2. Codex CLI；
3. Codex IDE；
4. Cursor；
5. 其他可调用命令行的 agent 环境。

核心实现以 CLI 为权威执行路径，但 `/ai-review` 可以作为 Codex/Cursor 的快捷入口。

## 2. CLI 与 host-current 主模型的关系

CLI 负责：

1. Git 前置检查；
2. Markdown 扫描；
3. ReviewUnit hash；
4. 上下文构建；
5. 外部 voter 模型调用；
6. issue 生命周期；
7. 事务化写入；
8. Dashboard 更新；
9. run-state 恢复。

`host-current` 主模型负责：

1. 主模型投票；
2. 结合上下文做最终问题理解；
3. 聚合解释；
4. 生成面向用户的简体中文 issue 描述和 Dashboard 摘要。

CLI 不能天然读取当前 Codex/Cursor 的内部模型状态，因此 `/ai-review` 快捷入口应把当前会话模型接入 AI Review 流程。

## 3. 推荐命令

```bash
ai-review review
ai-review review --changed
ai-review review --all
ai-review review path/to/file.md
ai-review review path/to/folder/
ai-review review --issue ar0001
ai-review review --resume
ai-review review --dry-run
ai-review review --apply
ai-review review --limit 20
ai-review review --main configured
ai-review dashboard
ai-review check
```

默认行为：

```bash
ai-review review
```

等价于：

```bash
ai-review review --changed --dry-run
```

在普通终端中，如果配置要求 `models.main.mode: host-current`，CLI 应报错并提示：

1. 从 Codex/Cursor 的 `/ai-review` 运行；
2. 或将 `models.main.mode` 改为 `configured`；
3. 或临时使用 `--main configured`。

## 4. `/ai-review` 推荐流程

```text
/ai-review
  ↓
读取 AI-Review 规范文档
  ↓
调用 CLI 做检查与 prepare
  ↓
当前 Codex/Cursor 会话模型作为 host-current 主模型投票
  ↓
CLI 收集外部 voter 模型投票
  ↓
按 weight × confidence 聚合
  ↓
CLI 事务化写入或 dry-run 输出
```

## 5. limit 含义

`--limit N` 表示本次最多审查 N 个 ReviewUnit。

## 6. Git 前置检查

写入前必须满足：

1. 当前目录是 Git 仓库；
2. 主仓库工作区干净；
3. 主仓库暂存区干净；
4. 当前分支有 upstream；
5. `HEAD == @{u}`；
6. 执行过 `git fetch --all --prune` 后仍满足同步；
7. 相关 submodule 已初始化；
8. 相关 submodule 工作区干净；
9. 相关 submodule HEAD 与主仓库记录一致；
10. 相关 submodule HEAD 与自身 upstream 同步。

不满足则跳过对应仓库或停止运行。

## 7. Submodule 规则

允许扫描和写入 submodule 中的 Markdown 文件。

规则：

1. submodule 未初始化：跳过并 warning；
2. submodule dirty：跳过并 warning；
3. submodule HEAD 与主仓库记录不一致：跳过并 warning；
4. submodule 没有 upstream：跳过并 warning；
5. submodule 与 upstream 不同步：跳过并 warning；
6. submodule 干净且同步：允许扫描和写入。

写入 submodule 后，需要输出提交脚本。

## 8. 可中断阶段

| 阶段 | 是否可中断 |
|---|---|
| SCANNING | 可中断 |
| BUILDING_CONTEXT | 可中断 |
| VOTING | 可中断 |
| MERGING | 可中断 |
| WRITING | 不可中断 |
| VERIFYING | 不建议中断 |
| DONE | 可中断 |

## 9. 写入事务

所有写入必须事务化：

1. 写入临时文件；
2. 校验 Markdown；
3. 校验 frontmatter；
4. 校验 Obsidian 链接；
5. 更新 issue 文件；
6. 更新原文 AI-Review 块；
7. 更新 ledger；
8. 更新 Dashboard；
9. 原子替换目标文件；
10. 校验 git diff。

## 10. 异常策略

模型异常包括：

1. 超时；
2. 限流；
3. 返回格式错误；
4. 多模态能力不满足；
5. API 报错。

处理规则：

1. 该模型跳过本 ReviewUnit 的投票；
2. 同一模型同类问题只 warning 一次；
3. 如果没有可用模型，则该 ReviewUnit 标记为 Unknown 或跳过，按配置决定；
4. 主模型不可用时，不写入该 ReviewUnit。

## 11. Obsidian 语法支持范围

支持：

1. `[[Wiki Link]]`
2. `[[Wiki Link#Heading]]`
3. `[[Wiki Link#^blockid]]`
4. `[[Wiki Link|Alias]]`
5. `![[image.png]]`
6. `![[image.jpg]]`
7. `![[image.jpeg]]`
8. `![[image.webp]]`
9. `![[image.svg]]`
10. `![[note.md]]`
11. `#tag`
12. `^blockid`
13. frontmatter
14. callout/admonition
15. Mermaid 代码块
16. 普通代码块

不支持的语法应 warning，不强行解析。

## 12. 附件规则

支持：

1. 图片；
2. SVG 临时转 PNG；
3. Mermaid 按源码审查；
4. 引用到的代码文件作为上下文；
5. 小体积 zip 可尝试打开。

暂不处理：

1. PDF；
2. 视频；
3. 音频；
4. 外部网页链接。
