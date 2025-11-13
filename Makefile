.PHONY: install test lint type-check format ci completions clean formula-test formula-update

install:
	uv sync

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check dock/ tests/

type-check:
	uv run mypy dock/

format:
	uv run ruff format dock/ tests/

ci: lint type-check test

completions:
	./scripts/generate-completions.sh

clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf dist
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

formula-test:
	./scripts/test-formula.sh

formula-update:
	@echo "Usage: make formula-update VERSION=1.0.0"
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION is required"; \
		exit 1; \
	fi
	./scripts/update-formula.sh $(VERSION)
