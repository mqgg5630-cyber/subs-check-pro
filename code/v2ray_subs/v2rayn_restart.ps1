# code/v2ray_subs/v2rayn_restart.ps1
# Controlled v2rayN restart used only after explicit user approval.
# It backs up the database, preserves the active profile identifier, checks the
# current-user proxy state, then starts the same v2rayN executable again.
# ASCII-only for Windows PowerShell 5.1.
param(
    [Parameter(Mandatory = $true)][string]$Exe,
    [Parameter(Mandatory = $true)][string]$Db,
    [Parameter(Mandatory = $true)][string]$Gui,
    [Parameter(Mandatory = $true)][string]$BackupDir,
    [int]$WaitSec = 35
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$res = [ordered]@{
    ok = $false
    stage = 'start'
    backup = ''
    stopped = $false
    started = $false
    process_count = 0
    active_index_known = $false
    active_index_same = $true
    proxy_unchanged = $true
    proxy_restored = $false
    error = ''
}

function Emit([int]$code) {
    $res | ConvertTo-Json -Compress -Depth 6
    exit $code
}

function Get-ConfigState([string]$path) {
    $o = @{ known = $false; index = '' }
    if (-not (Test-Path -LiteralPath $path)) { return $o }
    try {
        $j = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($j.PSObject.Properties.Name -contains 'IndexId') {
            $o.known = $true
            $o.index = [string]$j.IndexId
        }
    } catch { }
    return $o
}

function Get-ProxySnapshot {
    $path = 'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
    $names = @('ProxyEnable', 'ProxyServer', 'ProxyOverride', 'AutoConfigURL', 'AutoDetect', 'MigrateProxy', 'EnableNegotiate')
    $key = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($path, $false)
    $out = New-Object System.Collections.ArrayList
    foreach ($n in $names) {
        $exists = $false
        $value = $null
        $kind = $null
        if ($null -ne $key) {
            try {
                $value = $key.GetValue($n, $null, [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
                $exists = ($null -ne $value)
                if ($exists) { $kind = $key.GetValueKind($n) }
            } catch { }
        }
        [void]$out.Add([pscustomobject]@{ name = $n; exists = $exists; value = $value; kind = $kind })
    }
    if ($null -ne $key) { $key.Close() }
    return @($out.ToArray())
}

function Value-Key([object]$v) {
    if ($null -eq $v) { return '<null>' }
    if ($v -is [byte[]]) { return [Convert]::ToBase64String($v) }
    return [string]$v
}

function Same-ProxySnapshot([object[]]$a, [object[]]$b) {
    if ($a.Count -ne $b.Count) { return $false }
    for ($i = 0; $i -lt $a.Count; $i++) {
        if ([string]$a[$i].name -ne [string]$b[$i].name) { return $false }
        if ([bool]$a[$i].exists -ne [bool]$b[$i].exists) { return $false }
        if ((Value-Key $a[$i].value) -ne (Value-Key $b[$i].value)) { return $false }
    }
    return $true
}

function Restore-ProxySnapshot([object[]]$snap) {
    $path = 'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
    $key = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($path, $true)
    if ($null -eq $key) { throw 'proxy_registry_not_writable' }
    try {
        foreach ($e in $snap) {
            if ([bool]$e.exists) {
                $key.SetValue([string]$e.name, $e.value, $e.kind)
            } else {
                $key.DeleteValue([string]$e.name, $false)
            }
        }
    } finally {
        $key.Close()
    }
}

try {
    if (-not (Test-Path -LiteralPath $Exe)) { throw 'exe_not_found' }
    if (-not (Test-Path -LiteralPath $Db)) { throw 'database_not_found' }
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

    $beforeConfig = Get-ConfigState $Gui
    $res.active_index_known = [bool]$beforeConfig.known
    $beforeProxy = Get-ProxySnapshot

    $backup = Join-Path $BackupDir ('guiNDB.before-ui-restart-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.db')
    Copy-Item -LiteralPath $Db -Destination $backup -Force
    foreach ($suffix in @('-wal', '-shm')) {
        $side = $Db + $suffix
        if (Test-Path -LiteralPath $side) { Copy-Item -LiteralPath $side -Destination ($backup + $suffix) -Force }
    }
    $res.backup = Split-Path -Leaf $backup

    $procs = @(Get-Process -Name 'v2rayN' -ErrorAction SilentlyContinue)
    $res.process_count = $procs.Count
    if ($procs.Count -ne 1) { throw 'v2rayn_process_count_not_one_before_restart' }
    $res.stage = 'stop'
    Stop-Process -Id $procs[0].Id -Force -ErrorAction Stop
    $until = (Get-Date).AddSeconds(12)
    do {
        Start-Sleep -Milliseconds 250
        $procs = @(Get-Process -Name 'v2rayN' -ErrorAction SilentlyContinue)
    } while ($procs.Count -gt 0 -and (Get-Date) -lt $until)
    if ($procs.Count -gt 0) { throw 'v2rayn_did_not_stop' }
    $res.stopped = $true

    $res.stage = 'start'
    Start-Process -FilePath $Exe -WorkingDirectory (Split-Path -Parent $Exe) | Out-Null
    $until = (Get-Date).AddSeconds([Math]::Max(8, $WaitSec))
    do {
        Start-Sleep -Milliseconds 500
        $procs = @(Get-Process -Name 'v2rayN' -ErrorAction SilentlyContinue)
    } while ($procs.Count -ne 1 -and (Get-Date) -lt $until)
    $res.process_count = $procs.Count
    if ($procs.Count -ne 1) { throw 'v2rayn_did_not_restart_as_one_process' }
    $res.started = $true
    Start-Sleep -Seconds 4

    $afterConfig = Get-ConfigState $Gui
    if ($beforeConfig.known -and $afterConfig.known -and $beforeConfig.index -ne $afterConfig.index) {
        $res.active_index_same = $false
        throw 'active_profile_changed_during_restart'
    }

    $afterProxy = Get-ProxySnapshot
    if (-not (Same-ProxySnapshot $beforeProxy $afterProxy)) {
        Restore-ProxySnapshot $beforeProxy
        $res.proxy_restored = $true
        Start-Sleep -Milliseconds 500
        $afterProxy = Get-ProxySnapshot
    }
    $res.proxy_unchanged = Same-ProxySnapshot $beforeProxy $afterProxy
    if (-not $res.proxy_unchanged) { throw 'system_proxy_state_changed_during_restart' }

    $res.stage = 'restarted'
    $res.ok = $true
    Emit 0
} catch {
    $res.error = [string]$_.Exception.Message
    if ($res.stage -eq 'start') { $res.stage = 'failed' }
    Emit 2
}
