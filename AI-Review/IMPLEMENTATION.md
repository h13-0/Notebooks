# AI Review Implementation Plan

#AI-Review

## 1. 运行环境

AI Review skill 必须支持：

1. CLI；
2. Cursor；
3. Codex；
4. 其他可调用命令行的 agent 环境。

核心实现应以 CLI 为中心，Cursor/Codex 通过调用 CLI 完成任务。

## 2. 语言规则

1. 所有 CLI 输出、agent 回复、issue 文件、Dashboard、warning、日志和复查说明，主语言必须使用简体中文；
2. 必要的专业英文术语、命令、路径、代码、配置字段、模型名和 API 字段可以保留英文；
3. 模型 JSON 字段名保持英文，字段值中的自然语言内容使用简体中文；
4. 如果模型返回英文自然语言，聚合阶段应转换为简体中文后再写入文件。

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

## 4. limit 含义

`--limit N` 表示本次最多审查 N 个 ReviewUnit。

示例：

```bash
ai-review review --all --limit 20
```

表示从待审查队列中取前 20 个标题段进行审查。

## 5. Git 前置检查

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

## 6. Submodule 规则

允许扫描和写入 submodule 中的 Markdown 文件。

规则：

1. submodule 未初始化：跳过并 warning；
2. submodule dirty：跳过并 warning；
3. submodule HEAD 与主仓库记录不一致：跳过并 warning；
4. submodule 没有 upstream：跳过并 warning；
5. submodule 与 upstream 不同步：跳过并 warning；
6. submodule 干净且同步：允许扫描和写入。

写入 submodule 后，需要输出提交脚本。

示例：

```bash
cd path/to/submodule
git add -A
git commit -m "docs: update AI review results"

cd /path/to/main-repo
git add path/to/submodule AI-Review
git commit -m "docs: update AI review results"
```

## 7. 主模型投票

1. 当前主模型默认参与投票；
2. 主模型必须和其他模型一样输出模型投票 JSON；
3. 主模型投票使用 `.ai-review.yaml` 中配置的 `weight`；
4. 主模型投票必须写入 issue 的模型投票表；
5. 聚合阶段不得隐式抬高、降低或覆盖主模型投票；
6. 如需关闭主模型投票，只能通过配置 `vote_enabled: false` 或 `voting.main_model_vote_enabled: false`。

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

运行时应输出状态：

```text
[可中断] 正在构建上下文：ru000001
[可中断] 正在等待模型投票：ru000001
[不可中断] 正在写入 Review 结果：ru000001
[可中断] 写入完成：ru000001
```

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

压缩包规则：

1. 默认只支持 `.zip`；
2. 不执行压缩包内任何脚本；
3. 只读取文本类文件；
4. 限制体积和文件数量。

## 13. CLI / Cursor / Codex 协作原则

1. CLI 是唯一写入入口；
2. Cursor、Codex 等 agent 应先阅读 `AI-Review/README.md`、`DESIGN.md`、`IMPLEMENTATION.md`、`MODEL_PROTOCOL.md`、`CONFIG_REFERENCE.md`；
3. Agent 不应绕过 CLI 手动批量修改原文；
4. 如果 CLI 不存在或不可用，agent 只能给出 dry-run 级别建议，不应写入仓库；
5. Agent 的所有自然语言回复主语言必须是简体中文。
