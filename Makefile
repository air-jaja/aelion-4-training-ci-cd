install:
	uv sync --extra dev

test:
	uv run pytest -q

lint:
	uv run ruff check .

format-check:
	uv run black --check .

check:
	uv run pytest -q
	uv run ruff check .
	uv run black --check .
	uv run indusense --help
