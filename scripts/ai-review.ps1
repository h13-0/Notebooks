param(
  [string]$Command = "check",
  [Parameter(ValueFromRemainingArguments=$true)]
  [string[]]$Rest
)

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Cli = Join-Path $Root "tools\ai-review\ai_review_cli.py"

switch ($Command) {
  "apply"  { python $Cli merge --apply @Rest }
  "all"    { python $Cli prepare --all --dry-run @Rest }
  default   { python $Cli $Command @Rest }
}
