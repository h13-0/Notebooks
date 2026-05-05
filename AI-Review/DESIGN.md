# AI Review Design

#AI-Review

## 1. ReviewUnit 规则

ReviewUnit 是 AI Review 的最小审查单位。

1. 按 Markdown 1-6 级标题划分。
2. 一个标题及其下方正文，直到下一个任意级别标题之前，构成一个 ReviewUnit。
3. 如果两个标题之间没有正文内容，则跳过，不生成 ReviewUnit，不插入 AI Review 折叠块。
4. 文件开头在第一个标题前的正文可作为 `_preamble` ReviewUnit。
5. ReviewUnit ID 使用 `ru000001` 形式递增。
6. ReviewUnit ID 写入原文 AI-Review 折叠块。
7. 文件路径、标题路径只作为 locator，不作为稳定 ID。
8. 段落内容 hash 用于判断是否需要复查。

## 2. Hash 规则

计算 ReviewUnit hash 时，应进行归一化：

1. 忽略 AI-Review 自动插入块。
2. 统一换行符为 `\n`。
3. 删除段前段后空行。
4. 连续多个空行压缩。
5. 删除行尾空格。
6. 保留代码块内容，不做语义格式化。
7. 附件按原始 bytes 计算 hash。
8. SVG 转 PNG 仅用于多模态审查，不写入笔记仓库，可放到系统临时目录。

## 3. 扫描黑名单规则

AI Review 必须支持配置扫描黑名单，用于排除不应作为普通笔记审查对象的目录或文件模式。

配置示例：

```yaml
scan:
  exclude_paths:
    - "AI-Review"
    - "skills"
    - ".codex"
    - ".cursor"
    - "tools/ai-review"
    - "AGENTS.ai-review.md"
    - "AI-Review-SLASH_COMMANDS.md"
    - "README.ai-review-skill.md"
```

规则：

1. 黑名单在 Markdown 文件扫描阶段生效，命中后不生成 ReviewUnit。
2. 黑名单支持目录名和仓库相对路径 glob。
3. `AI-Review/`、`skills/`、`.codex/`、`.cursor/`、`tools/ai-review/`、`AGENTS.ai-review.md`、`AI-Review-SLASH_COMMANDS.md`、`README.ai-review-skill.md` 等 AI Review 自身产物、skill、命令模板和工具实现默认应排除。
4. 即使未显式配置，`.git/`、`.obsidian/`、`.codex/`、`.cursor/`、`__pycache__/` 和当前 `review_dir` 也必须默认排除。
5. 黑名单只影响扫描范围，不影响 CLI 显式维护 `AI-Review/` 下 issue、Dashboard 和 state 文件。

## 4. 主模型规则

主模型支持三种来源：

| 模式 | 含义 | 适用场景 |
|---|---|---|
| `host-current` | 跟随当前 Codex/Cursor 会话模型 | `/ai-review`、Cursor Agent、Codex IDE/CLI |
| `configured` | 使用 `.ai-review.yaml` 和 `.ai-review-secrets.yaml` 中显式配置的 API 模型 | 独立 CLI、CI、本地脚本 |
| `none` | 不使用主模型 | 不推荐，仅用于特殊测试 |

默认模式是 `host-current`。

规则：

1. 在 Codex/Cursor 环境中，执行 `/ai-review` 时，当前会话模型就是主模型。
2. 主模型默认拥有投票权限。
3. 主模型投票必须进入统一加权评分，不能在聚合阶段偷偷覆盖其他投票。
4. 主模型投票必须在 issue 文件的模型投票表中可见。
5. 独立 CLI 无法直接访问 `host-current`；当前会话模型必须通过 task/vote 文件桥接参与投票。

## 5. Issue 生命周期

Issue 状态包括：

1. `Open`
2. `Closed`
3. `Superseded`
4. `Unknown`

规则：

1. issue ID 使用 `ar0001` 形式递增十六进制。
2. `ar0000` 保留不用。
3. issue ID 永不复用。
4. issue 永远不合并。
5. issue 永远不跨 ReviewUnit 复用。
6. 一个 ReviewUnit 可以有多个 issue。
7. Correct 不生成 issue 文件。
8. 问题修复后移动到 `Closed/`。
9. 旧问题被新问题替代时移动到 `Superseded/`。
10. 无法判断的问题进入 `Unknown/`。

## 6. 严重等级

| 等级 | 含义 | Obsidian Callout |
|---|---|---|
| Correct | 正确 | `[!success]` |
| Enhance | 建议补充重点知识 | `[!tip]` |
| Minor | 轻微错误或不严谨 | `[!attention]` |
| Major | 明显错误，可能误导理解 | `[!bug]` |
| Critical | 严重错误，核心结论错误 | `[!danger]` |
| Unknown | 无法判断，需要人工确认 | `[!question]` |

## 7. 多模型投票规则

每个模型输出：

1. severity；
2. confidence；
3. topic；
4. 问题摘要；
5. 建议修改；
6. 是否需要多模态；
7. 是否使用了上下文。

最终等级按加权得分决定：

```text
score(severity) = Σ(model_weight × model_confidence)
```

最终等级为得分最高且达到该等级阈值的 severity。

每个 severity 都可以单独设置阈值。

模型调用失败规则：

1. 超时、限流、HTTP 错误、返回空内容、返回 JSON 格式错误的模型视为本 ReviewUnit 投票失败。
2. 失败模型不得生成 `Unknown` 投票，也不得参与加权评分。
3. `Unknown` 只能由成功返回的模型显式投出。
4. 如果一个 ReviewUnit 没有任何成功投票，则跳过该 ReviewUnit，并输出 warning。

## 7.1 Task / Vote / Merge 工作流

AI Review 必须支持可恢复的三阶段工作流，并逐步以该工作流取代旧的同步式主模型/投票模型耦合流程。

1. `prepare` 必须是 AI-assisted 阶段，由 Codex/Cursor 当前会话模型通过 skill 编排完成。
2. 普通 CLI 不得提供 `prepare` 子命令；因为 CLI 无法主动与 Codex/Cursor 当前会话模型通信，也无法独立完成必要的联网判断和上下文选择。
3. 当前会话模型必须读取候选段落，按标题、内容、引用关系和审查目标决定最终 task。
4. 当前会话模型必须解析 Obsidian 引用，并把必要的 `[[note#Heading]]`、`[[note#^blockid]]` 目标段落拼接进 task 上下文。
5. 当前会话模型在必要时必须联网查询权威资料，并把来源写入 task 的 `external_sources` 或等价字段。
6. Task 文件必须包含 `task_id`、`task_hash`、定位信息、原文内容、引用上下文、AI 选择/裁剪后的上下文、外部资料来源和完整 prompt。
7. `/ai-review prepare --dry-run` 只打印将生成的 task 列表和上下文/资料来源摘要，不得写入 `.state/tasks` 或 `tasks-index.json`。
8. `/ai-review prepare` 写入 `AI-Review/.state/tasks/{task_id}.json`；写入内容必须已经过当前会话模型准备，不得只是机械字符串切分结果。
9. `vote` 阶段只读取 task 文件，并把每个成功投票写入 `AI-Review/.state/votes/{model_id}/{task_id}.json`。
10. 如果已有 vote 文件且其中 `task_hash` 与当前 task 一致，`vote` 阶段必须跳过该任务。
11. 失败模型不得写入 vote 文件，也不得生成 `Unknown` 票。
12. `merge` 阶段只读取 task 文件和 vote 文件，所有 reviewer 一视同仁参与加权聚合。
13. `host-current`、外部 API 模型、人工补充模型都只是不同的 `model_id`，聚合阶段不得再区分“主模型”和“投票模型”。
14. Codex/Cursor 当前会话模型参与投票时，应读取 task 文件，并把投票写入 `AI-Review/.state/votes/host-current/{task_id}.json`。
15. `merge --apply` 才允许写入 issue、源文件 AI-Review 折叠块、Dashboard 和 ledger。

## 7.2 外部 Vote CLI 交互规则

外部 voter CLI 必须面向长时间并发审查设计。

1. `vote` 命令必须并行请求多个模型，并支持按模型配置 `concurrency`。
2. CLI 必须实时显示每个活跃任务的模型名、task id、状态、耗时、近似 token 速度、token 消耗和一行流式输出预览。
3. 流式输出预览最多占用一行；内容过长时用省略号保留尾部。
4. 流式请求下，`request_timeout_sec` 表示 socket 空闲超时；只要服务端持续输出 chunk，就不应被判定为无响应。
5. `stream_total_timeout_sec` 是防止无限输出的总时长上限，默认应足够宽松以允许复杂 review 长时间运行。
6. 用户按 Ctrl+C 时，CLI 必须取消尚未开始和尚未写入文件的任务，并等待正在写入文件的原子写入完成后退出。
7. 中断后再次运行 `vote` 必须通过 `task_hash` 跳过已完成投票，从未完成任务恢复。

## 8. Topic 规则

Issue 文件中必须包含 topic。

```yaml
topic:
  - rkdeveloptool
  - MaskROM/Loader
  - 分区备份
```

规则：

1. topic 不在原文反向折叠块中显示。
2. topic 用于 Dashboard 分维度聚合。
3. Correct 段落不列历史 issue，也不列历史 topic；只保留当前块 ID 和 Dashboard 链接。

## 9. Issue 引用源块 ID

Issue 文件必须引用原始 ReviewUnit 块 ID，例如：

```markdown
## 原文位置

- [[Linux/rkdeveloptool.md#^ru000001]]
```

原文折叠块中必须包含 `unit=ru000001`，并建议在需要兼容 Obsidian 块引用时额外保留 `^ru000001`。

## 10. Obsidian 引用上下文

AI Review 构建上下文时必须解析当前 ReviewUnit 中的 Obsidian 引用。

支持：

1. `[[note]]`
2. `[[note#Heading]]`
3. `[[note#^blockid]]`
4. `[[note|Alias]]`
5. `![[image.png]]`

规则：

1. 当配置 `context.include_outlink_blocks: true` 时，CLI 应把 `[[note#Heading]]` 对应标题段落拼接到模型上下文。
2. 当引用为 `[[note#^blockid]]` 时，CLI 应定位目标文件中的块 ID，并拼接该块所属段落；如果块 ID 标记在标题上，则拼接该标题下的完整 ReviewUnit。
3. 拼接内容必须标明来源链接，且受 `context.max_outlink_chars` 限制。
4. 找不到目标文件或块 ID 时，只 warning，不得强行编造上下文。
5. 该上下文仅供审查，不得写回原文正文。

## 11. 联网资料规则

当前宿主主模型 `host-current` 在必要时必须联网查询权威资料。

必要场景包括：

1. 当前知识不足以判断；
2. 事实可能随版本、标准、API、内核行为或产品文档变化；
3. 需要核对官方手册、标准、源码文档或厂商文档；
4. 多个 voter 分歧较大，需要外部证据裁决。

规则：

1. 联网资料应优先使用官方文档、标准、源码、论文等一手来源。
2. 投票 JSON 必须在 `external_sources` 字段列出 URL 或可追溯来源。
3. `summary` 或 `evidence` 必须说明哪些判断来自外部资料。
4. 无法联网或来源不足时，应降低 confidence 或返回 Unknown。

## 12. 人工备注区

Issue 文件必须包含人工备注区：

```markdown
## 人工备注

<!-- user-notes:start -->

<!-- user-notes:end -->
```

规则：

1. AI 可以读取人工备注。
2. AI 复查时应参考人工备注。
3. AI 不得覆盖、删除、改写人工备注。
4. 如果人工备注边界损坏，应停止更新该 issue 并 warning。

## 13. 不允许直接修改正文

AI Review 不得直接修改：

1. 普通正文；
2. 标题；
3. 代码块；
4. 表格；
5. 用户手写备注。

AI Review 只允许修改：

1. 原文中的 AI-Review 折叠块；
2. `AI-Review/Open/`；
3. `AI-Review/Closed/`；
4. `AI-Review/Superseded/`；
5. `AI-Review/Unknown/`；
6. `AI-Review/Dashboard.md`；
7. `AI-Review/.state/`。

## 14. 输出语言

所有自然语言输出主语言必须是简体中文。允许保留必要的专业外文单词、命令、路径、代码、API 字段、模型名和配置键名。
