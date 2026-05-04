# AI Review Model Protocol

#AI-Review

## 1. 输出语言

所有模型返回的自然语言字段必须使用简体中文为主。必要的专业外文单词、命令、路径、代码、API 字段、模型名和配置键名可以保留原文。

## 2. 模型输出必须是 JSON

每个投票模型必须返回结构化 JSON。主模型为 `host-current` 时，也必须按同一 schema 产生主模型投票。

## 3. 单模型输出格式

```json
{
  "unit_id": "ru000001",
  "model_id": "host-current",
  "model_role": "main",
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
| `model_id` | string | 模型 ID，当前宿主主模型使用 `host-current` |
| `model_role` | string | `main` / `voter` |
| `result` | string | `correct` / `issue` / `unknown` |
| `severity` | string | `Correct` / `Enhance` / `Minor` / `Major` / `Critical` / `Unknown` |
| `confidence` | number | 0 到 1 |
| `title` | string | 问题标题 |
| `topic` | string[] | topic 关键词，只用于 issue 和 Dashboard，不写入原文反向块 |
| `summary` | string | 问题摘要 |
| `evidence` | string[] | 依据 |
| `suggested_fix` | string | 建议修改 |
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
  "model_id": "host-current",
  "model_role": "main",
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
  "model_id": "deepseek-v4-pro",
  "model_role": "voter",
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

主模型如果启用投票，必须作为普通加权 voter 参与计算，不得在聚合阶段隐式覆盖结果。
