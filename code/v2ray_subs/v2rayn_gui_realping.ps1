# code/v2ray_subs/v2rayn_gui_realping.ps1
# Select a named v2rayN subscription group in the live UI and invoke its own
# real-ping shortcut (Ctrl+A then Ctrl+R). ASCII-only for Windows PowerShell.
param(
    [Parameter(Mandatory = $true)][string]$Group,
    [Parameter(Mandatory = $true)][string]$Exe,
    [int]$WaitSec = 18
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$uiLoadError = ''
try {
    Add-Type -AssemblyName UIAutomationClient
    Add-Type -AssemblyName UIAutomationTypes
    Add-Type -AssemblyName System.Windows.Forms
} catch {
    $uiLoadError = 'ui_automation_assembly_not_available'
}
$res = [ordered]@{
    ok = $false
    stage = 'start'
    processes = 0
    ui_available = $false
    group_seen = $false
    group_selected = $false
    realping_started = $false
    error = ''
}

function Emit([int]$code) {
    $res | ConvertTo-Json -Compress -Depth 5
    exit $code
}

function Wait-Until([scriptblock]$test, [int]$seconds) {
    $until = (Get-Date).AddSeconds([Math]::Max(1, $seconds))
    do {
        $found = & $test
        if ($null -ne $found) { return $found }
        Start-Sleep -Milliseconds 250
    } while ((Get-Date) -lt $until)
    return $null
}

function All-Elements([object]$Root) {
    if ($null -eq $Root) { return @() }
    try {
        return @($Root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
            [System.Windows.Automation.Condition]::TrueCondition))
    } catch {
        return @()
    }
}

function Window-For([object]$Element) {
    if ($null -eq $Element) { return $null }
    $walker = [System.Windows.Automation.TreeWalker]::RawViewWalker
    $cur = $Element
    for ($i = 0; $i -lt 20 -and $null -ne $cur; $i++) {
        try {
            if ($cur.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window) { return $cur }
            $cur = $walker.GetParent($cur)
        } catch { return $null }
    }
    return $null
}

function Has-ListAncestor([object]$Element) {
    $walker = [System.Windows.Automation.TreeWalker]::RawViewWalker
    $cur = $Element
    for ($i = 0; $i -lt 10 -and $null -ne $cur; $i++) {
        try {
            if ($cur.Current.ControlType -eq [System.Windows.Automation.ControlType]::List) { return $true }
            if ($cur.Current.ControlType -eq [System.Windows.Automation.ControlType]::DataGrid) { return $false }
            $cur = $walker.GetParent($cur)
        } catch { return $false }
    }
    return $false
}

function Find-GroupItem([object]$Root, [string]$Name) {
    foreach ($e in (All-Elements $Root)) {
        try {
            $n = [string]$e.Current.Name
            if (($n -eq $Name -or $n -like ('*' + $Name + '*')) -and (Has-ListAncestor $e)) { return $e }
        } catch { }
    }
    return $null
}

function Select-UiItem([object]$Element) {
    if ($null -eq $Element) { return $false }
    $walker = [System.Windows.Automation.TreeWalker]::RawViewWalker
    $cur = $Element
    for ($i = 0; $i -lt 12 -and $null -ne $cur; $i++) {
        try {
            $p = [System.Windows.Automation.SelectionItemPattern]$cur.GetCurrentPattern(
                [System.Windows.Automation.SelectionItemPattern]::Pattern)
            $p.Select()
            return $true
        } catch { }
        try { $cur = $walker.GetParent($cur) } catch { $cur = $null }
    }
    return $false
}

function First-ByControlType([object]$Root, [object]$ControlType) {
    foreach ($e in (All-Elements $Root)) {
        try { if ($e.Current.ControlType -eq $ControlType) { return $e } } catch { }
    }
    return $null
}

try {
    if ($uiLoadError) { throw $uiLoadError }
    if (-not (Test-Path -LiteralPath $Exe)) { throw 'exe_not_found' }
    $procs = @(Get-Process -Name 'v2rayN' -ErrorAction SilentlyContinue)
    $res.processes = $procs.Count
    if ($procs.Count -ne 1) { throw 'v2rayn_process_count_not_one' }

    # Signal the existing singleton to show its main window; it does not create a second instance.
    Start-Process -FilePath $Exe | Out-Null
    Start-Sleep -Seconds 2
    $procs = @(Get-Process -Name 'v2rayN' -ErrorAction SilentlyContinue)
    $res.processes = $procs.Count
    if ($procs.Count -ne 1) { throw 'v2rayn_show_signal_did_not_settle' }

    $root = [System.Windows.Automation.AutomationElement]::RootElement
    $pidCond = [System.Windows.Automation.PropertyCondition]::new(
        [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
        [object]([int]$procs[0].Id)
    )
    $main = Wait-Until {
        $wins = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $pidCond)
        foreach ($w in $wins) {
            try {
                if ($w.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window) { return $w }
            } catch { }
        }
        return $null
    } $WaitSec
    if ($null -eq $main) { throw 'ui_main_window_not_available' }
    $res.ui_available = $true
    try { $main.SetFocus() } catch { }

    $groupItem = Wait-Until { Find-GroupItem $main $Group } $WaitSec
    if ($null -eq $groupItem) { throw 'ui_group_not_visible_in_main_list' }
    $res.group_seen = $true
    if (-not (Select-UiItem $groupItem)) { throw 'ui_group_could_not_be_selected' }
    $res.group_selected = $true
    Start-Sleep -Milliseconds 1200

    $grid = Wait-Until { First-ByControlType $main ([System.Windows.Automation.ControlType]::DataGrid) } 5
    if ($null -eq $grid) { throw 'ui_profiles_grid_not_available' }
    $grid.SetFocus()
    [System.Windows.Forms.SendKeys]::SendWait('^a')
    Start-Sleep -Milliseconds 250
    [System.Windows.Forms.SendKeys]::SendWait('^r')
    $res.realping_started = $true
    $res.stage = 'realping_started'
    $res.ok = $true
    Emit 0
} catch {
    $res.error = [string]$_.Exception.Message
    if ($res.stage -eq 'start') { $res.stage = 'failed' }
    Emit 2
}
