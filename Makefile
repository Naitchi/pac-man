.PHONY: install run debug build clean fclean lint lint-strict

CONFIG ?= config.json

install:
	uv sync

run:
	uv run python -m pac-man $(CONFIG)

debug:
	uv run python -m pdb -m pac-man $(CONFIG)

build:
	uv run pyinstaller --noconfirm --name Pac-Man --paths . --add-data "config.json:json" --add-data "highscores.json:json" --add-data "src/entities/assets:assets" src/build-entry.py

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +

fclean:
	$(MAKE) clean
	rm -rf dist/ build/ .venv/ Pac-Man.spec

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict
