# AI Review Config Reference

#AI-Review

## 1. 配置文件

主配置：

```text
.ai-review.yaml
```

敏感配置：

```text
.ai-review-secrets.yaml
```

敏感配置模板：

```text
.ai-review-secrets.template.yaml
```

`.ai-review-secrets.yaml` 必须加入 `.gitignore`。

## 2. `.ai-review.yaml` 示例

```yaml
version: 1

review_dir: "AI-Review"

language:
  primary: "zh-Hans"
  require_simplified_chinese: true
  allow_foreign_terms: true

default_mode:
  scope: "changed"
  dry_run: true

unit:
  split_by_headings: true
  heading_levels: [1, 2, 3, 4, 5, 6]
  skip_empty_heading: true

normalize:
  ignore_ai_review_blocks: true
  trim_blank_lines: true
  collapse_blank_lines: true
  strip_trailing_spaces: true

scan:
  exclude_paths:
    - "AI-Review"
    - "skills"
    - ".codex"
    - ".cursor"
    - "tools/ai-review"
    - "Readme.md"

severity:
  callout:
    Enhance: tip
    Minor: attention
    Major: bug
    Critical: danger
    Unknown: question

voting:
  main_model_vote_enabled: true
  main_model_vote_visible: true
  host_current_allowed: true
  issue_score_threshold: 3.0
  max_missing_vote_ratio: 0.5

  severity_thresholds:
    Enhance:
      min_normalized_score: 0.35
    Minor:
      min_normalized_score: 0.45
    Major:
      min_normalized_score: 0.40
    Critical:
      min_normalized_score: 0.35

models:
  main:
    mode: "host-current"   # host-current / configured / none
    id: "host-current"
    display_name: "当前 Codex/Cursor 主模型"
    role: "main"
    vote_enabled: true
    weight: 5

  configured_main:
    id: "gpt-main"
    display_name: "Configured Main Model"
    provider: "openai-compatible"
    model: "gpt-x"
    multimodal: true
    role: "main"
    vote_enabled: true
    weight: 5

  voters:
    - id: "deepseek-v4-pro"
      display_name: "DeepSeek-V4-Pro"
      provider: "deepseek"
      model: "deepseek-v4-pro"
      multimodal: false
      weight: 1
      role: "voter"
      vote_enabled: true
      concurrency: 1
      thinking:
        enabled: true
        effort: "high"
      generation:
        max_tokens: 8192
        temperature: 0.1

context:
  include_outlinks: true
  include_backlinks: true
  include_outlink_blocks: true
  max_outlinks: 8
  max_outlink_chars: 2500
  max_backlinks: 5
  max_context_tokens: 6000

attachments:
  svg:
    convert_to_png: true
    cache: "temp"

  archive:
    enabled: true
    formats: [".zip"]
    max_size_mb: 5
    max_files: 50

git:
  require_clean_worktree: true
  require_synced_with_upstream: true
  fetch_before_check: true

submodules:
  scan: true
  write_annotations: true
  require_clean_worktree: true
  require_synced_with_upstream: true
  skip_uninitialized: true
  skip_if_head_mismatch: true

dashboard:
  top_n_per_section: 10
  topic_keywords_per_unit: 5

runtime:
  max_concurrency: 3
  request_timeout_sec: 300
  stream: true
  stream_total_timeout_sec: 1800
  retry: 1
  warn_once_per_model: true
  model_failure_policy: "skip_model"
  no_eligible_model_policy: "skip"

write:
  preserve_user_notes: true
  compact_callout: true
  auto_commit: false
  backup: false
```

## 3. `.ai-review-secrets.template.yaml` 示例

```yaml
providers:
  openai-compatible:
    base_url: "https://your-api-endpoint/v1"
    api_key: "YOUR_API_KEY"

  deepseek:
    base_url: "https://api.deepseek.com"
    api_key: "YOUR_API_KEY"
```

## 4. `.gitignore` 示例

```gitignore
.ai-review-secrets.yaml
AI-Review/.tmp/
AI-Review/.cache/
```

## 5. host-current 与 configured 的区别

`host-current` 不需要 API key，因为它使用当前 Codex/Cursor 会话模型。

`configured` 需要在 `.ai-review.yaml` 和 `.ai-review-secrets.yaml` 中配置 provider、model、base_url、api_key。

普通终端 CLI 无法直接访问 `host-current`。需要当前 Codex/Cursor 会话模型参与时，应使用 `prepare / vote / merge` 工作流，并由当前会话模型把投票写入 `AI-Review/.state/votes/host-current/{task_id}.json`。

在 `prepare` 前应运行 `identity` 写入稳定段落 ID。`identity --dry-run` 只预览，`identity --apply` 写入缺失的 AI-Review identity 块；空段落会跳过，已有块会保留。

## 6. Task / Vote / Merge 相关配置

外部 voter 可配置单模型并发：

```yaml
models:
  voters:
    - id: "deepseek-v4-pro"
      concurrency: 2
```

`runtime.request_timeout_sec` 是单次 HTTP socket 空闲超时。启用 `runtime.stream: true` 后，只要服务端持续输出 SSE chunk，就不会因为总耗时较长而被判定为无响应。

`runtime.stream_total_timeout_sec` 是单个流式 review 的总时长上限，用于防止无限输出。复杂 review 建议设置为 1800 秒或更高。

`ai-review vote --concurrency N` 会临时覆盖每个模型的 `concurrency`。

完整 `/ai-review prepare` 必须由 Codex/Cursor skill 做 AI-assisted 准备。CLI `prepare` 只提供确定性 task 队列和候选上下文支撑。prepare 阶段如联网查询资料，task 的 `external_sources` 必须写入 URL/标题/用途和正文或关键摘录，供无联网能力的外部 voter API 直接使用。

`/ai-review vote` 只写当前会话模型的 `host-current` 投票；外部模型并发、超时和流式参数只适用于普通终端中的 `.\ai-review.cmd vote`。

`prepare` 和 `vote` 默认应按 `unit_id + content_hash` 增量跳过已处理结果；重新生成单段或全量结果必须显式指定 `--regenerate`。

`voting.issue_score_threshold` 是单个 finding 进入 `Open` 的最低总分。完整性通过但低于该阈值的 finding 进入 `Rejected`。

`voting.max_missing_vote_ratio` 是有投票权模型中失败或缺失投票的最大比例。超过该比例的 finding 进入 `PendingVote`，不进入 `Open` 或 `Rejected`。

JSON 状态写入会拒绝疑似编码损坏内容，包括连续问号 `????` 和 Unicode replacement character `�`。如果触发该错误，应检查生成 task/vote 的终端编码或脚本输入方式。
