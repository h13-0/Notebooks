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

## 3. 主模型规则

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
5. 独立 CLI 无法访问 `host-current` 时，必须报错，除非用户显式切换到 `configured` 主模型。

## 4. Issue 生命周期

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

## 5. 严重等级

| 等级 | 含义 | Obsidian Callout |
|---|---|---|
| Correct | 正确 | `[!success]` |
| Enhance | 建议补充重点知识 | `[!tip]` |
| Minor | 轻微错误或不严谨 | `[!attention]` |
| Major | 明显错误，可能误导理解 | `[!bug]` |
| Critical | 严重错误，核心结论错误 | `[!danger]` |
| Unknown | 无法判断，需要人工确认 | `[!question]` |

## 6. 多模型投票规则

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

## 7. Topic 规则

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

## 8. Issue 引用源块 ID

Issue 文件必须引用原始 ReviewUnit 块 ID，例如：

```markdown
## 原文位置

- [[Linux/rkdeveloptool.md#^ru000001]]
```

原文折叠块中必须包含 `unit=ru000001`，并建议在需要兼容 Obsidian 块引用时额外保留 `^ru000001`。

## 9. 人工备注区

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

## 11. 输出语言

所有自然语言输出主语言必须是简体中文。允许保留必要的专业外文单词、命令、路径、代码、API 字段、模型名和配置键名。
