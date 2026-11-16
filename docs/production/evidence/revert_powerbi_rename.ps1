<#
.SYNOPSIS
    Reverts OWNER-PBI-REN-001 (canonical Power BI rename) to the received state.

.DESCRIPTION
    Three escalating levels, per POWERBI_RENAME_BASELINE.md section 10. Every level
    finishes by recomputing SHA256 against the baseline manifest and requires zero
    divergences, because .gitattributes declares `text eol=crlf` for the frozen
    scientific CSVs and a checkout that rewrites them would change their bytes.

    Level 2 keeps the fix/powerbi-canonical-naming-pbix branch, so the evidence of
    the attempt survives the revert. Nothing here deletes that branch.

.PARAMETER Level
    1  Reset the working tree to the baseline commit (keeps the branch).
    2  Switch back to main only (discards nothing; least destructive).
    3  Physical restore from the untouched backup tree, if Git is unusable.

.PARAMETER Confirm
    Required for levels 1 and 3, which overwrite working-tree files.

.PARAMETER Backup
    Level 3 only: the untouched copy of the received state. It lives outside the
    repository, so it cannot be derived and must be passed.

.EXAMPLE
    .\revert_powerbi_rename.ps1 -Level 2
.EXAMPLE
    .\revert_powerbi_rename.ps1 -Level 1 -Confirm
.EXAMPLE
    .\revert_powerbi_rename.ps1 -Level 3 -Confirm -Backup 'X:\copia\steel-plates-quality-mlops'
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet(1, 2, 3)][int]$Level,
    [switch]$Confirm,
    # Level 3 restores from the untouched copy of the received state. It lives outside
    # the repository, so there is nothing to derive it from -- pass it explicitly.
    [string]$Backup
)

$ErrorActionPreference = 'Stop'

# docs\production\evidence\<this script> -> repository root
$Repo     = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$Baseline = 'be46d0c'
$Manifest = Join-Path $Repo 'docs\production\evidence\powerbi_rename_baseline_inventory.json'

function Assert-DesktopClosed {
    $open = Get-CimInstance Win32_Process -Filter "Name='PBIDesktop.exe'" |
        Where-Object { $_.CommandLine -like "*steel-plates-quality-mlops*" }
    if ($open) {
        $open | ForEach-Object { Write-Host "  PID $($_.ProcessId): $($_.CommandLine)" }
        throw 'Power BI Desktop has this project open. Close it before reverting.'
    }
    Write-Host 'Power BI Desktop does not hold this project. OK.'
}

function Test-BaselineIntegrity {
    # The manifest is the received state, so it never lists the deliverables added
    # afterwards; a file missing from disk is a real failure, an extra file is not.
    if (-not (Test-Path -LiteralPath $Manifest)) {
        Write-Warning "Baseline manifest not found: $Manifest"
        Write-Warning 'Recover it from commit ea40f4a before trusting this revert.'
        return $false
    }
    $entries = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
    $bad = @()
    foreach ($entry in $entries) {
        $path = Join-Path $Repo ($entry.path -replace '/', '\')
        if (-not (Test-Path -LiteralPath $path)) { $bad += "MISSING  $($entry.path)"; continue }
        $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLower()
        if ($hash -ne $entry.sha256) { $bad += "MISMATCH $($entry.path)" }
    }
    Write-Host ''
    Write-Host "Verified $($entries.Count) baseline files; $($bad.Count) divergences."
    $bad | ForEach-Object { Write-Host "  $_" }
    return ($bad.Count -eq 0)
}

Assert-DesktopClosed

switch ($Level) {
    1 {
        if (-not $Confirm) { throw 'Level 1 overwrites working-tree files. Re-run with -Confirm.' }
        Write-Host "Level 1: resetting the working tree to $Baseline."
        Push-Location -LiteralPath $Repo
        try {
            git stash list
            git reset --hard $Baseline
            # -fd only: -x would delete .venv and the caches, which is not a revert.
            git clean -fd
        } finally { Pop-Location }
    }
    2 {
        Write-Host 'Level 2: switching to main; the rename branch is preserved.'
        Push-Location -LiteralPath $Repo
        try {
            git checkout main
            git branch --list 'fix/powerbi-canonical-naming-pbix'
        } finally { Pop-Location }
    }
    3 {
        if (-not $Confirm) { throw 'Level 3 overwrites working-tree files. Re-run with -Confirm.' }
        if (-not $Backup) { throw 'Level 3 needs -Backup <path to the untouched copy>.' }
        if (-not (Test-Path -LiteralPath $Backup)) { throw "Backup tree not found: $Backup" }
        Write-Host 'Level 3: physical restore from the untouched backup tree.'
        # /XD .git keeps the repository history; the backup has none of its own.
        robocopy $Backup $Repo /MIR /XD __pycache__ .pytest_cache .git /NFL /NDL /NJH /R:1 /W:1
        if ($LASTEXITCODE -ge 8) { throw "robocopy failed with exit code $LASTEXITCODE." }
        Write-Host "robocopy exit $LASTEXITCODE (below 8 means success)."
    }
}

if (Test-BaselineIntegrity) {
    Write-Host ''
    Write-Host 'REVERT VERIFIED: every baseline file matches its recorded SHA256.'
    exit 0
}

Write-Host ''
Write-Warning 'REVERT NOT VERIFIED. Do not report the revert as complete.'
Write-Warning 'Investigate the divergences above before any further change.'
exit 1
