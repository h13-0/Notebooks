# AI Review Skill

This skill is for reviewing an Obsidian-style Markdown notebook repository using the repository-local AI Review specification.

## Required reading before acting

Before reviewing or modifying files, read these files if they exist:

1. `AI-Review/README.md`
2. `AI-Review/DESIGN.md`
3. `AI-Review/IMPLEMENTATION.md`
4. `AI-Review/MODEL_PROTOCOL.md`
5. `AI-Review/CONFIG_REFERENCE.md`
6. `.ai-review.yaml`

If these files are missing, do not invent incompatible rules. Ask the user to add the AI-Review package first.

## Core rules

1. Do not directly modify original note content.
2. Only modify AI Review managed blocks, issue files, Dashboard, and state files.
3. ReviewUnit is split by Markdown headings level 1-6.
4. Empty heading sections are skipped and must not get an AI Review block.
5. Every reviewed non-empty ReviewUnit must get an AI Review folded block.
6. The folded block must show the current ReviewUnit ID.
7. The folded block must not show topic keywords.
8. Issue files must reference the source ReviewUnit block ID, for example `[[note.md#^ru000001]]`.
9. Correct units do not get issue files.
10. Issue IDs use `ar0001` style hexadecimal IDs and are never reused.
11. Issues are never merged or shared across ReviewUnits.
12. Model API keys and base URLs belong in `.ai-review-secrets.yaml`, never in tracked files.
13. If the CLI exists, prefer the CLI over manual edits.
14. If the CLI is missing or unsafe to run, provide dry-run style recommendations instead of writing files.

## Preferred CLI flow

```bash
ai-review check
ai-review review --changed --dry-run
ai-review review --changed --apply
ai-review review --resume
ai-review dashboard
```

Default review scope should be changed files only. Full-repository review must be explicit with `--all`.

## Git safety

Before applying writes, the main repository and any target submodule must be clean and synced with upstream. Dirty, uninitialized, unsynced, or HEAD-mismatched submodules must be skipped with a warning.

## Managed block format

Issue example:

```markdown
<!-- ai-review:start unit=ru000001 -->
> [!bug]- AI Review `ru000001`
> - [ ] [[AI-Review/Open/ar0001-Major-Loader与MaskROM概念混用|ar0001]]
> `2026-05-04` · GPT-5.5/DeepSeek
<!-- ai-review:end -->
^ru000001
```

Correct example:

```markdown
<!-- ai-review:start unit=ru000002 -->
> [!success]- AI Review `ru000002`
> - [[AI-Review/Dashboard|Dashboard]]
> `2026-05-04` · GPT-5.5/DeepSeek
<!-- ai-review:end -->
^ru000002
```

Topic keywords must appear in issue files and Dashboard aggregation only, never in the source note folded block.
