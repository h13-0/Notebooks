# AI Review Skill

## 目标

在笔记仓库中执行 AI Review：按 Markdown 标题段审查，调用主模型和多个 voter 模型投票，生成 Obsidian 反向折叠块、issue 文件和 Dashboard。

## 强制规则

1. 所有自然语言输出主语言必须是简体中文。
2. 必要的专业外文单词、路径、命令、代码、API 字段、模型名可以保留原文。
3. 在 Codex/Cursor 环境中，`/ai-review` 默认使用当前会话模型作为主模型，即 `host-current`。
4. 主模型默认拥有投票权限；主模型必须先提出 `findings[]` 候选 bug 清单，每个 finding 的初始分数为 `主模型权重 × 置信度`。
5. CLI 是唯一权威执行路径；slash command 只是快捷入口。
6. AI Review 不得直接修改原文正文，只能修改 AI-Review 折叠块、issue 文件、Dashboard 和状态文件。
7. issue 永远不合并、不复用、不跨段落共享。
8. 原文折叠块不显示 topic；topic 只写入 issue 文件和 Dashboard。
9. `/ai-review prepare` 必须由当前 Codex/Cursor 会话模型参与完成，不得只调用 CLI 做机械字符串切分。
10. prepare 阶段必须自动解析 Obsidian 引用，必要时把 `[[note#Heading]]` 和 `[[note#^blockid]]` 对应段落拼接到 task 上下文中。
11. prepare 阶段在必要时必须联网查询权威资料，并把来源写入 task 的 `external_sources` 或等价字段；必须包含正文或足以独立判断的关键摘录，供无联网能力的外部 voter 和 issue 修改者核实。
12. 当前宿主主模型 `host-current` 在投票时如果继续使用外部资料，也必须在投票 JSON 的 `external_sources` 中列出来源。
13. `/ai-review prepare` 是 skill 工作流：可以调用 `.\ai-review.cmd prepare` 获取候选 task，但最终上下文裁剪、引用取舍、联网来源和 prompt 必须由当前会话模型参与确认。
14. `/ai-review vote` 是 skill 工作流，只负责当前 Codex/Cursor 会话模型自己的投票，必须写入 `.state/votes/host-current/*.json`，不得调用外部模型 API。
15. 外部 voter 必须由普通终端显式运行 `.\ai-review.cmd vote`（Linux/macOS 可用 `./ai-review.sh vote`）调用；外部 voter 应优先使用流式请求，超时语义应按“空闲超时”处理。
16. 必须使用 `identity / prepare / vote / merge` 四阶段流程；`host-current` 写入 findings，外部模型对每个 finding 写入 `support/oppose/skip`，聚合阶段逐 finding 计算。
17. `/ai-review prepare` 前必须确保目标段落已有稳定 AI-Review identity 块；缺失时应提示或运行 `.\ai-review.cmd identity --apply`。
18. prepare 和 vote 默认必须增量处理：已有 task/vote 且 hash 一致时跳过；只有显式重新生成标志才覆盖。
19. 执行 `/ai-review vote` 时，应读取 `.state/tasks/*.json`，逐个生成符合 `AI-Review/MODEL_PROTOCOL.md` 的 `findings[]` JSON；一个段落有多个独立问题时必须提出多个 finding，不得压缩成一个段落级 verdict。
20. 已失败或未成功返回协议 JSON 的外部模型不得写入 vote 文件，不得被转成 `Unknown`。
21. 写入 task/vote 时必须保持 UTF-8；不得用会把中文替换为 `?` 的 PowerShell 管道或临时脚本写入自然语言字段。
22. 写入前如发现连续问号 `????` 或 Unicode replacement character `�`，必须停止并修复编码来源，不能继续 vote/merge。
23. 开发或修改 AI Review 能力时，必须同步更新设计文档、skill 说明和工具实现；如果某一层无需变更，应在回复中说明原因。

## 必读文档

执行前应读取：

1. `AI-Review/README.md`
2. `AI-Review/DESIGN.md`
3. `AI-Review/IMPLEMENTATION.md`
4. `AI-Review/MODEL_PROTOCOL.md`
5. `AI-Review/CONFIG_REFERENCE.md`
6. `AI-Review/SLASH_COMMANDS.md`

## 推荐入口

```bash
ai-review identity --changed --dry-run
ai-review identity --changed --apply
/ai-review prepare --changed
/ai-review vote
/ai-review merge --dry-run
ai-review prepare --changed --dry-run
ai-review vote
ai-review merge --dry-run
```

在 Codex/Cursor 中，推荐使用 `/ai-review` 快捷入口。

## `identity` 工作流

1. `identity` 是普通 CLI 功能，不需要 AI 判断。
2. 运行 `.\ai-review.cmd identity --changed --dry-run` 或 `.\ai-review.cmd identity --all --dry-run` 预览；Linux/macOS 可使用 `./ai-review.sh ...`。
3. 确认后运行 `.\ai-review.cmd identity ... --apply` 或 `./ai-review.sh identity ... --apply` 写入缺失的 AI-Review identity 块。
4. 空段落、空标题段和只包含 AI-Review 块的段落必须跳过。
5. 已有 AI-Review 块必须原样保留，不得降级成待审查块。
6. `identity` 必须幂等：段落正文和已有块未变化时，重复运行不得刷新日期、移动块或重分配 ID。
7. 相同内容段落不得因为 hash 相同共享 `unit_id`；发现重复 ID 时应保留第一处明确归属，其它重复处重新分配唯一 ID 并输出 warning。
8. ReviewUnit 只按 `# text` / `#\ttext` 形式的 Markdown 标题切分；`#tag`、`#中文标签` 等 Obsidian 标签必须留在当前段落正文中。

## `/ai-review prepare` 工作流

1. 读取 `AI-Review/DESIGN.md`、`AI-Review/MODEL_PROTOCOL.md` 和 `.ai-review.yaml`。
2. 确认目标段落已有 `unit=ruXXXXXX` identity 块；缺失则先运行 identity。
3. 可调用 CLI 或本地代码作为候选段落发现工具，但不得把机械切分结果直接当成最终 task。
4. 默认跳过已有 task 且 `task_hash` 一致的段落；`--regenerate` 才覆盖。
5. 支持 `--unit ruXXXXXX` 定位单段，支持 `--all --regenerate` 重新生成全部扫描范围。
6. 对每个候选 ReviewUnit，读取原文、标题路径、相邻必要上下文和已有 AI Review 块。
7. 解析该段中的 Obsidian 引用，自动定位并摘取必要目标段落；找不到目标时在 task 中记录 warning，不得编造上下文。
8. 判断是否需要联网。涉及版本、标准、API、芯片/内核行为、外部工具、厂商文档或模型知识不确定时，必须联网查询一手来源。
9. 将联网来源写入 task，至少包含 URL 或可追溯来源名、标题、用途摘要，以及正文或足以支撑判断的关键摘录；不得只写链接和 title。
10. 写入 `AI-Review/.state/tasks/{task_id}.json`；`--dry-run` 只打印 task 摘要、引用上下文摘要和外部来源摘要，不写文件。

## `/ai-review vote` 工作流

1. 只读取 `AI-Review/.state/tasks/*.json`。
2. 只生成当前会话模型 `host-current` 的 findings 清单和初始支持票。
3. 每个 task 写入 `AI-Review/.state/votes/host-current/{task_id}.json`，格式必须包含 `findings` 数组；无问题时写入空数组。
4. 如果已有 host-current vote 且 `task_hash` 一致，默认跳过；`--regenerate` 才覆盖。
5. 每个 finding 必须有稳定 `finding_id`，建议使用 `ruXXXXXX-f001`、`ruXXXXXX-f002`。
6. 外部模型投票由用户另行运行 `.\ai-review.cmd vote`，外部模型只能对已有 finding 投 `support/oppose/skip`。

## 编码安全

1. 生成 task/vote 的自然语言字段必须直接来自当前会话模型或 UTF-8 文件。
2. 不要把包含中文的内联脚本通过 PowerShell 管道传给解释器；如果必须用脚本，脚本内容应只含 ASCII 转义，或写入 UTF-8 文件后再执行。
3. 写完 task/vote 后检查 `.state/tasks` 和 `.state/votes/host-current` 中是否存在 `????` 或 `�`；存在时立即修复，不得进入 merge。
