#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "$ROOT/tools/ai-review/ai_review_cli.py" "$@"
