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

如果未注入 `host-current` 投票，CLI 会继续调用配置的 voter 模型；如果没有任何可用模型，则按配置降级为 `Unknown`。

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

## 外部 voter

外部模型从 `.ai-review.yaml` 读取模型列表，从 `.ai-review-secrets.yaml` 读取 provider 的 `base_url` 和 `api_key`。请求使用 OpenAI-compatible `/chat/completions` 形态，模型必须返回协议 JSON。

## 写入约束

`--dry-run` 不写入仓库文件。`--apply` 执行 Git 前置检查、人工备注区校验、issue 生成、原文 AI-Review 折叠块更新、ledger 更新、Dashboard 更新和原子替换。

## 结构化本地验证

如只想验证扫描、ReviewUnit 切分、聚合和渲染链路，不调用外部模型：

```powershell
.\ai-review.cmd review --all --limit 20 --dry-run --no-external
```
