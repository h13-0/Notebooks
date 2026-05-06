# AI Review Design

#AI-Review

## 0. 维护同步约束

AI Review 能力的设计文档、skill 说明和工具实现必须一起演进。任何协议、流程、命令语义、状态文件或编码规则变更，都应同时检查并更新：

1. `AI-Review/` 下的设计和协议文档；
2. `skills/ai-review/SKILL.md` 以及实际会被 agent 读取的 AI Review skill 副本；
3. `tools/ai-review/`、入口脚本和相关 CLI 帮助说明。

如果某一层无需改动，变更说明中应明确写出原因，避免设计、skill 和实现长期漂移。

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
    - "Readme.md"
    - "AGENTS.ai-review.md"
    - "AI-Review-SLASH_COMMANDS.md"
    - "README.ai-review-skill.md"
```

规则：

1. 黑名单在 Markdown 文件扫描阶段生效，命中后不生成 ReviewUnit。
2. 黑名单支持目录名和仓库相对路径 glob。
3. `AI-Review/`、`skills/`、`.codex/`、`.cursor/`、`tools/ai-review/`、`README.md`、`AGENTS.ai-review.md`、`AI-Review-SLASH_COMMANDS.md`、`README.ai-review-skill.md` 等 AI Review 自身产物、skill、命令模板和工具实现默认应排除。
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
4. `PendingVote`
5. `Rejected`

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
10. 投票缺失或失败比例过高的问题进入 `PendingVote/`。
11. 投票完整性足够但分数低于阈值的问题进入 `Rejected/`。

## 6. 严重等级

| 等级 | 含义 | Obsidian Callout |
|---|---|---|
| Enhance | 建议补充重点知识 | `[!tip]` |
| Minor | 轻微错误或不严谨 | `[!attention]` |
| Major | 明显错误，可能误导理解 | `[!bug]` |
| Critical | 严重错误，核心结论错误 | `[!danger]` |
| Unknown | 无法判断，需要人工确认 | `[!question]` |

## 7. 多模型投票规则

一个 ReviewUnit 可以有多个候选 bug finding。主模型必须先提出 `findings[]` 清单；每个 finding 独立投票、独立计分、独立进入 issue 生命周期。

主模型 finding 包含：

1. `finding_id`；
2. severity；
3. confidence；
4. topic；
5. 问题摘要；
6. 建议修改；
7. 是否需要多模态；
8. 使用的上下文和外部来源。

主模型对每个 finding 的初始票为支持票：

```text
main_score = main_model_weight × confidence
```

外部 voter 只能对主模型提出的 finding 投 `support`、`oppose` 或 `skip`：

```text
support_score = +1 × model_weight × confidence
oppose_score = -1 × model_weight × confidence
skip_score = 0
```

每个 finding 最终得分：

```text
score(finding) = main_score + Σ(support_score) + Σ(oppose_score)
```

完整性规则：

1. 有投票权限的模型包括 `host-current` 和配置中启用的外部 voter。
2. `requires_multimodal=true` 的 finding 只能由支持多模态的模型投票；不支持多模态的模型视为无投票权，不计入缺失比例。
3. 对有投票权模型，失败或未投票比例高于 `voting.max_missing_vote_ratio` 时，该 finding 进入 `PendingVote`，并输出 warning。
4. 完整性通过后，`score >= voting.issue_score_threshold` 的 finding 进入 `Open`。
5. 完整性通过但分数低于阈值的 finding 进入 `Rejected`。
6. 失败模型不得被转成 `Unknown` 票；`Unknown` 不再作为默认 issue 状态使用。

## 7.1 Identity / Prepare / Vote / Merge 工作流

AI Review 必须使用可恢复的四阶段工作流；旧的 `review`、`prepare-host`、`merge-host` 同步桥接流程不再作为入口保留。

1. `identity` 是确定性 CLI 阶段，负责给非空 ReviewUnit 写入稳定 AI-Review 块。
2. 空标题段、空正文段、仅 AI-Review 块构成的段落必须跳过，不分配 ID。
3. `identity` 必须保留已有 AI-Review 块内容；仅为缺失块的段落新增最小 identity 块。
4. `identity --dry-run` 只预览；`identity --apply` 才允许修改源文。
5. `identity --apply` 遇到 dirty、未初始化或 HEAD 不匹配的子仓库时必须跳过该子仓库并输出 warning，不得因此阻止主仓库其他安全路径写入。
6. `prepare` 是 task 生成阶段，task 必须在此阶段写入 `AI-Review/.state/tasks/{task_id}.json`。
7. `.\ai-review.cmd prepare`（Linux/macOS 可用 `./ai-review.sh prepare`）负责确定性扫描、identity 校验、候选上下文构建、task JSON 原子写入和 `tasks-index.json` 更新。
8. `/ai-review prepare` 是 skill 工作流，必须基于 CLI 生成的候选信息补全 AI-assisted 上下文裁剪、Obsidian 引用取舍、必要联网来源和最终 prompt。
9. `prepare` 必须基于已经存在的 `unit=ruXXXXXX` 身份块工作；如果目标段落没有 identity，应先运行 `identity --apply`。
10. 默认 `prepare` 是增量的：已有 task 且 `unit_id + content_hash + schema_version` 兼容时必须跳过，除非显式指定重新生成。
11. 当前会话模型必须读取候选段落，按标题、内容、引用关系和审查目标决定最终 task。
12. 当前会话模型必须解析 Obsidian 引用，并把必要的 `[[note#Heading]]`、`[[note#^blockid]]` 目标段落拼接进 task 上下文。
13. 当前会话模型在必要时必须联网查询权威资料，并把来源写入 task 的 `external_sources` 或等价字段。
14. Task 文件必须包含 `version`、`task_id`、`unit_id`、`task_hash`、定位信息、原文内容、引用上下文、AI 选择/裁剪后的上下文、外部资料来源和完整 prompt。
15. `/ai-review prepare --dry-run` 和 `.\ai-review.cmd prepare --dry-run` 只打印将生成的 task 列表和上下文/资料来源摘要，不得写入 `.state/tasks` 或 `tasks-index.json`。
16. `/ai-review prepare --unit ru000123 --regenerate` 可重新生成单个段落；`/ai-review prepare --all --regenerate` 可重新生成全范围。
17. `/ai-review vote` 只代表当前 Codex/Cursor 会话模型投票，必须为每个 task 写入 `findings[]` 到 `AI-Review/.state/votes/host-current/{task_id}.json`。
18. `/ai-review vote` 默认增量跳过已有且 `task_hash` 一致的 host-current vote；除非显式指定重新投票。
19. `/ai-review vote` 不得调用外部模型 API；外部模型投票必须由普通终端显式运行 `.\ai-review.cmd vote` 或 `./ai-review.sh vote`。
20. 外部 `.\ai-review.cmd vote` / `./ai-review.sh vote` 只读取 task 文件和 host-current findings，并把每个模型对每个 finding 的 `support/oppose/skip` 写入 `AI-Review/.state/votes/{model_id}/{task_id}.json`。
21. 如果已有 vote 文件且其中 `task_hash` 与当前 task 一致，外部 vote 阶段必须跳过该任务。
22. 失败模型不得写入 vote 文件，也不得生成 `Unknown` 票。
23. `merge` 阶段只读取 task 文件、host-current findings 和外部 vote 文件，逐 finding 聚合。
24. `merge` 必须重新读取源文并校验 `unit_id` 和 `content_hash`；块缺失或 hash 不一致时不得写入旧结果。
25. `host-current`、外部 API 模型、人工补充模型都只是不同的 `model_id`，聚合阶段只按 finding 和投票权处理。
26. `merge --apply` 才允许写入 issue、源文件 AI-Review 折叠块、Dashboard 和 ledger。

## 7.2 外部 Vote CLI 交互规则

外部 voter CLI 必须面向长时间并发审查设计。

1. `.\ai-review.cmd vote` 命令必须并行请求多个外部模型，并支持按模型配置 `concurrency`。
2. CLI 必须实时显示每个活跃任务的模型名、task id、状态、耗时、近似 token 速度、token 消耗和一行流式输出预览。
3. 流式输出预览最多占用一行；内容过长时用省略号保留尾部。
4. 流式请求下，`request_timeout_sec` 表示 socket 空闲超时；只要服务端持续输出 chunk，就不应被判定为无响应。
5. `stream_total_timeout_sec` 是防止无限输出的总时长上限，默认应足够宽松以允许复杂 review 长时间运行。
6. 用户按 Ctrl+C 时，CLI 必须取消尚未开始和尚未写入文件的任务，并等待正在写入文件的原子写入完成后退出。
7. 中断后再次运行 `vote` 必须通过 `task_hash` 跳过已完成投票，从未完成任务恢复。

## 7.3 编码与写入规则

AI Review 写入 task、vote、ledger 和 issue 时必须保持 UTF-8 语义完整。

1. 不得通过会把非 ASCII 字符替换为 `?` 的终端管道生成 task 或 vote。
2. 生成脚本、skill 和 CLI 必须把自然语言字段作为 UTF-8 文本处理。
3. JSON 写入前必须拒绝疑似编码损坏内容，例如连续问号 `????` 或 Unicode replacement character `�`。
4. 如果发现已写入的 task/vote 出现编码替换，必须先修复或删除该文件，再继续 vote/merge。
5. 外部模型基于损坏 task 生成的 vote 视为无效，不应进入 merge。

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
3. 无 finding 的段落不列历史 issue，也不列历史 topic；只保留当前块 ID 和 Dashboard 链接。

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
5. `AI-Review/PendingVote/`；
6. `AI-Review/Rejected/`；
7. `AI-Review/Dashboard.md`；
8. `AI-Review/.state/`。

## 14. 输出语言

所有自然语言输出主语言必须是简体中文。允许保留必要的专业外文单词、命令、路径、代码、API 字段、模型名和配置键名。
