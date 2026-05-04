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
      thinking:
        enabled: true
        effort: "high"
      generation:
        max_tokens: 8192
        temperature: 0.1

context:
  include_outlinks: true
  include_backlinks: true
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
  request_timeout_sec: 120
  retry: 2
  warn_once_per_model: true
  model_failure_policy: "skip_model"
  no_eligible_model_policy: "unknown"

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

如果在普通终端执行 CLI 且主模型配置为 `host-current`，CLI 应拒绝执行写入，并提示用户切换到 `configured` 或从 Codex/Cursor 的 `/ai-review` 入口运行。
