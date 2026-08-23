#!/usr/bin/env bash
set -euo pipefail

echo "== System tools =="
python3 --version || true
uv --version
git --version
docker --version || true

echo
echo "== Project checks =="
uv venv --python 3.13
uv sync --extra dev
uv run python --version
uv run python -c "import indusense; print(indusense.__file__)"
uv run pytest -q
uv run ruff check .
uv run black --check .
uv run indusense --help
uv run indusense check-data
uv run indusense build-gold
