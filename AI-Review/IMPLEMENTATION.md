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

## 1.1 维护同步约束

实现改动不得只落在单一层。修改 AI Review 的行为、协议、命令、状态文件、编码策略或 agent 工作流时，必须同步检查：

1. `AI-Review/DESIGN.md`、`AI-Review/IMPLEMENTATION.md`、`AI-Review/MODEL_PROTOCOL.md` 等设计和协议文档；
2. `skills/ai-review/SKILL.md` 以及 agent 实际加载的 AI Review skill 副本；
3. `tools/ai-review/`、`ai-review.cmd`、`scripts/ai-review.*` 和 CLI 帮助文本。

若某一层没有对应改动，应在交付说明中说明“已检查，无需变更”的原因。

## 2. CLI 与 host-current 主模型的关系

CLI 负责：

1. Git 前置检查；
2. Markdown 扫描；
3. ReviewUnit hash；
4. 确定性上下文构建；
5. 外部 voter 模型调用；
6. issue 生命周期；
7. 事务化写入；
8. Dashboard 更新；
9. run-state 恢复。

`host-current` 主模型负责：

1. 为每个 task 提出 `findings[]` 候选 bug 清单；
2. 结合上下文做最终问题理解；
3. 为每个 finding 提供初始支持票；
4. 生成面向用户的简体中文 finding 描述和建议修改。

CLI 不能天然读取当前 Codex/Cursor 的内部模型状态，因此当前会话模型必须通过 `/ai-review prepare` 和 `/ai-review vote` skill 把 task/vote 文件写入统一状态目录。CLI 只负责确定性辅助、外部 voter 和最终 merge。`/ai-review prepare` 联网查询到的资料必须以正文或关键摘录形式写入 task，CLI 外部 voter prompt 会把这些资料一并发送给无联网能力的 API 模型。

## 3. 推荐命令

```bash
ai-review identity --changed --dry-run
ai-review identity --changed --apply
ai-review prepare --changed --dry-run
ai-review prepare --changed --apply
ai-review prepare --all --limit 20 --dry-run
ai-review vote
ai-review vote --model deepseek-v4-pro
ai-review merge --dry-run
ai-review merge --apply
ai-review dashboard
ai-review check
```

默认行为：

```bash
ai-review check
```

不带子命令时只执行 `check`，不再隐式运行旧的同步审查流程。

### 3.1 配置解析

CLI 运行时优先使用 PyYAML 解析 `.ai-review.yaml`；环境缺少 PyYAML 时，必须使用内置简易解析器解析当前仓库配置所需的 YAML 子集，包括嵌套映射、标量列表以及列表中的映射项。

### 3.2 Identity 幂等性

`identity` 写入必须是保守补块流程：

1. 扫描 ReviewUnit 时先解析当前段落范围内已有的 AI-Review 块，并优先沿用块中的 `unit_id`。
2. 对已经有块且未发生重复 ID 冲突的段落，写回时原样保留该块，不刷新日期、不移动位置。
3. 只对缺失块的 ReviewUnit 新增 identity 块。
4. 不得用全局内容 hash 直接复用 `unit_id`；相同内容出现在不同 locator 时仍必须拥有不同 ReviewUnit ID。
5. 发现重复 `unit_id` 时，保留扫描顺序中第一处，其它重复处重新分配唯一 ID，并输出 warning。
6. 对当前扫描无法归属的旧 AI-Review 块，默认保留并 warning，不主动删除。

## 4. `/ai-review` 推荐流程

```text
/ai-review
  ↓
读取 AI-Review 规范文档
  ↓
ai-review identity --changed --dry-run，必要时提示用户 apply
  ↓
/ai-review prepare --changed 生成 .state/tasks
  ↓
/ai-review vote 写入 .state/votes/host-current
  ↓
用户在普通终端运行 ai-review vote，对每个 finding 写入 support/oppose/skip
  ↓
ai-review merge 按 finding 分数阈值和缺票比例聚合
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
3. 如果 finding 的失败/缺失投票比例超过 `voting.max_missing_vote_ratio`，该 finding 进入 `PendingVote`；
4. 主模型未写入 `findings[]` 时，外部 voter 和 merge 都跳过该 ReviewUnit。

## 10.1 Finding 聚合

每个 finding 独立聚合：

1. 主模型初始支持分为 `main_model.weight × finding.confidence`。
2. 外部 `support` 票为 `+1 × model.weight × confidence`。
3. 外部 `oppose` 票为 `-1 × model.weight × confidence`。
4. `skip` 不计分，但写入 issue 的跳过模型列表。
5. 分数达到 `voting.issue_score_threshold` 时进入 `Open`。
6. 分数低于阈值且投票完整性足够时进入 `Rejected`。
7. 投票完整性不足时进入 `PendingVote`。

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
