# code/v2ray_subs/local_run.ps1
# Windows side of the subs-check-pro -> Desktop folder -> v2rayN pipeline.
# The git-sync watcher runs this file as check_cmd when the sandbox requests a
# check. Mode comes from results/v2ray_subs/mode.txt:
#   probe : read-only environment report (user name redacted)
#   run   : subs-check-pro checks the default subscription sources, the usable
#           V2Ray nodes go to a NEW Desktop folder, then ONE new subscription
#           group is added to v2rayN. v2rayN is not restarted, the active node
#           and the system proxy are not changed.
#   realtest: like run, but before the Desktop folder and the v2rayN import every
#           candidate node is tested the way v2rayN's real-ping test does (its own
#           core, its ping URL, 5 s budget; see v2rayn_realtest.py). Only the nodes
#           that answer are delivered and imported into a NEW group.
#   uirefresh: uses the running v2rayN UI to refresh its subscription group list
#           and succeeds only after the named group is visible in that list.
#   uirestartrealping: after explicit approval, restarts v2rayN once, verifies
#           the group in its UI, and invokes v2rayN's own real-ping command.
# Exit 0 = passed. Anything else = failed (the receipt says at which stage).
#   refresh: rebuilds the plain list, README and manifest of the newest Desktop
#           folder from its own base64 file. No check, no import.
#   export : copies the newest plain node list to
#           results/v2ray_subs/nodes_public_<stamp>.txt so that it goes to git.
#           Only after the user explicitly confirmed a PUBLIC push. Set mode.txt
#           back to probe afterwards.
# Node links stay in the Desktop folder unless an export was requested.
# Keep this file ASCII-only: Windows PowerShell 5.1 reads .ps1 as ANSI.
param([string]$Mode = '')

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
Set-Location -LiteralPath $repo

$outDir = Join-Path $repo 'results\v2ray_subs'
$settingsPath = Join-Path $repo 'code\v2ray_subs\settings.json'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$script:exitCode = 2
$script:report = New-Object System.Collections.ArrayList

if (-not $Mode) {
    $modeFile = Join-Path $outDir 'mode.txt'
    if (Test-Path -LiteralPath $modeFile) {
        $Mode = ((Get-Content -LiteralPath $modeFile -Raw) -replace '\s', '').ToLower()
    }
}
if (-not $Mode) { $Mode = 'probe' }

# Print one line (captured into the check log) and keep it for the report file.
function Say([string]$text) {
    $t = [string]$text
    if ($env:USERNAME) { $t = $t.Replace($env:USERNAME, '<user>') }
    [void]$script:report.Add($t)
    Write-Output $t
}

function Write-Utf8([string]$path, [string]$text, [bool]$bom = $false) {
    $enc = New-Object System.Text.UTF8Encoding($bom)
    [System.IO.File]::WriteAllText($path, $text, $enc)
}

function Read-Settings {
    return (Get-Content -LiteralPath $settingsPath -Raw -Encoding UTF8 | ConvertFrom-Json)
}

function Test-PortFree([int]$port) {
    try {
        $l = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
        $l.Start()
        $l.Stop()
        return $true
    } catch {
        return $false
    }
}

function Test-TcpOpen([string]$hostName, [int]$port) {
    $c = [System.Net.Sockets.TcpClient]::new()
    try {
        $t = $c.ConnectAsync($hostName, $port)
        $ok = $t.Wait(2000)
        return ($ok -and $c.Connected)
    } catch {
        return $false
    } finally {
        $c.Close()
    }
}

function Get-FreePorts([int]$count) {
    $found = @()
    $guard = 0
    while ($found.Count -lt $count -and $guard -lt 500) {
        $guard++
        $p = Get-Random -Minimum 20000 -Maximum 60000
        if ($found -contains $p) { continue }
        if (Test-PortFree $p) { $found += $p }
    }
    if ($found.Count -lt $count) { throw 'no free local port found' }
    return ,$found
}

function Test-Url([string]$u) {
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    } catch { }
    try {
        $resp = Invoke-WebRequest -Uri $u -Method Head -UseBasicParsing -TimeoutSec 15
        return ('HTTP ' + [int]$resp.StatusCode)
    } catch {
        return ('unreachable: ' + $_.Exception.GetType().Name)
    }
}

function Find-Python {
    $cands = @(
        @{ exe = 'py'; pre = @('-3') },
        @{ exe = 'python'; pre = @() },
        @{ exe = 'python3'; pre = @() }
    )
    foreach ($c in $cands) {
        $exeName = [string]$c.exe
        $pre = @($c.pre)
        $cmd = Get-Command $exeName -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $cmd) { continue }
        $v = ''
        try { $v = (& $exeName @pre '--version' 2>&1 | Out-String) } catch { $v = '' }
        if ($v -match 'Python 3\.') { return [pscustomobject]@{ exe = $exeName; pre = $pre } }
    }
    return $null
}

function Get-V2rayNCandidates {
    # Folder names starting with v2rayN, searched 2 levels deep in the usual places
    # (drive roots: 1 level). Returns full paths (names only are printed).
    $dirs = New-Object System.Collections.ArrayList
    $deep = @($env:LOCALAPPDATA, (Join-Path $env:LOCALAPPDATA 'Programs'), $env:ProgramFiles, (Join-Path $env:USERPROFILE 'Desktop'), (Join-Path $env:USERPROFILE 'Downloads'), (Join-Path $env:USERPROFILE 'Documents'))
    foreach ($root in $deep) {
        if (-not $root -or -not (Test-Path -LiteralPath $root)) { continue }
        $hit = @(Get-ChildItem -LiteralPath $root -Directory -Recurse -Depth 2 -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'v2rayN*' })
        foreach ($h in $hit) { [void]$dirs.Add($h.FullName) }
    }
    foreach ($root in @('D:\', 'E:\', 'F:\')) {
        if (-not (Test-Path -LiteralPath $root)) { continue }
        $hit = @(Get-ChildItem -LiteralPath $root -Directory -Recurse -Depth 1 -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'v2rayN*' })
        foreach ($h in $hit) { [void]$dirs.Add($h.FullName) }
    }
    return $dirs.ToArray()
}

function Find-V2rayN {
    $procs = @(Get-Process -Name 'v2rayN' -ErrorAction SilentlyContinue)
    $procDirs = New-Object System.Collections.ArrayList
    $unreadable = 0
    foreach ($p in $procs) {
        $pp = ''
        try { $pp = [string]$p.Path } catch { $pp = '' }
        if ($pp) { [void]$procDirs.Add((Split-Path -Parent $pp)) } else { $unreadable++ }
    }
    if ($procDirs.Count -eq 0 -and $procs.Count -gt 0) {
        try {
            $cims = @(Get-CimInstance -ClassName Win32_Process -Filter "Name = 'v2rayN.exe'" -ErrorAction Stop)
            foreach ($c in $cims) {
                if ($c.ExecutablePath) { [void]$procDirs.Add((Split-Path -Parent ([string]$c.ExecutablePath))) }
            }
        } catch { }
    }
    $cand = New-Object System.Collections.ArrayList
    foreach ($d in $procDirs) { [void]$cand.Add($d) }
    foreach ($d in @(Get-V2rayNCandidates)) { [void]$cand.Add($d) }
    $all = @($cand | Select-Object -Unique)
    $running = ($procs.Count -gt 0)
    foreach ($d in $all) {
        $db = Join-Path $d 'guiConfigs\guiNDB.db'
        if (Test-Path -LiteralPath $db) {
            return [pscustomobject]@{ dir = $d; db = $db; running = $running; hasDb = $true; procCount = $procs.Count; unreadable = $unreadable }
        }
    }
    $d0 = ''
    $db0 = ''
    if ($procDirs.Count -gt 0) {
        $d0 = [string]$procDirs[0]
        $db0 = Join-Path $d0 'guiConfigs\guiNDB.db'
    }
    return [pscustomobject]@{ dir = $d0; db = $db0; running = $running; hasDb = $false; procCount = $procs.Count; unreadable = $unreadable }
}

function Get-DownloadRoutes {
    # Route 1 is direct (uses the Windows proxy setting if one exists).
    # Routes 2+ go through the HTTP inbound of an already-running v2rayN, for
    # this download only. The active node and the system proxy are not changed.
    $list = New-Object System.Collections.ArrayList
    [void]$list.Add(@{ name = 'direct'; proxy = '' })
    foreach ($port in @(10809, 10808)) {
        if (Test-TcpOpen '127.0.0.1' $port) {
            [void]$list.Add(@{ name = ('v2rayN-local-' + $port); proxy = ('http://127.0.0.1:' + $port) })
        }
    }
    return $list.ToArray()
}

function Save-Remote([string]$uri, [string]$outFile, [string]$proxyUrl, [int]$timeoutSec) {
    if (Test-Path -LiteralPath $outFile) { Remove-Item -LiteralPath $outFile -Force }
    if ($proxyUrl) {
        Invoke-WebRequest -Uri $uri -OutFile $outFile -UseBasicParsing -TimeoutSec $timeoutSec -Proxy $proxyUrl | Out-Null
    } else {
        Invoke-WebRequest -Uri $uri -OutFile $outFile -UseBasicParsing -TimeoutSec $timeoutSec | Out-Null
    }
    if (-not (Test-Path -LiteralPath $outFile) -or (Get-Item -LiteralPath $outFile).Length -eq 0) {
        throw 'empty download'
    }
}

function Get-SubsCheckExe([object]$st, [string]$work) {
    $ver = [string]$st.subs_check_pro_version
    $bin = Join-Path $work ('bin\' + $ver)
    $have = @(Get-ChildItem -LiteralPath $bin -Recurse -Filter 'subs-check-pro*.exe' -ErrorAction SilentlyContinue)
    if ($have.Count -gt 0) {
        $script:downloadInfo['route'] = 'cached'
        return $have[0].FullName
    }
    New-Item -ItemType Directory -Force -Path $bin | Out-Null
    $dl = Join-Path $work 'download'
    New-Item -ItemType Directory -Force -Path $dl | Out-Null
    try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch { }

    $asset = [string]$st.windows_asset
    $sumsName = [string]$st.checksums_asset
    $sumsPath = Join-Path $dl $sumsName
    $zipPath = Join-Path $dl $asset
    $sumsUrl = [string]$st.release_base + $sumsName
    $zipUrl = [string]$st.release_base + $asset

    # the small checksum file picks the first route that can reach the release
    $routes = @(Get-DownloadRoutes)
    $good = $null
    foreach ($route in $routes) {
        try {
            Save-Remote $sumsUrl $sumsPath ([string]$route.proxy) 120
            $good = $route
            break
        } catch {
            $script:downloadInfo['attempts'] += ([string]$route.name + ' checksums: ' + $_.Exception.GetType().Name)
        }
    }
    if ($null -eq $good) { throw 'no download route reached the release checksums' }

    $order = New-Object System.Collections.ArrayList
    [void]$order.Add($good)
    foreach ($route in $routes) {
        if ($route.name -ne $good.name) { [void]$order.Add($route) }
    }
    $zipOk = $false
    foreach ($route in $order) {
        try {
            Save-Remote $zipUrl $zipPath ([string]$route.proxy) 900
            $script:downloadInfo['route'] = [string]$route.name
            $zipOk = $true
            break
        } catch {
            $script:downloadInfo['attempts'] += ([string]$route.name + ' binary: ' + $_.Exception.GetType().Name)
        }
    }
    if (-not $zipOk) { throw 'binary download failed on every route' }

    $want = ''
    foreach ($line in (Get-Content -LiteralPath $sumsPath)) {
        $parts = @($line.Trim() -split '\s+')
        if ($parts.Count -ge 2 -and $parts[$parts.Count - 1] -eq $asset) { $want = $parts[0].ToLower() }
    }
    if (-not $want) { throw 'checksum line for the Windows asset was not found' }
    $got = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash.ToLower()
    if ($got -ne $want) { throw ('sha256 mismatch for ' + $asset) }
    Expand-Archive -LiteralPath $zipPath -DestinationPath $bin -Force
    $exe = @(Get-ChildItem -LiteralPath $bin -Recurse -Filter 'subs-check-pro*.exe' | Select-Object -First 1)
    if ($exe.Count -eq 0) { throw 'subs-check-pro exe not found after extract' }
    return $exe[0].FullName
}

function Get-SafeTail([string]$path, [int]$n) {
    if (-not (Test-Path -LiteralPath $path)) { return @() }
    $lines = @(Get-Content -LiteralPath $path -Encoding UTF8 -Tail $n -ErrorAction SilentlyContinue)
    $out = @()
    foreach ($ln in $lines) {
        $t = ([string]$ln) -replace '\S+://\S+', '<link>'
        if ($t.Length -gt 220) { $t = $t.Substring(0, 220) }
        $out += $t
    }
    return $out
}

function Write-Receipt([System.Collections.IDictionary]$r) {
    $json = ($r | ConvertTo-Json -Depth 8)
    if ($env:USERNAME) { $json = $json.Replace($env:USERNAME, '<user>') }
    $name = 'RECEIPT_' + $stamp + '.json'
    Write-Utf8 (Join-Path $outDir $name) ($json + "`n")
    Write-Utf8 (Join-Path $outDir 'RECEIPT_LATEST.json') ($json + "`n")
    return $name
}

function Get-NodeInfo([string]$b64Path) {
    # Decode the subscription (base64 of share links) and keep every "scheme://" line.
    # http/https lines are not share links and are skipped.
    $raw = [string](Get-Content -LiteralPath $b64Path -Raw -Encoding UTF8)
    $clean = $raw -replace '\s', ''
    $plain = $raw
    try { $plain = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($clean)) } catch { $plain = $raw }
    $nodes = New-Object System.Collections.ArrayList
    foreach ($ln in ($plain -split "`r?`n")) {
        $t = $ln.Trim()
        if ($t -match '^([A-Za-z][A-Za-z0-9+.-]*)://') {
            $sch = $matches[1].ToLower()
            if ($sch -ne 'http' -and $sch -ne 'https') { [void]$nodes.Add($t) }
        }
    }
    $uniq = @($nodes | Select-Object -Unique)
    $hist = @{}
    foreach ($n in $uniq) {
        $sch2 = (($n -split '://', 2)[0]).ToLower()
        if ($hist.ContainsKey($sch2)) { $hist[$sch2] = [int]$hist[$sch2] + 1 } else { $hist[$sch2] = 1 }
    }
    return @{ nodes = $uniq; hist = $hist; plain_lines = @($plain -split "`r?`n").Count }
}

function Get-Breakdown([hashtable]$hist) {
    $pairs = @()
    foreach ($k in $hist.Keys) { $pairs += [pscustomobject]@{ k = [string]$k; v = [int]$hist[$k] } }
    $sorted = @($pairs | Sort-Object -Property @{ Expression = 'v'; Descending = $true }, @{ Expression = 'k'; Descending = $false })
    $parts = @()
    foreach ($x in $sorted) { $parts += ($x.k + ' ' + $x.v) }
    return ($parts -join ' / ')
}

function Invoke-Refresh {
    # No check and no v2rayN write here: rebuild the plain list, README and manifest
    # of the newest delivered Desktop folder from its own base64 file.
    $script:exitCode = 2
    $st = Read-Settings
    $desk = [Environment]::GetFolderPath('Desktop')
    $r = @{ mode = 'refresh'; stamp = $stamp; started = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss'); state = 'failed'; stage = 'find'; delivered = $false; imported = $false }
    try {
        $cand = @(Get-ChildItem -LiteralPath $desk -Directory -Filter ([string]$st.desktop_folder_prefix + '*') -ErrorAction SilentlyContinue | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'v2ray_subscription_base64.txt') } | Sort-Object -Property Name -Descending)
        if ($cand.Count -eq 0) { throw 'no delivered folder with a subscription file was found' }
        $folder = $cand[0].FullName
        $r['folder'] = 'Desktop\' + $cand[0].Name

        $r['stage'] = 'collect'
        $info = Get-NodeInfo (Join-Path $folder 'v2ray_subscription_base64.txt')
        $nodes = @($info['nodes'])
        if ($nodes.Count -eq 0) { throw 'no share links in the delivered subscription' }
        $breakdown = Get-Breakdown $info['hist']
        $r['node_counts'] = @{ total = $nodes.Count; by_scheme = $info['hist'] }
        Say ('refresh: ' + $nodes.Count + ' share links (' + $breakdown + ')')

        $r['stage'] = 'write'
        $old = $null
        $manPath = Join-Path $folder 'manifest.json'
        if (Test-Path -LiteralPath $manPath) { $old = Get-Content -LiteralPath $manPath -Raw -Encoding UTF8 | ConvertFrom-Json }
        $oldImp = $null
        if ($old -ne $null) { $oldImp = $old.v2rayn }
        $okImp = ($oldImp -ne $null -and [bool]$oldImp.ok)
        $importLine = 'v2rayN: see the receipt for the import result.'
        if ($okImp) {
            $importLine = 'v2rayN: added subscription group "' + [string]$oldImp.group + '" with ' + [string]$oldImp.profiles + ' node(s). The active node and the system proxy were not changed.'
        }

        $fPlain = Join-Path $folder 'v2ray_nodes_plain.txt'
        $fReadme = Join-Path $folder 'README.txt'
        $fManifest = Join-Path $folder 'manifest.json'
        Write-Utf8 $fPlain (($nodes -join "`n") + "`n")
        $tpl = [string](Get-Content -LiteralPath (Join-Path $repo 'code\v2ray_subs\desktop_readme.txt') -Raw -Encoding UTF8)
        $txt = $tpl
        $txt = $txt.Replace('{{generated_at}}', (Get-Date).ToString('yyyy-MM-dd HH:mm'))
        $txt = $txt.Replace('{{version}}', [string]$st.subs_check_pro_version)
        $txt = $txt.Replace('{{source_count}}', [string](@($st.sub_urls_remote).Count))
        $txt = $txt.Replace('{{total}}', [string]$nodes.Count)
        $txt = $txt.Replace('{{breakdown}}', $breakdown)
        $txt = $txt.Replace('{{import_line}}', $importLine)
        Write-Utf8 $fReadme $txt $true

        $files = @()
        foreach ($f in @((Join-Path $folder 'v2ray_subscription_base64.txt'), $fPlain, $fReadme)) {
            $fi = Get-Item -LiteralPath $f
            $files += @{ name = $fi.Name; bytes = $fi.Length; sha256 = (Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLower() }
        }
        $r['files'] = $files
        $man = @{
            generated = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
            refreshed_by = 'refresh mode (same subscription file, rebuilt lists)'
            subs_check_pro = [string]$st.subs_check_pro_version
            source_index_count = @($st.sub_urls_remote).Count
            node_counts = $r['node_counts']
            files = $files
            v2rayn = $oldImp
            note = 'counts and hashes only; node links are only in v2ray_nodes_plain.txt and the base64 file'
        }
        Write-Utf8 $fManifest (($man | ConvertTo-Json -Depth 6) + "`n")

        $r['delivered'] = $true
        $r['imported'] = $okImp
        if ($okImp) { $r['v2rayn_profiles'] = [int]$oldImp.profiles }
        if ($okImp) { $r['matches_v2rayn_count'] = ([int]$oldImp.profiles -eq $nodes.Count) }
        $r['state'] = $(if ($okImp) { 'ok' } else { 'delivered_not_imported' })
        $script:exitCode = $(if ($okImp) { 0 } else { 2 })
    } catch {
        $r['error'] = [string]$_.Exception.Message
        Say ('FAILED at stage ' + $r['stage'] + ': ' + $r['error'])
        $script:exitCode = 2
    }
    $r['finished'] = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $name = Write-Receipt $r
    Say ('receipt: results/v2ray_subs/' + $name + ' state=' + $r['state'])
}

# ---------------------------------------------------------------- probe mode
function Invoke-Probe {
    $script:exitCode = 0
    Say ('probe ' + $stamp)
    Say ('os: ' + [Environment]::OSVersion.VersionString + ' | ps: ' + $PSVersionTable.PSVersion)
    Say ('desktop folder exists: ' + (Test-Path -LiteralPath ([Environment]::GetFolderPath('Desktop'))))
    Say ('LOCALAPPDATA set: ' + [bool]$env:LOCALAPPDATA)

    $v = Find-V2rayN
    $vdir = '-'
    if ($v.dir) { $vdir = Split-Path -Leaf $v.dir }
    Say ('v2rayN: processes=' + $v.procCount + ' pathUnreadable=' + $v.unreadable + ' guiNDB.db=' + $v.hasDb + ' dir=' + $vdir)
    foreach ($d in @(Get-V2rayNCandidates)) {
        $exeHere = Test-Path -LiteralPath (Join-Path $d 'v2rayN.exe')
        $dbHere = Test-Path -LiteralPath (Join-Path $d 'guiConfigs\guiNDB.db')
        Say ('  candidate folder ' + (Split-Path -Leaf $d) + ': exe=' + $exeHere + ' guiNDB.db=' + $dbHere)
    }

    $py = Find-Python
    if ($py) { Say ('python 3: ' + $py.exe + ' ' + ($py.pre -join ' ')) } else { Say 'python 3: not found' }

    foreach ($p in @(8199, 8299)) { Say ('port ' + $p + ' free: ' + (Test-PortFree $p)) }
    $dyn = Get-FreePorts 2
    Say ('dynamic ports sample: ' + ($dyn -join ', '))

    $st = Read-Settings
    Say ('github release page: ' + (Test-Url ([string]$st.release_base)))
    Say ('raw.githubusercontent index: ' + (Test-Url ([string]$st.sub_urls_remote[0])))

    $tasks = @(Get-ScheduledTask -TaskName 'git-sync-watch-*' -ErrorAction SilentlyContinue)
    Say ('git-sync watcher tasks: ' + $tasks.Count)
    foreach ($t in $tasks) { Say ('  ' + $t.TaskName + ' state=' + $t.State) }
}

# ------------------------------------------- v2rayN-style real ping test (realtest)
function Invoke-RealtestHelper([object]$py, [string[]]$helperArgs) {
    # Runs code\v2ray_subs\v2rayn_realtest.py and returns its one JSON summary line.
    $helper = Join-Path $repo 'code\v2ray_subs\v2rayn_realtest.py'
    $all = New-Object System.Collections.ArrayList
    foreach ($x in @($py.pre)) { [void]$all.Add([string]$x) }
    [void]$all.Add($helper)
    foreach ($x in $helperArgs) { [void]$all.Add([string]$x) }
    $out = (& ([string]$py.exe) @($all.ToArray()) 2>&1 | Out-String)
    $jl = @($out -split "`r?`n" | Where-Object { $_ -match '^\s*\{' })
    if ($jl.Count -eq 0) {
        $lastLines = @($out -split "`r?`n" | Where-Object { $_.Trim() -ne '' })
        $tail = ''
        if ($lastLines.Count -gt 0) { $tail = [string]$lastLines[$lastLines.Count - 1] }
        if ($tail.Length -gt 200) { $tail = $tail.Substring(0, 200) }
        $script:helperTail = $tail
        return $null
    }
    return ($jl[$jl.Count - 1] | ConvertFrom-Json)
}

function Show-V2rayNFacts([object]$v, [object]$py) {
    # Versions, the ping URL and the last delays v2rayN stored (counts only).
    $gui = Join-Path $v.dir 'guiConfigs\guiNConfig.json'
    $d = Invoke-RealtestHelper $py @('diag', '--dir', [string]$v.dir, '--db', [string]$v.db, '--gui', $gui)
    if ($null -eq $d) { Say 'v2rayN facts: the helper gave no answer'; return }
    Say ('v2rayN cores: xray=' + [string]$d.cores.xray + ' | sing-box=' + [string]$d.cores.sing_box)
    Say ('v2rayN ping url: ' + [string]$d.ping_url + ' (' + [string]$d.ping_url_source + ')')
    if ($d.db) {
        if ($d.db.groups) {
            foreach ($p in $d.db.groups.PSObject.Properties) {
                $g = $p.Value
                Say ('v2rayN last delays, group ' + $p.Name + ': profiles=' + [string]$g.profiles + ' minus1=' + [string]$g.minus1 + ' positive=' + [string]$g.positive + ' zero=' + [string]$g.zero_or_null)
            }
        }
        if ($d.db.messages_top) {
            foreach ($m in @($d.db.messages_top)) { Say ('v2rayN message: ' + [string]$m[0] + ' x' + [string]$m[1]) }
        }
    }
}

function Invoke-V2rayNTest([object]$v, [object]$py, [string[]]$links, [string]$label, [string]$workDir) {
    # Tests the links with v2rayN's cores and ping URL. Files stay in the local work folder.
    $res = @{ label = $label; tested = 0; passed = 0; error = ''; summary = $null; passedLinks = @() }
    New-Item -ItemType Directory -Force -Path $workDir | Out-Null
    $linksFile = Join-Path $workDir ($label + '_links.txt')
    $outDir = Join-Path $workDir $label
    Write-Utf8 $linksFile (($links -join "`n") + "`n")
    $gui = Join-Path $v.dir 'guiConfigs\guiNConfig.json'
    $st = Read-Settings
    $workers = 8
    $startup = 8
    if ($st.v2rayn_realtest) {
        if ($st.v2rayn_realtest.workers) { $workers = [int]$st.v2rayn_realtest.workers }
        if ($st.v2rayn_realtest.startup_wait_sec) { $startup = [double]$st.v2rayn_realtest.startup_wait_sec }
    }
    $sum = Invoke-RealtestHelper $py @('test', '--links', $linksFile, '--dir', [string]$v.dir, '--out', $outDir, '--gui', $gui, '--workers', [string]$workers, '--startup', [string]$startup, '--label', $label)
    Remove-Item -LiteralPath $linksFile -Force -ErrorAction SilentlyContinue
    if ($null -eq $sum) { $res['error'] = ('helper gave no summary: ' + [string]$script:helperTail); return $res }
    $res['summary'] = $sum
    $res['tested'] = [int]$sum.tested
    $res['passed'] = [int]$sum.passed
    if ($sum.error) { $res['error'] = [string]$sum.error }
    $pf = Join-Path $outDir 'passed.txt'
    if (Test-Path -LiteralPath $pf) {
        $res['passedLinks'] = @(Get-Content -LiteralPath $pf -Encoding UTF8 | Where-Object { $_ -match '://' })
    }
    return $res
}

# ------------------------------------------------------------- UI refresh mode
function Invoke-V2rayNUiRefreshHelper([object]$v, [string]$groupName) {
    # Run in a nested PowerShell process so its exit code cannot end local_run.ps1.
    $helper = Join-Path $repo 'code\v2ray_subs\v2rayn_ui_refresh.ps1'
    $exe = Join-Path ([string]$v.dir) 'v2rayN.exe'
    $res = @{ ok = $false; error = ''; detail = $null }
    if (-not (Test-Path -LiteralPath $helper)) { $res.error = 'UI helper is missing'; return $res }
    if (-not (Test-Path -LiteralPath $exe)) { $res.error = 'v2rayN.exe is missing from the detected folder'; return $res }
    $out = (& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $helper -Group $groupName -Exe $exe -WaitSec 14 2>&1 | Out-String)
    $code = $LASTEXITCODE
    $jsonLines = @($out -split "`r?`n" | Where-Object { $_ -match '^\s*\{' })
    if ($jsonLines.Count -eq 0) {
        $res.error = 'UI helper did not return JSON'
        return $res
    }
    try {
        $detail = $jsonLines[$jsonLines.Count - 1] | ConvertFrom-Json
        $res.detail = $detail
        $res.ok = ([bool]$detail.ok -and $code -eq 0)
        if ($detail.error) { $res.error = [string]$detail.error }
        if (-not $res.ok -and -not $res.error) { $res.error = ('UI helper exit ' + [string]$code) }
    } catch {
        $res.error = 'UI helper returned invalid JSON'
    }
    return $res
}

function Invoke-UiRefresh {
    $script:exitCode = 2
    $st = Read-Settings
    $r = @{ mode = 'uirefresh'; stamp = $stamp; started = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss'); state = 'failed'; stage = 'find'; group = [string]$st.group_name }
    try {
        $v = Find-V2rayN
        if (-not $v.hasDb -or $v.procCount -ne 1) { throw 'v2rayN must be running as exactly one process with guiNDB.db present' }
        $r['stage'] = 'ui-refresh'
        $ui = Invoke-V2rayNUiRefreshHelper $v ([string]$st.group_name)
        if ($ui.detail) {
            $r['ui'] = @{ available = [bool]$ui.detail.ui_available; settings_group_seen = [bool]$ui.detail.settings_group_seen; main_group_seen = [bool]$ui.detail.main_group_seen; action = [string]$ui.detail.action }
            Say ('v2rayN UI: available=' + [string]$ui.detail.ui_available + ' settings_group_seen=' + [string]$ui.detail.settings_group_seen + ' main_group_seen=' + [string]$ui.detail.main_group_seen + ' action=' + [string]$ui.detail.action)
        }
        if (-not $ui.ok) { throw ('v2rayN UI group visibility was not confirmed: ' + [string]$ui.error) }
        $py = Find-Python
        if ($py) { Show-V2rayNFacts $v $py }
        $r['stage'] = 'visible'
        $r['state'] = 'ok'
        $script:exitCode = 0
        Say ('v2rayN group is visible in the running UI: ' + [string]$st.group_name)
    } catch {
        $r['error'] = [string]$_.Exception.Message
        Say ('FAILED at stage ' + [string]$r['stage'] + ': ' + $r['error'])
    }
    $r['finished'] = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $name = Write-Receipt $r
    Say ('receipt: results/v2ray_subs/' + $name + ' state=' + $r['state'])
}

# --------------------------------------------------- UI restart + real-ping mode
function Invoke-V2rayNRestartHelper([object]$v, [string]$backupDir) {
    $helper = Join-Path $repo 'code\v2ray_subs\v2rayn_restart.ps1'
    $exe = Join-Path ([string]$v.dir) 'v2rayN.exe'
    $gui = Join-Path ([string]$v.dir) 'guiConfigs\guiNConfig.json'
    $res = @{ ok = $false; error = ''; detail = $null }
    if (-not (Test-Path -LiteralPath $helper)) { $res.error = 'restart helper is missing'; return $res }
    $out = (& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $helper -Exe $exe -Db ([string]$v.db) -Gui $gui -BackupDir $backupDir -WaitSec 35 2>&1 | Out-String)
    $code = $LASTEXITCODE
    $jsonLines = @($out -split "`r?`n" | Where-Object { $_ -match '^\s*\{' })
    if ($jsonLines.Count -eq 0) { $res.error = 'restart helper did not return JSON'; return $res }
    try {
        $detail = $jsonLines[$jsonLines.Count - 1] | ConvertFrom-Json
        $res.detail = $detail
        $res.ok = ([bool]$detail.ok -and $code -eq 0)
        if ($detail.error) { $res.error = [string]$detail.error }
        if (-not $res.ok -and -not $res.error) { $res.error = ('restart helper exit ' + [string]$code) }
    } catch { $res.error = 'restart helper returned invalid JSON' }
    return $res
}

function Invoke-V2rayNGuiRealPingHelper([object]$v, [string]$groupName) {
    $helper = Join-Path $repo 'code\v2ray_subs\v2rayn_gui_realping.ps1'
    $exe = Join-Path ([string]$v.dir) 'v2rayN.exe'
    $res = @{ ok = $false; error = ''; detail = $null }
    if (-not (Test-Path -LiteralPath $helper)) { $res.error = 'GUI real-ping helper is missing'; return $res }
    $out = (& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $helper -Group $groupName -Exe $exe -WaitSec 18 2>&1 | Out-String)
    $code = $LASTEXITCODE
    $jsonLines = @($out -split "`r?`n" | Where-Object { $_ -match '^\s*\{' })
    if ($jsonLines.Count -eq 0) { $res.error = 'GUI real-ping helper did not return JSON'; return $res }
    try {
        $detail = $jsonLines[$jsonLines.Count - 1] | ConvertFrom-Json
        $res.detail = $detail
        $res.ok = ([bool]$detail.ok -and $code -eq 0)
        if ($detail.error) { $res.error = [string]$detail.error }
        if (-not $res.ok -and -not $res.error) { $res.error = ('GUI real-ping helper exit ' + [string]$code) }
    } catch { $res.error = 'GUI real-ping helper returned invalid JSON' }
    return $res
}

function Get-V2rayNGroupFacts([object]$v, [object]$py, [string]$groupName) {
    $gui = Join-Path ([string]$v.dir) 'guiConfigs\guiNConfig.json'
    $d = Invoke-RealtestHelper $py @('diag', '--dir', [string]$v.dir, '--db', [string]$v.db, '--gui', $gui, '--group', $groupName)
    if ($null -eq $d -or $null -eq $d.db -or $null -eq $d.db.target_group) { return $null }
    return $d.db.target_group
}

function Invoke-UiRestartRealPing {
    $script:exitCode = 2
    $st = Read-Settings
    $r = @{ mode = 'uirestartrealping'; stamp = $stamp; started = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss'); state = 'failed'; stage = 'find'; group = [string]$st.group_name }
    try {
        $v = Find-V2rayN
        if (-not $v.hasDb -or $v.procCount -ne 1) { throw 'v2rayN must be running as exactly one process with guiNDB.db present' }
        $py = Find-Python
        if ($null -eq $py) { throw 'python 3 is required to verify v2rayN real-ping results' }
        $before = Get-V2rayNGroupFacts $v $py ([string]$st.group_name)
        if ($null -eq $before -or -not [bool]$before.exists -or [int]$before.profiles -le 0) { throw 'the expected v2rayN group is absent from its database' }
        $r['before'] = @{ profiles = [int]$before.profiles; minus1 = [int]$before.minus1; positive = [int]$before.positive; zero_or_null = [int]$before.zero_or_null }

        $r['stage'] = 'restart'
        $work = Join-Path $env:LOCALAPPDATA 'subs-check-pro-d2a66b2d'
        $restart = Invoke-V2rayNRestartHelper $v (Join-Path $work 'backup')
        if ($restart.detail) {
            $r['restart'] = @{ stopped = [bool]$restart.detail.stopped; started = [bool]$restart.detail.started; active_index_same = [bool]$restart.detail.active_index_same; proxy_unchanged = [bool]$restart.detail.proxy_unchanged; proxy_restored = [bool]$restart.detail.proxy_restored; backup = [string]$restart.detail.backup }
            Say ('v2rayN restart: stopped=' + [string]$restart.detail.stopped + ' started=' + [string]$restart.detail.started + ' active_index_same=' + [string]$restart.detail.active_index_same + ' proxy_unchanged=' + [string]$restart.detail.proxy_unchanged)
        }
        if (-not $restart.ok) { throw ('v2rayN restart was not confirmed: ' + [string]$restart.error) }

        $v = Find-V2rayN
        if (-not $v.hasDb -or $v.procCount -ne 1) { throw 'v2rayN did not return as one running process' }
        $r['stage'] = 'ui-realping'
        $ui = Invoke-V2rayNGuiRealPingHelper $v ([string]$st.group_name)
        if ($ui.detail) {
            $r['ui'] = @{ available = [bool]$ui.detail.ui_available; group_seen = [bool]$ui.detail.group_seen; group_selected = [bool]$ui.detail.group_selected; realping_started = [bool]$ui.detail.realping_started }
            Say ('v2rayN UI: available=' + [string]$ui.detail.ui_available + ' group_seen=' + [string]$ui.detail.group_seen + ' group_selected=' + [string]$ui.detail.group_selected + ' realping_started=' + [string]$ui.detail.realping_started)
        }
        if (-not $ui.ok) { throw ('v2rayN GUI real-ping was not started: ' + [string]$ui.error) }

        $r['stage'] = 'wait-realping'
        $deadline = (Get-Date).AddSeconds(180)
        $after = $null
        do {
            Start-Sleep -Seconds 3
            $after = Get-V2rayNGroupFacts $v $py ([string]$st.group_name)
            if ($after -and [int]$after.positive -gt 0) { break }
        } while ((Get-Date) -lt $deadline)
        if ($null -eq $after) { throw 'could not read v2rayN real-ping results from its database' }
        $r['realping'] = @{ profiles = [int]$after.profiles; minus1 = [int]$after.minus1; positive = [int]$after.positive; zero_or_null = [int]$after.zero_or_null }
        Say ('v2rayN GUI real-ping results: profiles=' + [string]$after.profiles + ' positive=' + [string]$after.positive + ' minus1=' + [string]$after.minus1 + ' zero=' + [string]$after.zero_or_null)
        if ([int]$after.positive -le 0) { throw 'v2rayN GUI real-ping produced no positive delay' }

        $r['stage'] = 'passed'
        $r['state'] = 'ok'
        $script:exitCode = 0
        Say ('v2rayN GUI real-ping passed for group: ' + [string]$st.group_name)
    } catch {
        $r['error'] = [string]$_.Exception.Message
        Say ('FAILED at stage ' + [string]$r['stage'] + ': ' + $r['error'])
    }
    $r['finished'] = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $name = Write-Receipt $r
    Say ('receipt: results/v2ray_subs/' + $name + ' state=' + $r['state'])
}

# ----------------------------------------------------------------- run mode
function Invoke-Run {
    $script:exitCode = 2
    $script:downloadInfo = @{ route = ''; attempts = @() }
    $st = Read-Settings
    $work = Join-Path $env:LOCALAPPDATA 'subs-check-pro-d2a66b2d'
    foreach ($d in @('bin', 'download', 'logs', 'output', 'backup')) {
        New-Item -ItemType Directory -Force -Path (Join-Path $work $d) | Out-Null
    }
    $r = @{
        mode = 'run'
        stamp = $stamp
        started = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
        state = 'failed'
        stage = 'start'
        delivered = $false
        imported = $false
        download = $script:downloadInfo
    }
    $proc = $null
    try {
        # 1. binary: official release, SHA256 checked
        $r['stage'] = 'download'
        $exe = Get-SubsCheckExe $st $work
        $r['subs_check_pro_version'] = [string]$st.subs_check_pro_version
        Say ('subs-check-pro binary ready: ' + $r['subs_check_pro_version'] + ' (route ' + $script:downloadInfo['route'] + ')')

        # 2. config: ports chosen free at run time, never 8199/8299
        $r['stage'] = 'config'
        $ports = Get-FreePorts 2
        $outRun = Join-Path $work 'output'
        foreach ($f in @('sub\base64.txt', 'sub\all.yaml', 'sub\mihomo.yaml')) {
            Remove-Item -LiteralPath (Join-Path $outRun $f) -Force -ErrorAction SilentlyContinue
        }
        $cfgPath = Join-Path $work 'config.yaml'
        $cfg = New-Object System.Collections.ArrayList
        [void]$cfg.Add("listen-port: '127.0.0.1:" + $ports[0] + "'")
        [void]$cfg.Add("sub-store-port: ':" + $ports[1] + "'")
        [void]$cfg.Add("save-method: 'local'")
        [void]$cfg.Add("output-dir: '" + $outRun + "'")
        [void]$cfg.Add("cron-expression: ''")
        [void]$cfg.Add("check-interval: 100000")
        [void]$cfg.Add("update: false")
        [void]$cfg.Add("update-on-startup: false")
        [void]$cfg.Add("media-check: false")
        [void]$cfg.Add("enable-web-ui: true")
        [void]$cfg.Add("success-limit: " + [int]$st.success_limit)
        [void]$cfg.Add("sub-urls: []")
        [void]$cfg.Add("sub-urls-remote:")
        foreach ($u in @($st.sub_urls_remote)) { [void]$cfg.Add("  - '" + [string]$u + "'") }
        Write-Utf8 $cfgPath (($cfg -join "`n") + "`n")
        Say ('config written, local ports ' + $ports[0] + ' and ' + $ports[1])

        # 3. check (hidden process). Stop when base64.txt is saved, or on timeout.
        $r['stage'] = 'check'
        $runLog = Join-Path $work ('logs\run_' + $stamp + '.out.log')
        $errLog = Join-Path $work ('logs\run_' + $stamp + '.err.log')
        $t0 = Get-Date
        $proc = Start-Process -FilePath $exe -ArgumentList ('-f "' + $cfgPath + '"') -WorkingDirectory $work -WindowStyle Hidden -PassThru -RedirectStandardOutput $runLog -RedirectStandardError $errLog
        Say ('subs-check-pro started, pid ' + $proc.Id)
        # subs-check-pro 'local' save method writes into <output-dir>\sub\ (seen in the round-2 log)
        $allYaml = Join-Path $outRun 'sub\all.yaml'
        $b64Path = Join-Path $outRun 'sub\base64.txt'
        $deadline = $t0.AddMinutes([double]$st.check_timeout_min)
        $sawAll = $null
        $gotB64 = $false
        while ((Get-Date) -lt $deadline) {
            if ($proc.HasExited) { break }
            if (-not $sawAll -and (Test-Path -LiteralPath $allYaml)) {
                if ((Get-Item -LiteralPath $allYaml).LastWriteTime -gt $t0) { $sawAll = Get-Date }
            }
            if ($sawAll) {
                if (Test-Path -LiteralPath $b64Path) {
                    $bi = Get-Item -LiteralPath $b64Path
                    if ($bi.Length -gt 0 -and $bi.LastWriteTime -gt $t0) { $gotB64 = $true; break }
                }
                if (((Get-Date) - $sawAll).TotalSeconds -gt 300) { break }
            }
            Start-Sleep -Seconds 10
        }
        $mins = [int]((Get-Date) - $t0).TotalMinutes
        Say ('check done: all.yaml=' + [bool]$sawAll + ' base64=' + $gotB64 + ' minutes=' + $mins)
        if (-not $proc.HasExited) {
            & cmd.exe /d /c ('taskkill /PID ' + $proc.Id + ' /T /F') | Out-Null
            Start-Sleep -Seconds 2
        }
        if (-not $gotB64) {
            $r['log_tail'] = @(Get-SafeTail $errLog 12) + @(Get-SafeTail $runLog 12)
            throw 'no base64 subscription was produced (check or sub-store did not finish)'
        }

        # 4. collect: decode base64, keep every share link (any scheme://, not http/https)
        $r['stage'] = 'collect'
        $info = Get-NodeInfo $b64Path
        $nodes = @($info['nodes'])
        if ($nodes.Count -eq 0) { throw 'base64 output contained no share links' }
        $breakdown = Get-Breakdown $info['hist']
        $r['node_counts'] = @{ total = $nodes.Count; by_scheme = $info['hist'] }
        Say ('usable nodes: ' + $nodes.Count + ' (' + $breakdown + ')')

        # 4b. realtest only: test the candidates the way v2rayN does, keep the ones that answer
        if ($script:realtest) {
            $r['stage'] = 'v2rayn-test'
            $r['candidates'] = $nodes.Count
            $v2 = Find-V2rayN
            if (-not $v2.hasDb -or $v2.procCount -eq 0) { throw 'v2rayN is not running (or its database was not found), so the v2rayN-style test cannot run' }
            $py2 = Find-Python
            if ($null -eq $py2) { throw 'python 3 not found, so the v2rayN-style test cannot run' }
            $rtDir = Join-Path $work ('realtest\' + $stamp)
            Show-V2rayNFacts $v2 $py2
            $desk2 = [Environment]::GetFolderPath('Desktop')
            $prev = @(Get-ChildItem -LiteralPath $desk2 -Directory -Filter ([string]$st.desktop_folder_prefix + '*') -ErrorAction SilentlyContinue | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'v2ray_nodes_plain.txt') } | Sort-Object -Property Name -Descending)
            if ($prev.Count -gt 0 -and [bool]$st.v2rayn_realtest.control_test) {
                $prevLinks = @(Get-Content -LiteralPath (Join-Path $prev[0].FullName 'v2ray_nodes_plain.txt') -Encoding UTF8 | Where-Object { $_ -match '://' })
                $ctl = Invoke-V2rayNTest $v2 $py2 $prevLinks 'control' $rtDir
                $r['control'] = @{ folder = ('Desktop\' + $prev[0].Name); tested = $ctl.tested; passed = $ctl.passed }
                Say ('control (previous list, not delivered): tested ' + [string]$ctl.tested + ', passed ' + [string]$ctl.passed)
            }
            $t = Invoke-V2rayNTest $v2 $py2 $nodes 'candidates' $rtDir
            if ($t.error) { throw ('v2rayN-style test failed: ' + $t.error) }
            $r['v2rayn_test'] = @{ tested = $t.tested; passed = $t.passed; ping_url = [string]$t.summary.ping_url; cores = $t.summary.cores; by_reason = $t.summary.by_reason }
            Say ('v2rayN-style test: tested ' + [string]$t.tested + ', passed ' + [string]$t.passed)
            if ($t.passed -eq 0) { throw 'no candidate node passed the v2rayN-style test' }
            $nodes = @($t.passedLinks)
            $hist2 = @{}
            foreach ($p in $t.summary.by_scheme_passed.PSObject.Properties) { $hist2[$p.Name] = [int]$p.Value }
            $breakdown = Get-Breakdown $hist2
            $r['node_counts'] = @{ total = $nodes.Count; by_scheme = $hist2 }
            Say ('nodes kept for delivery: ' + $nodes.Count + ' (' + $breakdown + ')')
        }

        # 5. deliver: NEW folder on the Windows Desktop
        $r['stage'] = 'deliver'
        $desk = [Environment]::GetFolderPath('Desktop')
        $folder = Join-Path $desk ([string]$st.desktop_folder_prefix + (Get-Date -Format 'yyyyMMdd-HHmm'))
        if (Test-Path -LiteralPath $folder) { $folder = $folder + '-' + (Get-Date -Format 'ss') }
        New-Item -ItemType Directory -Force -Path $folder | Out-Null
        $fSub = Join-Path $folder 'v2ray_subscription_base64.txt'
        $fPlain = Join-Path $folder 'v2ray_nodes_plain.txt'
        $fReadme = Join-Path $folder 'README.txt'
        $fManifest = Join-Path $folder 'manifest.json'
        if ($script:realtest) {
            $b64Text = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes((($nodes -join "`n") + "`n")))
            Write-Utf8 $fSub ($b64Text + "`n")
        } else {
            Copy-Item -LiteralPath $b64Path -Destination $fSub -Force
        }
        Write-Utf8 $fPlain (($nodes -join "`n") + "`n")
        $r['delivered'] = $true
        $r['folder'] = 'Desktop\' + (Split-Path -Leaf $folder)
        Say ('delivered files to ' + $r['folder'])

        # 6. import: ONE new subscription group in v2rayN
        $r['stage'] = 'import'
        $v = Find-V2rayN
        $imp = @{ found = [bool]$v.hasDb; running = ($v.procCount -gt 0); procCount = $v.procCount; pathUnreadable = $v.unreadable; group = [string]$st.group_name; ok = $false }
        if ($v.dir) { $imp['dir_name'] = Split-Path -Leaf $v.dir }
        $importLine = ''
        if ($v.procCount -eq 0) {
            $imp['error'] = 'v2rayN is not running'
            $importLine = 'v2rayN is not running, so nothing was imported. Start v2rayN and request the import again.'
        } elseif (-not $v.hasDb) {
            $imp['error'] = 'guiNDB.db not found next to the running v2rayN'
            $importLine = 'The v2rayN database was not found where expected, so nothing was imported.'
        } else {
            $py = Find-Python
            if ($null -eq $py) {
                $imp['error'] = 'python 3 not found'
                $importLine = 'Python 3 was not found, so nothing was imported.'
            } else {
                $importPort = (Get-FreePorts 1)[0]
                $helper = Join-Path $repo 'code\v2ray_subs\v2rayn_import.py'
                $pyExe = [string]$py.exe
                $pyArgs = @()
                $pyArgs += @($py.pre)
                $pyArgs += $helper
                $pyArgs += @('--db', [string]$v.db, '--group', [string]$st.group_name, '--file', $fSub, '--port', [string]$importPort, '--backup-dir', (Join-Path $work 'backup'), '--wait', [string]([int]$st.v2rayn_import_wait_sec), '--v2rayn-running', '1')
                $impOut = (& $pyExe @pyArgs 2>&1 | Out-String)
                $jl = @($impOut -split "`r?`n" | Where-Object { $_ -match '^\s*\{' })
                if ($jl.Count -gt 0) {
                    $res = $jl[$jl.Count - 1] | ConvertFrom-Json
                    $imp['ok'] = [bool]$res.ok
                    $imp['stage'] = [string]$res.stage
                    $imp['profiles'] = $res.profiles
                    $imp['reused_group'] = $res.reused_group
                    $imp['auto_update'] = $res.auto_update
                    $imp['backup'] = $res.backup
                    $imp['subitem_columns'] = $res.subitem_columns
                    if ($res.error) { $imp['error'] = [string]$res.error }
                } else {
                    $imp['error'] = 'import helper produced no result'
                }
                if ($imp['ok']) {
                    $importLine = 'v2rayN: added subscription group "' + [string]$st.group_name + '" with ' + [string]$imp['profiles'] + ' node(s). The active node and the system proxy were not changed.'
                } else {
                    $importLine = 'v2rayN import did not complete (' + [string]$imp['error'] + '). The database backup is in the work folder.'
                }
            }
        }
        if (-not $importLine) { $importLine = 'v2rayN: added subscription group "' + [string]$st.group_name + '".' }
        if ($script:realtest -and $r['v2rayn_test']) {
            $importLine = 'Test: ' + [string]$r['v2rayn_test']['passed'] + ' of ' + [string]$r['v2rayn_test']['tested'] + ' candidate nodes answered the v2rayN-style test (its own core and ping URL). ' + $importLine
        }
        $r['imported'] = [bool]$imp['ok']
        $r['v2rayn'] = $imp
        if ($imp['ok']) {
            Say ('v2rayN: imported ' + [string]$imp['profiles'] + ' nodes into the new group')
        } else {
            Say ('v2rayN: NOT imported (' + [string]$imp['error'] + ')')
        }

        # 7. README and manifest in the folder (counts and hashes only, no links)
        $tpl = [string](Get-Content -LiteralPath (Join-Path $repo 'code\v2ray_subs\desktop_readme.txt') -Raw -Encoding UTF8)
        $txt = $tpl
        $txt = $txt.Replace('{{generated_at}}', (Get-Date).ToString('yyyy-MM-dd HH:mm'))
        $txt = $txt.Replace('{{version}}', [string]$st.subs_check_pro_version)
        $txt = $txt.Replace('{{source_count}}', [string](@($st.sub_urls_remote).Count))
        $txt = $txt.Replace('{{total}}', [string]$nodes.Count)
        $txt = $txt.Replace('{{breakdown}}', $breakdown)
        $txt = $txt.Replace('{{import_line}}', $importLine)
        Write-Utf8 $fReadme $txt $true
        $files = @()
        foreach ($f in @($fSub, $fPlain, $fReadme)) {
            $fi = Get-Item -LiteralPath $f
            $files += @{ name = $fi.Name; bytes = $fi.Length; sha256 = (Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLower() }
        }
        $r['files'] = $files
        $man = @{
            generated = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
            subs_check_pro = [string]$st.subs_check_pro_version
            source_index_count = @($st.sub_urls_remote).Count
            node_counts = $r['node_counts']
            files = $files
            v2rayn = $imp
            note = 'counts and hashes only; node links are only in v2ray_nodes_plain.txt and the base64 file'
        }
        Write-Utf8 $fManifest (($man | ConvertTo-Json -Depth 6) + "`n")
        $r['manifest'] = 'manifest.json'
        if ($r['delivered'] -and $r['imported']) { $r['state'] = 'ok' }
        elseif ($r['delivered']) { $r['state'] = 'delivered_not_imported' }
        else { $r['state'] = 'failed' }
        $script:exitCode = $(if ($r['state'] -eq 'ok') { 0 } else { 2 })
    } catch {
        $r['error'] = [string]$_.Exception.Message
        Say ('FAILED at stage ' + $r['stage'] + ': ' + $r['error'])
        $script:exitCode = 2
    } finally {
        if ($null -ne $proc -and -not $proc.HasExited) {
            & cmd.exe /d /c ('taskkill /PID ' + $proc.Id + ' /T /F') | Out-Null
        }
    }
    $r['finished'] = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $name = Write-Receipt $r
    Say ('receipt: results/v2ray_subs/' + $name + ' state=' + $r['state'])
}

# ---------------------------------------------------------------- export mode
function Invoke-Export {
    # Runs only after the user explicitly confirmed a PUBLIC push. Copies the
    # newest delivered plain node list into results/v2ray_subs so the watcher
    # commits and pushes it. No check, no v2rayN write. Every line must be a
    # share link, otherwise nothing is exported.
    $script:exitCode = 2
    $st = Read-Settings
    $desk = [Environment]::GetFolderPath('Desktop')
    $r = @{ mode = 'export'; stamp = $stamp; started = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss'); state = 'failed'; stage = 'find' }
    try {
        $cand = @(Get-ChildItem -LiteralPath $desk -Directory -Filter ([string]$st.desktop_folder_prefix + '*') -ErrorAction SilentlyContinue | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'v2ray_nodes_plain.txt') } | Sort-Object -Property Name -Descending)
        if ($cand.Count -eq 0) { throw 'no delivered folder with a plain node list was found' }
        $src = Join-Path $cand[0].FullName 'v2ray_nodes_plain.txt'
        $r['folder'] = 'Desktop\' + $cand[0].Name

        $r['stage'] = 'validate'
        $text = [System.IO.File]::ReadAllText($src, [System.Text.Encoding]::UTF8)
        $lines = @($text -split "`r?`n" | ForEach-Object { $_.Trim().TrimStart([char[]]@([char]0xFEFF, [char]0x200B)).Trim() } | Where-Object { $_ -ne '' })
        if ($lines.Count -eq 0) { throw 'the plain node list is empty' }
        $hist = @{}
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $ln = [string]$lines[$i]
            # Same rule as the refresh mode: each line starts with scheme:// (node names may contain spaces).
            # Only the line number is reported, never the line itself.
            if ($ln -notmatch '^[A-Za-z][A-Za-z0-9+.-]*://\S') { throw ('line ' + ($i + 1) + ' does not start with scheme://, export refused') }
            $sch = (($ln -split '://', 2)[0]).ToLower()
            if ($sch -eq 'http' -or $sch -eq 'https') { throw ('line ' + ($i + 1) + ' is a web link, export refused') }
            if ($hist.ContainsKey($sch)) { $hist[$sch] = [int]$hist[$sch] + 1 } else { $hist[$sch] = 1 }
        }
        $breakdown = Get-Breakdown $hist
        $r['node_counts'] = @{ total = $lines.Count; by_scheme = $hist }

        $r['stage'] = 'write'
        $outName = 'nodes_public_' + $stamp + '.txt'
        $dst = Join-Path $outDir $outName
        Write-Utf8 $dst (($lines -join "`n") + "`n")
        $r['file'] = @{ name = $outName; bytes = (Get-Item -LiteralPath $dst).Length; sha256 = (Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash.ToLower() }
        Say ('export: ' + $lines.Count + ' share links (' + $breakdown + ') -> results/v2ray_subs/' + $outName)
        $r['state'] = 'ok'
        $script:exitCode = 0
    } catch {
        $r['error'] = [string]$_.Exception.Message
        Say ('FAILED at stage ' + $r['stage'] + ': ' + $r['error'])
        $script:exitCode = 2
    }
    $r['finished'] = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $rName = Write-Receipt $r
    Say ('receipt: results/v2ray_subs/' + $rName + ' state=' + $r['state'])
}

switch ($Mode) {
    'probe' { Invoke-Probe }
    'run' { Invoke-Run }
    'realtest' { $script:realtest = $true; Invoke-Run }
    'uirefresh' { Invoke-UiRefresh }
    'uirestartrealping' { Invoke-UiRestartRealPing }
    'refresh' { Invoke-Refresh }
    'export' { Invoke-Export }
    default { Say ('unknown mode: ' + $Mode); $script:exitCode = 1 }
}
if ($Mode -eq 'probe') {
    Write-Utf8 (Join-Path $outDir ('probe_' + $stamp + '.txt')) (($script:report -join "`n") + "`n")
}
exit $script:exitCode
