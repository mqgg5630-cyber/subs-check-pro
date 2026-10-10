# code/v2ray_subs/v2rayn_ui_refresh.ps1
# Refresh the v2rayN subscription-group list through its own visible UI.
# This script is ASCII-only for Windows PowerShell 5.1 compatibility.
# It opens the existing v2rayN window, saves the already-created subscription
# without changing its values, then closes its subscription settings. v2rayN
# refreshes the main group list after that save/close cycle.
param(
    [Parameter(Mandatory = $true)][string]$Group,
    [Parameter(Mandatory = $true)][string]$Exe,
    [int]$WaitSec = 12
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
    settings_group_seen = $false
    main_group_seen = $false
    action = 'none'
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

function First-ById([object]$Root, [string]$Id) {
    if ($null -eq $Root) { return $null }
    try {
        $c = [System.Windows.Automation.PropertyCondition]::new(
            [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
            [object]$Id
        )
        return $Root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $c)
    } catch {
        return $null
    }
}

function Find-Text([object]$Root, [string]$Text) {
    if ($null -eq $Root) { return $null }
    try {
        $all = $Root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
            [System.Windows.Automation.Condition]::TrueCondition)
        foreach ($e in $all) {
            try {
                $n = [string]$e.Current.Name
                if ($n -eq $Text -or $n -like ('*' + $Text + '*')) { return $e }
            } catch { }
        }
    } catch { }
    return $null
}

function Window-For([object]$Element) {
    if ($null -eq $Element) { return $null }
    $walker = [System.Windows.Automation.TreeWalker]::RawViewWalker
    $cur = $Element
    for ($i = 0; $i -lt 20 -and $null -ne $cur; $i++) {
        try {
            if ($cur.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window) { return $cur }
            $cur = $walker.GetParent($cur)
        } catch {
            return $null
        }
    }
    return $null
}

function Invoke-Ui([object]$Element) {
    if ($null -eq $Element) { return $false }
    try {
        $p = [System.Windows.Automation.InvokePattern]$Element.GetCurrentPattern(
            [System.Windows.Automation.InvokePattern]::Pattern)
        $p.Invoke()
        return $true
    } catch { }
    try {
        $Element.SetFocus()
        [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
        return $true
    } catch { }
    return $false
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

function Close-Settings([object]$Window) {
    if ($null -eq $Window) { return }
    $close = First-ById $Window 'menuClose'
    if (Invoke-Ui $close) { return }
    try {
        $Window.SetFocus()
        [System.Windows.Forms.SendKeys]::SendWait('{ESC}')
    } catch { }
}

try {
    if ($uiLoadError) { throw $uiLoadError }
    if (-not (Test-Path -LiteralPath $Exe)) { throw 'exe_not_found' }

    $procs = @(Get-Process -Name 'v2rayN' -ErrorAction SilentlyContinue)
    $res.processes = $procs.Count
    if ($procs.Count -ne 1) { throw 'v2rayn_process_count_not_one' }

    # A second normal launch only signals the already-running single instance to show itself.
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

    $subSetting = Wait-Until { First-ById $main 'menuSubSetting' } 3
    if ($null -eq $subSetting) { throw 'ui_subscription_settings_control_not_found' }
    if (-not (Invoke-Ui $subSetting)) { throw 'ui_subscription_settings_could_not_open' }
    $res.action = 'opened_settings'

    $subList = Wait-Until { First-ById $root 'lstSubscription' } $WaitSec
    if ($null -eq $subList) { throw 'ui_subscription_settings_not_opened' }
    $settingsWindow = Window-For $subList
    if ($null -eq $settingsWindow) { throw 'ui_subscription_settings_window_not_found' }

    $groupElement = Wait-Until { Find-Text $settingsWindow $Group } 4
    if ($null -eq $groupElement) {
        Close-Settings $settingsWindow
        throw 'ui_group_not_visible_in_subscription_settings'
    }
    $res.settings_group_seen = $true
    if (-not (Select-UiItem $groupElement)) {
        Close-Settings $settingsWindow
        throw 'ui_group_could_not_be_selected'
    }

    $edit = First-ById $settingsWindow 'menuSubEdit'
    if ($null -eq $edit -or -not (Invoke-Ui $edit)) {
        Close-Settings $settingsWindow
        throw 'ui_subscription_edit_could_not_open'
    }
    $res.action = 'saved_existing_subscription'

    $save = Wait-Until { First-ById $root 'btnSave' } $WaitSec
    if ($null -eq $save -or -not (Invoke-Ui $save)) {
        Close-Settings $settingsWindow
        throw 'ui_subscription_save_could_not_invoke'
    }
    Start-Sleep -Milliseconds 700
    Close-Settings $settingsWindow
    Start-Sleep -Milliseconds 900

    $groupList = Wait-Until { First-ById $main 'lstGroup' } 4
    $visible = Find-Text $groupList $Group
    if ($null -ne $visible) { $res.main_group_seen = $true }
    if (-not $res.main_group_seen) { throw 'ui_refresh_completed_but_group_not_seen_in_main_list' }

    $res.stage = 'visible'
    $res.ok = $true
    Emit 0
} catch {
    $res.error = [string]$_.Exception.Message
    if (-not $res.stage -or $res.stage -eq 'start') { $res.stage = 'failed' }
    Emit 2
}
