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
    - "AGENTS.ai-review.md"
    - "AI-Review-SLASH_COMMANDS.md"
    - "README.ai-review-skill.md"

severity:
  callout:
    Correct: success
    Enhance: tip
    Minor: attention
    Major: bug
    Critical: danger
    Unknown: question

voting:
  main_model_vote_enabled: true
  main_model_vote_visible: true
  host_current_allowed: true
  fallback_when_no_threshold_matched: "Unknown"

  severity_thresholds:
    Correct:
      min_normalized_score: 0.50
    Enhance:
      min_normalized_score: 0.35
    Minor:
      min_normalized_score: 0.45
    Major:
      min_normalized_score: 0.40
    Critical:
      min_normalized_score: 0.35
    Unknown:
      min_normalized_score: 0.30

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

完整 `/ai-review prepare` 必须由 Codex/Cursor skill 做 AI-assisted 准备。普通 CLI 不提供 `prepare` 子命令，因为它无法主动与当前会话模型通信。
