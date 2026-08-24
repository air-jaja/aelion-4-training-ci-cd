#!/usr/bin/env bash
set -euo pipefail

jalon="${1:-}"
if [[ ! "$jalon" =~ ^(0[1-9]|1[0-2])(-[a-z0-9-]+)?$ ]]; then
  echo "Usage: bash scripts/formation/verifier_jalon.sh 03" >&2
  exit 2
fi

jalon_number="${jalon:0:2}"

root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Ouvrez un terminal dans le depot CISIA." >&2
  exit 2
}
cd "$root"

if [[ ${#jalon} -eq 2 ]]; then
  marker_matches=$(grep -Ec "^# Jalon actuel : ${jalon_number}(-|$)" FORMATION/JALON_ACTUEL.md || true)
else
  marker_matches=$(grep -Fxc "# Jalon actuel : $jalon" FORMATION/JALON_ACTUEL.md || true)
fi
if [[ "$marker_matches" -ne 1 ]]; then
  echo "Le marqueur local ne correspond pas au jalon demande : $jalon" >&2
  exit 1
fi

uv sync --frozen --extra dev
uv run pytest -q
uv run ruff check .

echo "Jalon verifie : jalon/$jalon_number"
