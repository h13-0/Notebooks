#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$ROOT/tools/ai-review/ai_review_cli.py"
cmd="${1:-review}"
shift || true

case "$cmd" in
  review)
    python "$CLI" review "$@"
    ;;
  apply)
    python "$CLI" review --changed --apply "$@"
    ;;
  all)
    python "$CLI" review --all --dry-run "$@"
    ;;
  resume)
    python "$CLI" review --resume "$@"
    ;;
  *)
    python "$CLI" "$cmd" "$@"
    ;;
esac
