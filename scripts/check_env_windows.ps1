$ErrorActionPreference = "Continue"

Write-Host "== System tools =="
python --version
py -0p
uv --version
git --version
wsl -l -v
docker --version

Write-Host "`n== Project checks =="
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
