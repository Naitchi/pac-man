.PHONY: install run debug build clean lint lint-strict

CONFIG ?= config.json

install:
	uv sync

run:
	uv run python -m src.pac-man $(CONFIG)

debug:
	uv run python -m pdb -m src.pac-man $(CONFIG)

build:
	uv run --with pyinstaller pyinstaller -n Pac-Man -p . src/pac-man.py

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +

lint:
	uv run flake8 src/
	uv run mypy src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 src/
	uv run mypy src/ --strict
