[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^(0[1-9]|1[0-2])(?:-[a-z0-9-]+)?$')]
    [string]$Jalon
)

$ErrorActionPreference = 'Stop'
$root = (& git rev-parse --show-toplevel 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $root) {
    throw 'Ouvrez un terminal dans le depot CISIA.'
}
Set-Location -LiteralPath $root

$jalonNumber = $Jalon.Substring(0, 2)
$marker = Get-Content -LiteralPath 'FORMATION/JALON_ACTUEL.md' -Raw
$markerPattern = if ($Jalon.Length -eq 2) {
    "(?m)^# Jalon actuel : $([regex]::Escape($jalonNumber))(?:-|$)"
} else {
    "(?m)^# Jalon actuel : $([regex]::Escape($Jalon))\r?$"
}
if ($marker -notmatch $markerPattern) {
    throw "Le marqueur local ne correspond pas au jalon demande : $Jalon"
}

& uv sync --frozen --extra dev
if ($LASTEXITCODE -ne 0) { throw 'uv sync a echoue.' }
& uv run pytest -q
if ($LASTEXITCODE -ne 0) { throw 'pytest a echoue.' }
& uv run ruff check .
if ($LASTEXITCODE -ne 0) { throw 'ruff a echoue.' }

Write-Host "Jalon verifie : jalon/$jalonNumber"
