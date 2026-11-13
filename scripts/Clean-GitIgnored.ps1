<#
.SYNOPSIS
    Deletes every git-ignored file in all git repositories below a folder.

.DESCRIPTION
    Finds git repositories under -Root and runs `git clean -fdX` in each one.
    -X removes ONLY files that .gitignore (and .git/info/exclude and the global
    ignore file) would ignore. Tracked files and untracked-but-not-ignored files
    are never touched.

    By default the script is a DRY RUN: it only lists what would be deleted.
    Pass -Execute to really delete.

    WARNING: "ignored" often includes things you may want to keep, such as
    .env files, local config, virtual environments and node_modules. Read the
    dry-run output first.

.PARAMETER Root
    Folder that contains the repositories. Defaults to the current folder.
    If Root itself is a repository, it is cleaned too.

.PARAMETER MaxDepth
    How many folder levels below Root to search for repositories. Default 3.

.PARAMETER Execute
    Actually delete. Without this switch nothing is removed.

.EXAMPLE
    .\Clean-GitIgnored.ps1 -Root C:\src
    Dry run: shows what would be deleted in every repo under C:\src.

.EXAMPLE
    .\Clean-GitIgnored.ps1 -Root C:\src -Execute
    Deletes the ignored files.
#>
[CmdletBinding()]
param(
    [string]$Root = (Get-Location).Path,
    [int]$MaxDepth = 3,
    [switch]$Execute
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'git was not found on PATH.'
}

$Root = (Resolve-Path -LiteralPath $Root).Path

# Recursively find repos. A ".git" directory (normal repo) or file (worktree/submodule)
# marks a repo. We do not descend into a repo: nested repos are handled by their own
# `git clean`, and `git clean -X` skips nested repos anyway.
function Find-GitRepo {
    param([string]$Path, [int]$Depth)

    if (Test-Path -LiteralPath (Join-Path $Path '.git')) {
        $Path
        return
    }
    if ($Depth -le 0) { return }

    Get-ChildItem -LiteralPath $Path -Directory -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne '.git' } |
        ForEach-Object { Find-GitRepo -Path $_.FullName -Depth ($Depth - 1) }
}

$repos = @(Find-GitRepo -Path $Root -Depth $MaxDepth)

if ($repos.Count -eq 0) {
    Write-Host "No git repositories found under $Root (depth $MaxDepth)."
    return
}

$mode = if ($Execute) { 'DELETING' } else { 'DRY RUN (use -Execute to delete)' }
Write-Host "Mode: $mode"
Write-Host "Found $($repos.Count) repo(s) under $Root`n"

$failed = @()
foreach ($repo in $repos) {
    Write-Host "== $repo" -ForegroundColor Cyan

    # -f force, -d include directories, -X only ignored files, -n dry run
    $gitArgs = @('-C', $repo, 'clean', '-f', '-d', '-X')
    if (-not $Execute) { $gitArgs += '-n' }

    $output = & git @gitArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "git clean failed in ${repo}: $output"
        $failed += $repo
        continue
    }

    if ($output) { $output | ForEach-Object { Write-Host "   $_" } }
    else { Write-Host '   (nothing ignored)' -ForegroundColor DarkGray }
}

if ($failed.Count -gt 0) {
    Write-Warning "Failed in $($failed.Count) repo(s):`n$($failed -join "`n")"
    exit 1
}
