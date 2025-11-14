.PHONY: install audit test lint type-check format ci formula-test clean

install:
	uv sync

audit:
	uv export --group dev --no-emit-project > requirements.txt
	python3 -m pip install -U pip-audit
	python3 -m pip_audit -r requirements.txt

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check dock/ tests/

type-check:
	uv run mypy dock/

format:
	uv run ruff format dock/ tests/

ci: lint type-check test audit

formula-test:
	./scripts/test-formula.sh

clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf dist
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
