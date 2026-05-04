$ErrorActionPreference = "Stop"

$cmd = Get-Command ai-review -ErrorAction SilentlyContinue
if (-not $cmd) {
    Write-Error "错误：未找到 ai-review CLI。请先安装或实现 CLI 后再运行。"
    exit 127
}

& ai-review @args
exit $LASTEXITCODE
