#!/usr/bin/env bash
set -euo pipefail

cmd="${1:-review}"
shift || true

case "$cmd" in
  review)
    ai-review review "${@:-}"
    ;;
  apply)
    ai-review review --changed --apply "$@"
    ;;
  all)
    ai-review review --all --dry-run "$@"
    ;;
  resume)
    ai-review review --resume "$@"
    ;;
  *)
    ai-review "$cmd" "$@"
    ;;
esac
