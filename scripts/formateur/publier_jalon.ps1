[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^\d{2}-[a-z0-9-]+$')]
    [string]$Jalon
)

$ErrorActionPreference = 'Stop'
$root = (& git rev-parse --show-toplevel 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $root) { throw 'Depot Git introuvable.' }
Set-Location -LiteralPath $root

if (@(& git status --porcelain).Count -gt 0) {
    throw 'Le depot de preparation doit etre propre avant toute publication.'
}

$source = "preparation/$Jalon"
$target = "jalon/$Jalon"
& git show-ref --verify --quiet "refs/heads/$source"
if ($LASTEXITCODE -ne 0) { throw "Branche locale absente : $source" }

$origin = (& git remote get-url origin).Trim()
if ($origin -notmatch 'github\.com[/:]thomasfesq/CISIA_24082026_Parcours(?:\.git)?$') {
    throw "Remote refuse : $origin"
}

$remoteOid = (& git ls-remote --heads origin "refs/heads/$target").Trim()
if ($remoteOid) {
    $published = ($remoteOid -split '\s+')[0]
    $local = (& git rev-parse "refs/heads/$source").Trim()
    if ($published -eq $local) {
        Write-Host "Deja publie a l'identique : $target"
        exit 0
    }
    throw "Le jalon distant existe avec un autre commit. Aucune reecriture automatique."
}

if ($PSCmdlet.ShouldProcess("origin/$target", "publier uniquement $source")) {
    & git push origin "refs/heads/$source`:refs/heads/$target"
    if ($LASTEXITCODE -ne 0) { throw 'Publication Git echouee.' }
    Write-Host "Publie : $target"
}
