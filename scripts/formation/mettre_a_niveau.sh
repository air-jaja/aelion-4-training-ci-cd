#!/usr/bin/env bash
set -euo pipefail

jalon="${1:-}"
rattrapage="${2:-}"
if [[ ! "$jalon" =~ ^(0[1-9]|1[0-2])(-[a-z0-9-]+)?$ ]]; then
  echo "Usage: bash scripts/formation/mettre_a_niveau.sh 03 [--rattrapage]" >&2
  exit 2
fi
if [[ -n "$rattrapage" && "$rattrapage" != "--rattrapage" ]]; then
  echo "Option inconnue : $rattrapage" >&2
  exit 2
fi

root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Ouvrez un terminal dans le depot CISIA." >&2
  exit 2
}
cd "$root"

branch="$(git branch --show-current)"
if [[ -z "$branch" || "$branch" == "main" || "$branch" == jalon/* ]]; then
  echo "Travaillez sur une branche personnelle, pas sur '$branch'." >&2
  exit 2
fi
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Commitez votre travail avant le nouveau jalon." >&2
  exit 2
fi

jalon_number="${jalon:0:2}"
remote_branch="jalon/$jalon_number"
git fetch origin "refs/heads/$remote_branch:refs/remotes/origin/$remote_branch"
stamp="$(date +%Y%m%d-%H%M%S)"
safe_branch="${branch//\//-}"
backup="sauvegarde/$safe_branch/$stamp"
git branch "$backup" HEAD
echo "Sauvegarde creee : $backup"

if ! git pull --no-rebase --no-edit origin "$remote_branch"; then
  if git rev-parse -q --verify MERGE_HEAD >/dev/null; then
    git merge --abort
  fi
  if [[ "$rattrapage" != "--rattrapage" ]]; then
    echo "Fusion annulee. Travail preserve dans '$branch' et '$backup'." >&2
    echo "Relancez avec --rattrapage pour repartir du jalon officiel." >&2
    exit 1
  fi

  rescue="rattrapage/$jalon_number/$stamp"
  git switch -c "$rescue" "origin/$remote_branch"
  echo "Mode rattrapage actif : $rescue"
  echo "Travail precedent preserve : $branch et $backup"
  exit 0
fi

echo "Jalon integre sur $branch : $remote_branch"
git status --short --branch
