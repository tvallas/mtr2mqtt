.PHONY: install test lint build lock update-deps

default: test

install:
	uv sync --group dev

test:
	uv run pytest -v

lint:
	uv run pylint $$(find mtr2mqtt -name "*.py" -type f)

build:
	uv build

lock:
	uv lock

update-deps:
	uv lock --upgrade
	uv sync --group dev
