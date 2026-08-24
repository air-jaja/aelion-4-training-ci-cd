[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^(0[1-9]|1[0-2])(?:-[a-z0-9-]+)?$')]
    [string]$Jalon,

    [switch]$Rattrapage
)

$ErrorActionPreference = 'Stop'

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    & git @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Git a echoue : git $($Arguments -join ' ')"
    }
}

$root = (& git rev-parse --show-toplevel 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $root) {
    throw 'Ouvrez un terminal dans le depot CISIA avant de lancer ce script.'
}
Set-Location -LiteralPath $root

$branch = (& git branch --show-current).Trim()
if (-not $branch) {
    throw 'HEAD detache : revenez sur votre branche personnelle.'
}
if ($branch -eq 'main' -or $branch.StartsWith('jalon/')) {
    throw "Branche protegee '$branch' : creez d'abord une branche personnelle avec git switch -c prenom-nom."
}

$dirty = @(& git status --porcelain)
if ($dirty.Count -gt 0) {
    throw 'Travail non enregistre. Faites git status, git add -A puis git commit avant le jalon.'
}

$jalonNumber = $Jalon.Substring(0, 2)
$remoteBranch = "jalon/$jalonNumber"
Invoke-Git fetch origin "refs/heads/$remoteBranch`:refs/remotes/origin/$remoteBranch"

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$safeBranch = ($branch -replace '[^A-Za-z0-9._-]', '-')
$backup = "sauvegarde/$safeBranch/$stamp"
Invoke-Git branch $backup HEAD
Write-Host "Sauvegarde creee : $backup"

& git pull --no-rebase --no-edit origin $remoteBranch
if ($LASTEXITCODE -ne 0) {
    $gitDir = (& git rev-parse --git-dir).Trim()
    if (Test-Path -LiteralPath (Join-Path $gitDir 'MERGE_HEAD')) {
        & git merge --abort
    }

    if (-not $Rattrapage) {
        throw "Fusion annulee. Relancez avec -Rattrapage pour repartir du jalon officiel ; votre travail reste dans '$branch' et '$backup'."
    }

    $rescue = "rattrapage/$jalonNumber/$stamp"
    Invoke-Git switch -c $rescue "origin/$remoteBranch"
    Write-Host "Mode rattrapage actif : $rescue"
    Write-Host "Travail precedent preserve : $branch et $backup"
    exit 0
}

Write-Host "Jalon integre sur $branch : $remoteBranch"
Invoke-Git status --short --branch
