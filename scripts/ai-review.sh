#!/usr/bin/env bash
set -euo pipefail

if ! command -v ai-review >/dev/null 2>&1; then
  echo "错误：未找到 ai-review CLI。请先安装或实现 CLI 后再运行。" >&2
  exit 127
fi

exec ai-review "$@"
