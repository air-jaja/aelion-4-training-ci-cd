[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9._-]+$')]
    [string]$Binome,

    [string]$Destination
)

$ErrorActionPreference = 'Stop'
$root = (& git rev-parse --show-toplevel 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $root) {
    throw 'Lancez ce script depuis le depot du parcours.'
}

$bundle = Join-Path $root 'FORMATION/EXERCICES/J6/J6-gameday.bundle'
if (-not (Test-Path -LiteralPath $bundle)) { throw "Bundle absent : $bundle" }

if (-not $Destination) {
    $Destination = Join-Path (Split-Path -Parent $root) "CISIA_J6_GAMEDAY_$Binome"
}
$absoluteDestination = [System.IO.Path]::GetFullPath($Destination)
if (Test-Path -LiteralPath $absoluteDestination) {
    throw "Destination deja presente, aucune ecriture : $absoluteDestination"
}

& git clone -b J6-gameday $bundle $absoluteDestination
if ($LASTEXITCODE -ne 0) { throw 'Clone du bundle Game Day echoue.' }

& git -C $absoluteDestination switch -c "reparation-$Binome"
if ($LASTEXITCODE -ne 0) { throw 'Creation de la branche de reparation echouee.' }

& git -C $absoluteDestination rev-parse --verify v1.0-sain
if ($LASTEXITCODE -ne 0) { throw 'Tag sain absent du clone.' }

Write-Host "Game Day pret : $absoluteDestination"
Write-Host "Branche de travail : reparation-$Binome"
