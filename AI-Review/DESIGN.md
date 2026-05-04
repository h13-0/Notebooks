# AI Review Design

#AI-Review

## 1. ReviewUnit 规则

ReviewUnit 是 AI Review 的最小审查单位。

规则：

1. 按 Markdown 1-6 级标题划分；
2. 一个标题及其下方正文，直到下一个任意级别标题之前，构成一个 ReviewUnit；
3. 如果两个标题之间没有正文内容，则跳过；
4. 文件开头在第一个标题前的正文可作为 `_preamble` ReviewUnit；
5. ReviewUnit ID 使用 `ru000001` 形式递增；
6. ReviewUnit ID 写入原文 AI-Review 折叠块，并作为 Obsidian 块 ID 使用；
7. 文件路径、标题路径只作为 locator，不作为稳定 ID；
8. 段落内容 hash 用于判断是否需要复查。

## 2. 原文 AI-Review 折叠块

每个被审查的非空 ReviewUnit 后必须插入一个 AI-Review 折叠块。

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

规则：

1. 折叠块不显示 topic；
2. 折叠块必须显示当前 ReviewUnit ID；
3. issue 文件通过 `[[source.md#^ru000001]]` 引用原文块；
4. 折叠块是机器管理区域，除 checkbox 外不建议人工修改；
5. hash 计算时必须忽略整个 AI-Review 折叠块和尾随块 ID。

## 3. 语言规则

1. 所有面向用户的输出主语言必须是简体中文；
2. 所有写入 Markdown 的 issue、Dashboard、状态说明、warning 和运行日志主语言必须是简体中文；
3. 必要的专业外文单词、命令、路径、模型名、配置字段、API 字段和代码可以保留英文；
4. 模型投票 JSON 的字段名保持英文，字段值中的自然语言内容应使用简体中文。

## 4. Hash 规则

计算 ReviewUnit hash 时，应进行归一化：

1. 忽略 AI-Review 自动插入块；
2. 统一换行符为 `
`；
3. 删除段前段后空行；
4. 连续多个空行压缩；
5. 删除行尾空格；
6. 保留代码块内容，不做语义格式化；
7. 表格不自动重排；
8. 附件按原始 bytes 计算 hash；
9. SVG 转 PNG 仅用于多模态审查，不写入笔记仓库。

## 5. Issue 生命周期

Issue 状态包括：

1. `Open`
2. `Closed`
3. `Superseded`
4. `Unknown`

规则：

1. issue ID 使用 `ar0001` 形式递增十六进制；
2. `ar0000` 保留不用；
3. issue ID 永不复用；
4. issue 永远不合并；
5. issue 永远不跨 ReviewUnit 复用；
6. 一个 ReviewUnit 可以有多个 issue；
7. Correct 不生成 issue 文件；
8. 问题修复后移动到 `Closed/`；
9. 旧问题被新问题替代时移动到 `Superseded/`；
10. 无法判断的问题进入 `Unknown/`。

## 6. 严重等级

固定等级：

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

当前主模型默认开放投票权限。主模型投票结果必须像其他投票模型一样进入统一加权评分，并在 issue 的模型投票表中显式记录。

最终等级按加权得分决定：

```text
score(severity) = Σ(model_weight × model_confidence)
```

最终等级为得分最高且达到该等级阈值的 severity。

每个 severity 都可以单独设置阈值。

## 8. Topic 规则

Issue 文件中必须包含 topic。

示例：

```yaml
topic:
  - rkdeveloptool
  - MaskROM/Loader
  - 分区备份
```

规则：

1. topic 不在原文反向折叠块中显示；
2. topic 用于 Dashboard 聚合和筛选；
3. topic 应尽量短，优先使用技术关键词、概念名、命令名、模块名；
4. 一个 issue 推荐 1-5 个 topic。

## 9. 人工备注区

Issue 文件必须包含人工备注区：

```markdown
## 人工备注

<!-- user-notes:start -->

<!-- user-notes:end -->
```

规则：

1. AI 可以读取人工备注；
2. AI 复查时应参考人工备注；
3. AI 不得覆盖、删除、改写人工备注；
4. 如果人工备注边界损坏，应停止更新该 issue 并 warning。

## 10. 不允许直接修改正文

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
