$ErrorActionPreference = "Stop"

Write-Host "== System tools =="
if (Get-Command python -ErrorAction SilentlyContinue) { python --version }
if (Get-Command py -ErrorAction SilentlyContinue) { py -0p }
uv --version
git --version
if (Get-Command wsl -ErrorAction SilentlyContinue) { wsl -l -v }
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker --version
    docker compose version
}

Write-Host "`n== Project checks =="
uv venv --python 3.13
uv sync --frozen --extra dev
uv run python --version
uv run python -c "import indusense; print(indusense.__file__)"
uv run pytest -q
uv run ruff check .
uv run black --check .
uv run indusense --help
uv run indusense check-data
uv run indusense build-gold
