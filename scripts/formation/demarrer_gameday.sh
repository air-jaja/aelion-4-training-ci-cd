#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: bash scripts/formation/demarrer_gameday.sh IDENTIFIANT [DESTINATION]" >&2
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
  exit 2
fi

binome="$1"
if [[ ! "$binome" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "Identifiant invalide : lettres, chiffres, point, tiret ou underscore uniquement." >&2
  exit 2
fi

root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Lancez ce script depuis le depot du parcours." >&2
  exit 1
}
bundle="$root/FORMATION/EXERCICES/J6/J6-gameday.bundle"
if [[ ! -f "$bundle" ]]; then
  echo "Bundle absent : $bundle" >&2
  exit 1
fi

if [[ $# -eq 2 ]]; then
  destination="$2"
else
  destination="$(dirname "$root")/CISIA_J6_GAMEDAY_$binome"
fi

if [[ -e "$destination" ]]; then
  echo "Destination deja presente, aucune ecriture : $destination" >&2
  exit 1
fi

git clone -b J6-gameday "$bundle" "$destination"
git -C "$destination" remote rename origin bundle-local
git -C "$destination" remote set-url --push bundle-local DISABLED
git -C "$destination" switch -c "reparation-$binome"
git -C "$destination" rev-parse --verify 'v1.0-sain^{commit}' >/dev/null

echo "Game Day pret : $destination"
echo "Branche de travail : reparation-$binome"
echo "Remote local : bundle-local (lecture seule pedagogique ; ne pas pousser)"
