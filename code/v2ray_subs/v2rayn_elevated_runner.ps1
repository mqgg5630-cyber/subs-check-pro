# code/v2ray_subs/v2rayn_elevated_runner.ps1
# Runs the approved v2rayN restart + native GUI real-ping action after a UAC
# consent prompt. This file is started by a non-elevated watcher with RunAs.
# ASCII-only for Windows PowerShell 5.1.
param(
    [Parameter(Mandatory = $true)][string]$Repo,
    [Parameter(Mandatory = $true)][string]$ResultPath
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$result = [ordered]@{ ok = $false; exit_code = 2; error = '' }
try {
    $entry = Join-Path $Repo 'code\v2ray_subs\local_run.ps1'
    if (-not (Test-Path -LiteralPath $entry)) { throw 'local_run_missing' }
    Set-Location -LiteralPath $Repo
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $entry -Mode 'uirestartrealping'
    $result.exit_code = [int]$LASTEXITCODE
    $result.ok = ($result.exit_code -eq 0)
    if (-not $result.ok) { $result.error = 'approved_action_failed' }
} catch {
    $result.error = $_.Exception.GetType().Name
}
try {
    $dir = Split-Path -Parent $ResultPath
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $enc = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($ResultPath, (($result | ConvertTo-Json -Compress) + "`n"), $enc)
} catch { }
exit ([int]$result.exit_code)
