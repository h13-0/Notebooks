param(
  [string]$Command = "review",
  [Parameter(ValueFromRemainingArguments=$true)]
  [string[]]$Rest
)

switch ($Command) {
  "review" { ai-review review @Rest }
  "apply"  { ai-review review --changed --apply @Rest }
  "all"    { ai-review review --all --dry-run @Rest }
  "resume" { ai-review review --resume @Rest }
  default   { ai-review $Command @Rest }
}
