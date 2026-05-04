# AI Review Agent Instructions

This repository uses an AI Review workflow for Obsidian-style Markdown notes.

Before making any AI Review change, read:

- `AI-Review/README.md`
- `AI-Review/DESIGN.md`
- `AI-Review/IMPLEMENTATION.md`
- `AI-Review/MODEL_PROTOCOL.md`
- `AI-Review/CONFIG_REFERENCE.md`
- `.ai-review.yaml`

Use the CLI when available:

```bash
ai-review check
ai-review review --changed --dry-run
ai-review review --changed --apply
ai-review review --resume
ai-review dashboard
```

Do not bypass the design rules. In particular:

- Do not directly modify note body text.
- Do not display topic keywords in source note AI Review folded blocks.
- Do include the ReviewUnit block ID in source note folded blocks.
- Do make issue files reference `[[source.md#^ru000001]]`.
- Do keep API keys and base URLs out of tracked files.
