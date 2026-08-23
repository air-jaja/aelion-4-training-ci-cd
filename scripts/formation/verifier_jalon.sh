#!/usr/bin/env bash
set -euo pipefail

jalon="${1:-}"
if [[ ! "$jalon" =~ ^[0-9]{2}-[a-z0-9-]+$ ]]; then
  echo "Usage: bash scripts/formation/verifier_jalon.sh 03-j2-matin-m25" >&2
  exit 2
fi

root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Ouvrez un terminal dans le depot CISIA." >&2
  exit 2
}
cd "$root"

if ! grep -Fq "$jalon" FORMATION/JALON_ACTUEL.md; then
  echo "Le marqueur local ne correspond pas au jalon demande : $jalon" >&2
  exit 1
fi

uv sync --frozen --extra dev
uv run pytest -q
uv run ruff check .

echo "Jalon verifie : $jalon"
