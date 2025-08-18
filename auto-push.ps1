param(
    [string]$RepoPath = ".",
    [int]$DebounceSeconds = 10,
    [string]$RemoteName = "origin",
    [string]$BranchName = "main"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location $RepoPath

if (-not (Test-Path ".git")) {
    git init | Out-Null
    git branch -M $BranchName | Out-Null
}

$remoteUrl = $null
try { $remoteUrl = git config --get remote.$RemoteName.url 2>$null } catch {}
if (-not $remoteUrl) {
    Write-Host "No remote '$RemoteName' configured. Set it once: git remote add origin https://github.com/<USERNAME>/<REPO>.git" -ForegroundColor Yellow
}

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = (Resolve-Path ".").Path
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true
$watcher.Filter = "*.*"

$ignoredSubstrings = @(
    "\.git\",
    "__pycache__",
    ".venv",
    "node_modules",
    ".idea",
    ".vscode"
)

$script:changePending = $false
$script:lastChangeTime = Get-Date

$action = {
    param($source, $eventArgs)

    $path = $eventArgs.FullPath
    foreach ($s in $script:ignoredSubstrings) {
        if ($path -like "*${s}*") { return }
    }

    $script:changePending = $true
    $script:lastChangeTime = Get-Date
}

$created = Register-ObjectEvent $watcher Created -Action $action
$changed = Register-ObjectEvent $watcher Changed -Action $action
$deleted = Register-ObjectEvent $watcher Deleted -Action $action
$renamed = Register-ObjectEvent $watcher Renamed -Action $action

Write-Host "Auto-push watcher running in '$(Get-Location)'. Debounce: $DebounceSeconds s. Press Ctrl+C to stop." -ForegroundColor Cyan

try {
    while ($true) {
        Start-Sleep -Seconds 1
        if ($script:changePending -and ((Get-Date) - $script:lastChangeTime).TotalSeconds -ge $DebounceSeconds) {
            $script:changePending = $false

            git add -A | Out-Null
            $status = git status --porcelain
            if ($status) {
                $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                $msg = "Auto: update $timestamp"
                git commit -m $msg | Out-Null
                if ($remoteUrl) {
                    try { git pull --rebase $RemoteName $BranchName | Out-Null } catch {}
                    git push $RemoteName $BranchName | Out-Null
                    Write-Host "Pushed at $timestamp" -ForegroundColor Green
                } else {
                    Write-Host "Committed locally at $timestamp (no remote configured)." -ForegroundColor Yellow
                }
            }
        }
    }
}
finally {
    if ($created) { Unregister-Event -SourceIdentifier $created.Name }
    if ($changed) { Unregister-Event -SourceIdentifier $changed.Name }
    if ($deleted) { Unregister-Event -SourceIdentifier $deleted.Name }
    if ($renamed) { Unregister-Event -SourceIdentifier $renamed.Name }
    $watcher.Dispose()
}


