# code/v2ray_subs/local_run.ps1
# ---------------------------------------------------------------------------
# Windows side of the subs-check-pro -> desktop -> v2rayN pipeline.
# watch.ps1 runs this file as the repo check_cmd whenever the sandbox requests a
# check. The mode is read from results/v2ray_subs/mode.txt, so the sandbox can
# switch it by committing one line:
#   probe : read-only environment report (no node data, user name redacted)
#   run   : subs-check-pro -> desktop folder -> v2rayN subscription group
# Exit 0 = passed, anything else = failed.
# Keep this file ASCII-only: Windows PowerShell 5.1 decodes .ps1 as ANSI.
# ---------------------------------------------------------------------------
param([string]$Mode = '')

$ErrorActionPreference = 'Continue'
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
Set-Location -LiteralPath $repo

$outRel = 'results/v2ray_subs'
$outDir = Join-Path $repo 'results\v2ray_subs'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$script:exitCode = 0

if (-not $Mode) {
    $modeFile = Join-Path $outDir 'mode.txt'
    if (Test-Path -LiteralPath $modeFile) {
        $Mode = ((Get-Content -LiteralPath $modeFile -Raw) -replace '\s', '').ToLower()
    }
}
if (-not $Mode) { $Mode = 'probe' }

$script:report = New-Object System.Collections.ArrayList

# Write a line to stdout (captured into the check log) and keep it for the report file.
function Say([string]$text) {
    $t = [string]$text
    if ($env:USERNAME) { $t = $t.Replace($env:USERNAME, '<user>') }
    [void]$script:report.Add($t)
    Write-Output $t
}

function Save-Report([string]$name) {
    $path = Join-Path $outDir $name
    $body = ($script:report -join "`r`n") + "`r`n"
    [System.IO.File]::WriteAllText($path, $body, (New-Object System.Text.UTF8Encoding($false)))
    return $path
}

function Test-PortFree([int]$port) {
    try {
        $l = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $port)
        $l.Start()
        $l.Stop()
        return $true
    } catch {
        return $false
    }
}

function Test-Url([string]$u) {
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    } catch { }
    try {
        $r = Invoke-WebRequest -Uri $u -Method Head -UseBasicParsing -TimeoutSec 25
        return ('HTTP ' + [int]$r.StatusCode)
    } catch {
        return ('FAIL ' + $_.Exception.Message)
    }
}

function Invoke-Probe {
    Say ('== v2ray_subs probe ' + $stamp)
    Say ('powershell        : ' + $PSVersionTable.PSVersion.ToString())
    Say ('os                : ' + [Environment]::OSVersion.VersionString)
    $desk = [Environment]::GetFolderPath('Desktop')
    Say ('desktop exists    : ' + (Test-Path -LiteralPath $desk))

    foreach ($exe in @('git', 'py', 'python', 'python3')) {
        $cmd = Get-Command $exe -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $cmd) { Say ('tool ' + $exe + ' : not found'); continue }
        $v = ''
        try { $v = (& $exe --version 2>&1 | Out-String).Trim() } catch { $v = 'error' }
        Say ('tool ' + $exe + ' : ' + $v)
    }

    $names = @('v2rayN', 'xray', 'v2ray', 'subs-check-pro', 'sing-box', 'mihomo', 'clash-verge', 'nekoray', 'nekobox')
    $procs = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $names -contains $_.ProcessName })
    Say ('proxy-related processes: ' + $procs.Count)
    foreach ($p in $procs) {
        $pp = ''
        try { $pp = $p.Path } catch { $pp = '(no access)' }
        Say ('  ' + $p.ProcessName + ' pid=' + $p.Id + ' path=' + $pp)
    }

    # locate v2rayN: known install roots, one level deep
    $roots = @($env:LOCALAPPDATA, (Join-Path $env:LOCALAPPDATA 'Programs'), $env:ProgramFiles, 'D:\', 'E:\', 'F:\')
    $dirs = New-Object System.Collections.ArrayList
    foreach ($root in $roots) {
        if (-not $root -or -not (Test-Path -LiteralPath $root)) { continue }
        Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -like 'v2rayN*' } |
            ForEach-Object { [void]$dirs.Add($_.FullName) }
    }
    $appDataDir = Join-Path $env:APPDATA 'v2rayN'
    if (Test-Path -LiteralPath $appDataDir) { [void]$dirs.Add($appDataDir) }
    $dirs = @($dirs | Select-Object -Unique)
    Say ('v2rayN candidate dirs: ' + $dirs.Count)
    foreach ($d in $dirs) {
        Say ('v2rayN dir: ' + $d)
        $exeFile = Get-ChildItem -LiteralPath $d -Filter 'v2rayN.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($exeFile) {
            Say ('  exe: ' + $exeFile.FullName + ' version=' + $exeFile.VersionInfo.FileVersion)
        }
        Get-ChildItem -LiteralPath $d -File -Recurse -ErrorAction SilentlyContinue | Select-Object -First 80 | ForEach-Object {
            $rel = $_.FullName.Substring($d.Length).TrimStart('\')
            Say ('  file ' + $rel + ' size=' + $_.Length + ' mtime=' + $_.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))
        }
    }

    foreach ($port in @(8199, 8299, 18199, 18299, 10808, 10809, 7890)) {
        Say ('port ' + $port + ' free : ' + (Test-PortFree $port))
    }

    Say ('net api.github.com         : ' + (Test-Url 'https://api.github.com/zen'))
    Say ('net github release asset   : ' + (Test-Url 'https://github.com/sinspired/subs-check-pro/releases/download/v3.5.0/subs-check-pro_3.5.0_checksums.txt'))
    Say ('net raw.githubusercontent  : ' + (Test-Url 'https://raw.githubusercontent.com/sinspired/airport/main/subs/merged/col.txt'))

    $tasks = @(Get-ScheduledTask -TaskName 'git-sync-watch-*' -ErrorAction SilentlyContinue)
    Say ('git-sync watcher tasks: ' + $tasks.Count)
    foreach ($t in $tasks) { Say ('  ' + $t.TaskName + ' state=' + $t.State) }

    $path = Save-Report ('probe_' + $stamp + '.txt')
    Say ('report written: ' + $outRel + '/' + (Split-Path -Leaf $path))
    $script:exitCode = 0
}

switch ($Mode) {
    'probe' { Invoke-Probe }
    default {
        Say ('mode not supported yet: ' + $Mode)
        $script:exitCode = 1
    }
}
exit $script:exitCode
