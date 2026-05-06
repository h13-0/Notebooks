#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$ROOT/tools/ai-review/ai_review_cli.py"
cmd="${1:-check}"
shift || true

case "$cmd" in
  apply)
    python "$CLI" merge --apply "$@"
    ;;
  all)
    python "$CLI" prepare --all --dry-run "$@"
    ;;
  *)
    python "$CLI" "$cmd" "$@"
    ;;
esac
