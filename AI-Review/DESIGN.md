# AI Review Design

#AI-Review

## 1. ReviewUnit 规则

ReviewUnit 是 AI Review 的最小审查单位。

规则：

1. 按 Markdown 1-6 级标题划分；
2. 一个标题及其下方正文，直到下一个任意级别标题之前，构成一个 ReviewUnit；
3. 如果两个标题之间没有正文内容，则跳过，不插入反向折叠块；
4. 文件开头在第一个标题前的正文可作为 `_preamble` ReviewUnit；
5. ReviewUnit ID 使用 `ru000001` 形式递增；
6. ReviewUnit ID 写入原文 AI-Review 折叠块，并追加为 Obsidian 块 ID，例如 `^ru000001`；
7. 文件路径、标题路径只作为 locator，不作为稳定 ID；
8. 段落内容 hash 用于判断是否需要复查。

## 2. Hash 规则

计算 ReviewUnit hash 时，应进行归一化：

1. 忽略 AI-Review 自动插入块；
2. 统一换行符为 `\n`；
3. 删除段前段后空行；
4. 连续多个空行压缩；
5. 删除行尾空格；
6. 保留代码块内容，不做语义格式化；
7. 附件按原始 bytes 计算 hash；
8. SVG 转 PNG 仅用于多模态审查，不写入笔记仓库。

## 3. Issue 生命周期

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

## 4. 严重等级

固定等级：

| 等级 | 含义 | Obsidian Callout |
|---|---|---|
| Correct | 正确 | `[!success]` |
| Enhance | 建议补充重点知识 | `[!tip]` |
| Minor | 轻微错误或不严谨 | `[!attention]` |
| Major | 明显错误，可能误导理解 | `[!bug]` |
| Critical | 严重错误，核心结论错误 | `[!danger]` |
| Unknown | 无法判断，需要人工确认 | `[!question]` |

## 5. 多模型投票规则

每个模型输出：

1. severity；
2. confidence；
3. topic；
4. 问题摘要；
5. 建议修改；
6. 是否需要多模态；
7. 是否使用了上下文。

当前主模型默认有投票权限。主模型投票必须和其他模型一样进入统一加权评分，不得在聚合阶段隐式覆盖其他模型。

最终等级按加权得分决定：

```text
score(severity) = Σ(model_weight × model_confidence)
```

最终等级为得分最高且达到该等级阈值的 severity。每个 severity 都可以单独设置阈值。

## 6. Topic 规则

Issue 文件中必须包含 topic。

示例：

```yaml
topic:
  - rkdeveloptool
  - MaskROM/Loader
  - 分区备份
```

原文反向折叠块中不得显示 topic。Dashboard 可以按 topic 聚合问题。

## 7. 原文回链规则

Issue 文件必须引用原文 ReviewUnit 块 ID，例如：

```markdown
- [[Linux/rkdeveloptool.md#^ru000001]]
```

原文折叠块中只显示：

1. 当前 ReviewUnit ID；
2. issue 链接，或 Correct 状态下的 Dashboard 链接；
3. 检查日期；
4. 投票模型列表。

不得在原文折叠块中显示 topic。

## 8. 人工备注区

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

## 9. 不允许直接修改正文

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
