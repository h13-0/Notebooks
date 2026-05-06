# AI Review Model Protocol

#AI-Review

## 1. 输出语言

所有模型返回的自然语言字段必须使用简体中文为主。必要的专业外文单词、命令、路径、代码、API 字段、模型名和配置键名可以保留原文。

## 2. Task 输入格式

`prepare` 阶段必须为每个 ReviewUnit 写入一个 task JSON：

```json
{
  "version": 1,
  "schema_version": 1,
  "kind": "ai-review-task",
  "task_id": "ru000001",
  "unit_id": "ru000001",
  "task_hash": "sha256...",
  "content_hash": "sha256...",
  "source_file": "Linux/rkdeveloptool.md",
  "source_block_ref": "Linux/rkdeveloptool.md#^ru000001",
  "heading_path": ["rkdeveloptool", "Loader"],
  "heading": "Loader",
  "level": 2,
  "start_line": 12,
  "end_line": 34,
  "content": "原文段落...",
  "context_notes": ["引用上下文..."],
  "prepared_context": ["AI-assisted 裁剪后的上下文..."],
  "external_sources": [
    {
      "url": "https://example.com/spec",
      "title": "Spec title",
      "purpose": "核对版本行为"
    }
  ],
  "prompt": "发送给投票模型的完整提示词"
}
```

字段规则：

| 字段 | 类型 | 说明 |
|---|---|---|
| `task_id` / `unit_id` | string | ReviewUnit ID，必须一致 |
| `task_hash` / `content_hash` | string | 当前 ReviewUnit 归一化内容 hash，vote 和 merge 必须用它判断是否过期 |
| `source_file` | string | 仓库相对路径 |
| `source_block_ref` | string | Obsidian 块引用定位 |
| `context_notes` | string[] | 确定性上下文，如附件、outlink、block 引用摘录 |
| `prepared_context` | string[] | 当前会话模型选择或裁剪后的审查上下文 |
| `external_sources` | object[] | prepare 阶段联网来源；未联网时为空数组 |
| `prompt` | string | 外部 voter 和 host-current vote 使用的完整输入 |

已有 task 且 `task_hash` 与当前 ReviewUnit 一致时，`prepare` 默认跳过；显式 `--regenerate` 才覆盖。

## 3. 主模型 Findings 输出必须是 JSON

`/ai-review vote` 中的 `host-current` 主模型必须先提出候选 bug 清单。一个 ReviewUnit 可以有 0 个、1 个或多个 finding。

```json
{
  "version": 1,
  "task_id": "ru000001",
  "unit_id": "ru000001",
  "task_hash": "sha256...",
  "model_id": "host-current",
  "model_role": "main",
  "findings": [
    {
      "finding_id": "ru000001-f001",
      "severity": "Major",
      "confidence": 0.82,
      "title": "Loader 与 MaskROM 概念混用",
      "topic": ["rkdeveloptool", "MaskROM/Loader"],
      "summary": "原文将 Loader 模式和 MaskROM 模式的触发条件混为一谈。",
      "evidence": ["原文中说……"],
      "suggested_fix": "建议改为……",
      "requires_multimodal": false,
      "context_used": ["current_unit", "outlinks"],
      "external_sources": []
    }
  ]
}
```

主模型对每个 finding 的初始票等价于一张 `support` 票，分数为：

```text
main_score = main_model_weight × confidence
```

如果主模型没有发现问题，`findings` 必须为空数组，不生成 issue。

## 4. 外部 Voter 输出格式

外部 voter 只对主模型已提出的 finding 投票，不在本轮新增可 merge 的 bug。

```json
{
  "version": 1,
  "task_id": "ru000001",
  "unit_id": "ru000001",
  "task_hash": "sha256...",
  "model_id": "deepseek-v4-pro",
  "model_role": "voter",
  "votes": [
    {
      "finding_id": "ru000001-f001",
      "decision": "support",
      "confidence": 0.76,
      "rationale": "该问题成立。",
      "evidence": ["外部模型依据……"],
      "external_sources": []
    }
  ],
  "new_findings_suggestion": []
}
```

## 5. 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `unit_id` | string | ReviewUnit ID |
| `model_id` | string | 模型 ID，当前宿主主模型使用 `host-current` |
| `model_role` | string | `main` / `voter` |
| `finding_id` | string | ReviewUnit 内候选 bug ID，建议使用 `ruXXXXXX-f001` |
| `decision` | string | 外部 voter 对 finding 的投票：`support` / `oppose` / `skip` |
| `severity` | string | `Correct` / `Enhance` / `Minor` / `Major` / `Critical` / `Unknown` |
| `confidence` | number | 0 到 1 |
| `title` | string | 问题标题 |
| `topic` | string[] | topic 关键词，只用于 issue 和 Dashboard，不写入原文反向块 |
| `summary` | string | 问题摘要 |
| `evidence` | string[] | 依据 |
| `suggested_fix` | string | 建议修改 |
| `requires_multimodal` | boolean | 是否依赖图片/多模态 |
| `context_used` | string[] | 使用了哪些上下文 |
| `external_sources` | string[] | 联网查询或外部资料来源 URL / 可追溯来源；未使用外部资料时为空数组 |
| `rationale` | string | 外部 voter 支持、反对或跳过的理由 |

## 6. decision

允许值：

```text
support
oppose
skip
```

语义：

1. `support` 计分 `+1 × model_weight × confidence`。
2. `oppose` 计分 `-1 × model_weight × confidence`。
3. `skip` 表示模型无投票权或无法判断，不计分，但必须记录在 issue 中。

## 7. 无问题输出示例

```json
{
  "version": 1,
  "task_id": "ru000001",
  "unit_id": "ru000001",
  "task_hash": "sha256...",
  "model_id": "host-current",
  "model_role": "main",
  "findings": []
}
```

## 8. 跳过输出示例

```json
{
  "version": 1,
  "task_id": "ru000001",
  "unit_id": "ru000001",
  "task_hash": "sha256...",
  "model_id": "deepseek-v4-pro",
  "model_role": "voter",
  "votes": [
    {
      "finding_id": "ru000001-f001",
      "decision": "skip",
      "confidence": 1.0,
      "rationale": "该 finding 依赖图片，但当前模型不支持多模态。",
      "evidence": [],
      "external_sources": []
    }
  ]
}
```

## 9. 聚合规则

每个 finding 单独聚合：

```text
score(finding) = Σ(support: +1 × model_weight × confidence) + Σ(oppose: -1 × model_weight × confidence)
```

如果有投票权模型中 `failed + missing` 的比例高于 `voting.max_missing_vote_ratio`，该 finding 进入 `PendingVote` 并输出 warning。

完整性通过后，`score >= voting.issue_score_threshold` 进入 `Open`；低于阈值进入 `Rejected`。低分候选 bug 不进入 `Unknown`。
