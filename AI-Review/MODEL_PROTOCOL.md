# AI Review Model Protocol

#AI-Review

## 1. 模型输出必须是 JSON

每个投票模型必须返回结构化 JSON。

当前主模型默认具有投票权限。主模型投票必须使用与其他模型相同的 JSON 格式，并进入同一套加权评分流程。

## 2. 语言要求

JSON 字段名保持英文，字段值中的自然语言内容必须使用简体中文。必要的专业外文单词、命令、路径、API 字段、模型名、代码片段可以保留英文。

## 3. 单模型输出格式

```json
{
  "unit_id": "ru000001",
  "result": "issue",
  "severity": "Major",
  "confidence": 0.82,
  "title": "Loader 与 MaskROM 概念混用",
  "topic": [
    "rkdeveloptool",
    "MaskROM/Loader"
  ],
  "summary": "原文将 Loader 模式和 MaskROM 模式的触发条件混为一谈。",
  "evidence": [
    "原文中说……",
    "上下文中……"
  ],
  "suggested_fix": "建议改为……",
  "requires_multimodal": false,
  "context_used": [
    "current_unit",
    "outlinks",
    "backlinks"
  ],
  "relation_to_previous_issue": "same_issue"
}
```

## 4. 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `unit_id` | string | ReviewUnit ID |
| `result` | string | `correct` / `issue` / `unknown` |
| `severity` | string | `Correct` / `Enhance` / `Minor` / `Major` / `Critical` / `Unknown` |
| `confidence` | number | 0 到 1 |
| `title` | string | 问题标题，使用简体中文为主 |
| `topic` | string[] | topic 关键词，只用于 issue 和 Dashboard，不写入原文折叠块 |
| `summary` | string | 问题摘要，使用简体中文 |
| `evidence` | string[] | 依据，使用简体中文 |
| `suggested_fix` | string | 建议修改，使用简体中文 |
| `requires_multimodal` | boolean | 是否依赖图片/多模态 |
| `context_used` | string[] | 使用了哪些上下文 |
| `relation_to_previous_issue` | string | 与旧 issue 的关系 |

## 5. relation_to_previous_issue

允许值：

```text
same_issue
fixed
superseded
unrelated_new_issue
not_applicable
```

## 6. Correct 输出示例

```json
{
  "unit_id": "ru000001",
  "result": "correct",
  "severity": "Correct",
  "confidence": 0.91,
  "title": "",
  "topic": [
    "rkdeveloptool"
  ],
  "summary": "未发现明显问题。",
  "evidence": [],
  "suggested_fix": "",
  "requires_multimodal": false,
  "context_used": [
    "current_unit"
  ],
  "relation_to_previous_issue": "not_applicable"
}
```

## 7. Unknown 输出示例

```json
{
  "unit_id": "ru000001",
  "result": "unknown",
  "severity": "Unknown",
  "confidence": 0.74,
  "title": "图片内容无法确认",
  "topic": [
    "图片",
    "多模态"
  ],
  "summary": "当前段落依赖图片内容，但可用模型无法审查该图片。",
  "evidence": [],
  "suggested_fix": "请使用支持多模态的模型重新审查。",
  "requires_multimodal": true,
  "context_used": [
    "current_unit",
    "image"
  ],
  "relation_to_previous_issue": "not_applicable"
}
```

## 8. 聚合规则

最终等级计算：

```text
score(severity) = Σ(model_weight × confidence)
```

最终等级为得分最高且达到对应阈值的 severity。

如果没有任何等级达到阈值，则按配置降级为 `Unknown` 或 `Correct`。

主模型投票规则：

1. 主模型默认参与投票；
2. 主模型的 `weight` 从 `.ai-review.yaml` 读取；
3. 主模型投票必须显示在 issue 的模型投票表中；
4. 主模型不得在聚合阶段隐式覆盖投票结果；
5. 是否允许主模型投票可以通过配置关闭，但默认开启。

## 9. Issue 文件应引用原文块 ID

Issue 文件必须记录原文 ReviewUnit 块 ID。

示例 frontmatter：

```yaml
source_file: "Linux/rkdeveloptool.md"
source_unit_id: "ru000001"
source_block_ref: "[[Linux/rkdeveloptool#^ru000001]]"
```

正文中也应包含：

```markdown
## 原文位置

- [[Linux/rkdeveloptool#^ru000001]]
```
