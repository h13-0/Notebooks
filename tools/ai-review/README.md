# ai-review CLI

本目录包含可运行的 AI Review CLI 实现：

```text
tools/ai-review/ai_review_cli.py
```

## 维护约束

AI Review 的工具实现必须与设计文档和 skill 说明同步演进。修改 `tools/ai-review/`、`ai-review.cmd` 或 `scripts/ai-review.*` 的行为时，应同时检查并更新 `AI-Review/` 下的设计/协议文档以及 `skills/ai-review/SKILL.md` 和实际加载的 skill 副本；如果其中某一层无需变更，应在交付说明中说明原因。

## 配置解析

CLI 优先使用 PyYAML 读取 `.ai-review.yaml`。如果运行环境没有 PyYAML，会退回到内置简易 YAML 解析器；该解析器覆盖当前仓库配置使用的 YAML 子集，包括嵌套映射、标量列表和列表中的映射项。

仓库根目录提供 Windows 和 Linux/macOS 入口：

```powershell
.\ai-review.cmd identity --changed --dry-run
.\ai-review.cmd identity --changed --apply
.\ai-review.cmd prepare --changed --dry-run
.\ai-review.cmd prepare --changed --apply
.\ai-review.cmd vote
.\ai-review.cmd merge --dry-run
.\ai-review.cmd merge --apply
.\ai-review.cmd dashboard
.\ai-review.cmd check
```

```bash
./ai-review.sh identity --changed --dry-run
./ai-review.sh identity --changed --apply
./ai-review.sh prepare --changed --dry-run
./ai-review.sh prepare --changed --apply
./ai-review.sh vote
./ai-review.sh merge --dry-run
./ai-review.sh merge --apply
./ai-review.sh dashboard
./ai-review.sh check
```

也可以使用包装脚本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\ai-review.ps1 prepare --all --limit 20 --dry-run
```

```bash
scripts/ai-review.sh prepare --all --limit 20 --dry-run
```

## host-current

普通终端进程无法直接读取 Codex/Cursor 当前会话模型。`host-current` 只能由 `/ai-review vote` skill 写入：

```text
AI-Review/.state/votes/host-current/{task_id}.json
```

CLI 不再接受单文件注入的 `host-current` 投票，也不再提供 `prepare-host` / `merge-host` 桥接入口。

## Task / Vote / Merge 流程

四阶段流程把主模型和外部 voter 解耦为可恢复文件队列。完整 `/ai-review prepare` 必须由 Codex/Cursor skill 进行 AI-assisted 准备；CLI `prepare` 提供确定性的 task 队列生成、identity 校验和上下文候选写入。

在 prepare 之前，应先用 CLI 做身份锚定：

```powershell
.\ai-review.cmd identity --changed --dry-run
.\ai-review.cmd identity --changed --apply
```

`identity` 只给非空 ReviewUnit 写入缺失的 AI-Review identity 块；已有块原样保留，空段落跳过。

```powershell
.\ai-review.cmd prepare --changed --dry-run
.\ai-review.cmd prepare --changed --apply
.\ai-review.cmd vote
.\ai-review.cmd merge --dry-run
```

正式 `/ai-review prepare` 写入：

```text
AI-Review/.state/tasks/{task_id}.json
AI-Review/.state/tasks-index.json
```

在正式 `/ai-review prepare` 中，Codex/Cursor 当前会话模型必须读取候选段落，自动解析 Obsidian 引用，必要时联网补充权威来源，并把外部资料的正文或关键摘录写入 `.state/tasks` 的 `external_sources`。CLI `prepare` 的输出可作为候选 task，但不能替代当前会话模型的最终判断。

`.\ai-review.cmd vote` 只负责外部模型投票，不代表 Codex/Cursor 当前会话模型。当前会话模型的 `/ai-review vote` 必须由 skill 自己写入 `votes/host-current`，其中包含 `findings[]`；不得通过本 CLI 调外部模型。

外部 `vote` 从 task 文件和 host-current findings 并行发起外部 review。外部模型只对已有 finding 投 `support/oppose/skip`，成功结果写入：

```text
AI-Review/.state/votes/{model_id}/{task_id}.json
```

已有外部 vote 文件且 `task_hash` 一致时会自动跳过，因此 Ctrl+C 中断后可直接重新运行 `.\ai-review.cmd vote` 恢复。Codex/Cursor 当前会话模型参与投票时，也写入同一目录，例如：

```text
AI-Review/.state/votes/host-current/{task_id}.json
```

`merge` 只读取 task 和 vote 文件，逐 finding 聚合所有成功投票；没有成功运行的模型按缺失投票比例处理，不会生成 `Unknown` 票。写入结果时使用：

```powershell
.\ai-review.cmd merge --apply
```

## 外部 voter

外部模型从 `.ai-review.yaml` 读取模型列表，从 `.ai-review-secrets.yaml` 读取 provider 的 `base_url` 和 `api_key`。请求使用 OpenAI-compatible `/chat/completions` 形态，模型必须返回协议 JSON。外部 voter prompt 会携带 task 中的 `external_sources` 正文或摘录，不能依赖 API 服务商内置联网搜索。

## 写入约束

`--dry-run` 不写入仓库文件。`--apply` 执行 Git 前置检查、人工备注区校验、issue 生成、原文 AI-Review 折叠块更新、ledger 更新、Dashboard 更新和原子替换。

JSON 状态文件写入前会检查疑似编码损坏内容。若检测到连续问号 `????` 或 Unicode replacement character `�`，CLI 会拒绝写入；这通常说明生成脚本或终端管道把中文替换成了问号。

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

如只想验证扫描、ReviewUnit 切分和 task 生成链路：

```powershell
.\ai-review.cmd identity --all --limit 20 --dry-run
.\ai-review.cmd prepare --all --limit 20 --dry-run
.\ai-review.cmd merge --dry-run
```
