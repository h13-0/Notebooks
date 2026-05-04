param(
  [string]$Command = "review",
  [Parameter(ValueFromRemainingArguments=$true)]
  [string[]]$Rest
)

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Cli = Join-Path $Root "tools\ai-review\ai_review_cli.py"

switch ($Command) {
  "review" { python $Cli review @Rest }
  "apply"  { python $Cli review --changed --apply @Rest }
  "all"    { python $Cli review --all --dry-run @Rest }
  "resume" { python $Cli review --resume @Rest }
  default   { python $Cli $Command @Rest }
}
