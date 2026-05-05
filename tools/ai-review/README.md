# ai-review CLI

本目录包含可运行的 AI Review CLI 实现：

```text
tools/ai-review/ai_review_cli.py
```

仓库根目录提供 Windows 入口：

```powershell
.\ai-review.cmd review --changed --dry-run
.\ai-review.cmd review --all --limit 20 --dry-run
.\ai-review.cmd review --changed --apply
.\ai-review.cmd review --resume
.\ai-review.cmd dashboard
.\ai-review.cmd check
```

也可以使用包装脚本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\ai-review.ps1 review --all --limit 20 --dry-run
```

```bash
scripts/ai-review.sh review --all --limit 20 --dry-run
```

## host-current

普通终端进程无法直接读取 Codex/Cursor 当前会话模型。需要主模型投票时，可通过下列方式注入符合 `AI-Review/MODEL_PROTOCOL.md` 的 JSON：

```powershell
$env:AI_REVIEW_HOST_CURRENT_VOTES_JSON = Get-Content -Raw host-votes.json
.\ai-review.cmd review --changed --dry-run
```

或：

```powershell
.\ai-review.cmd review --changed --dry-run --host-current-vote-file host-votes.json
```

如果未注入 `host-current` 投票，CLI 会继续调用配置的 voter 模型；如果没有任何成功投票，则跳过该 ReviewUnit，不会把失败模型降级成 `Unknown`。

## Codex/Cursor 桥接流程

Codex/Cursor 的 `/ai-review` 应使用两段式桥接：

```powershell
.\ai-review.cmd prepare-host --changed --dry-run
```

该命令生成：

```text
AI-Review/.state/host-current-prepare.json
```

宿主模型读取其中 `units`，逐个生成符合 `AI-Review/MODEL_PROTOCOL.md` 的投票，并写入：

```text
AI-Review/.state/host-current-votes.json
```

随后合并：

```powershell
.\ai-review.cmd merge-host --prepare-file AI-Review/.state/host-current-prepare.json --host-current-vote-file AI-Review/.state/host-current-votes.json --dry-run
```

写入模式把 `prepare-host` 和 `merge-host` 的 `--dry-run` 都替换为 `--apply`。

## Task / Vote / Merge 流程

推荐新流程把主模型和外部 voter 解耦为可恢复文件队列：

```powershell
.\ai-review.cmd prepare --all --limit 20 --dry-run
.\ai-review.cmd vote
.\ai-review.cmd merge --dry-run
```

`prepare` 写入：

```text
AI-Review/.state/tasks/{task_id}.json
AI-Review/.state/tasks-index.json
```

`vote` 从 task 文件并行发起外部 review，成功结果写入：

```text
AI-Review/.state/votes/{model_id}/{task_id}.json
```

已有 vote 文件且 `task_hash` 一致时会自动跳过，因此 Ctrl+C 中断后可直接重新运行 `vote` 恢复。Codex/Cursor 当前会话模型参与投票时，也写入同一目录，例如：

```text
AI-Review/.state/votes/host-current/{task_id}.json
```

`merge` 只读取 task 和 vote 文件，统一聚合所有成功投票；没有成功运行的模型不会生成 `Unknown` 票，也不会参与评分。写入结果时使用：

```powershell
.\ai-review.cmd merge --apply
```

## 外部 voter

外部模型从 `.ai-review.yaml` 读取模型列表，从 `.ai-review-secrets.yaml` 读取 provider 的 `base_url` 和 `api_key`。请求使用 OpenAI-compatible `/chat/completions` 形态，模型必须返回协议 JSON。

## 写入约束

`--dry-run` 不写入仓库文件。`--apply` 执行 Git 前置检查、人工备注区校验、issue 生成、原文 AI-Review 折叠块更新、ledger 更新、Dashboard 更新和原子替换。

## 扫描黑名单

扫描范围可在 `.ai-review.yaml` 中配置：

```yaml
scan:
  exclude_paths:
    - "AI-Review"
    - "skills"
    - ".codex"
    - ".cursor"
    - "tools/ai-review"
```

黑名单支持目录名和仓库相对路径 glob。命中后不会生成 ReviewUnit，但不影响 CLI 维护 `AI-Review/` 下的 issue、Dashboard 和 state 文件。

## Obsidian 引用上下文

当 `.ai-review.yaml` 中启用：

```yaml
context:
  include_outlink_blocks: true
```

CLI 会解析当前 ReviewUnit 中的 `[[note#Heading]]` 和 `[[note#^blockid]]`，把目标标题段落或块 ID 所在段落拼接进模型上下文。

## 流式外部 voter

`runtime.stream: true` 时，外部 voter 使用 OpenAI-compatible SSE stream。此时 `request_timeout_sec` 是 socket 空闲超时：只要模型持续输出 chunk，就不会因为总输出时间较长而被误判为无响应。
`runtime.stream_total_timeout_sec` 是单次流式响应总时长上限，用于防止模型无限输出 reasoning 或服务端迟迟不发 `[DONE]`。

`vote` 命令会在终端中实时显示多个模型的状态、进度、近似 token 速度、token 消耗和一行流式输出预览。每个 voter 可在 `.ai-review.yaml` 中配置 `concurrency`，也可用 `--concurrency` 临时覆盖每个模型的并发数。

## 结构化本地验证

如只想验证扫描、ReviewUnit 切分、聚合和渲染链路，不调用外部模型：

```powershell
.\ai-review.cmd review --all --limit 20 --dry-run --no-external
```
