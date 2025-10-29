# Makefile for dock project (classic tab style)
SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

BATS       ?= bats
SHELLCHECK ?= shellcheck
SHFMT      ?= shfmt
YQ         ?= yq
TESTS_BIN  := $(CURDIR)/tests/bin

help: ## Show this help
	@awk 'BEGIN {FS":.*##"; printf "\nTargets:\n"} /^[a-zA-Z0-9_.-]+:.*##/ {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' "$(MAKEFILE_LIST)" ; echo

install: ## Install dev tools
	brew list --versions bats-core >/dev/null 2>&1 || brew install bats-core
	brew list --versions shellcheck >/dev/null 2>&1 || brew install shellcheck
	brew list --versions shfmt >/dev/null 2>&1 || brew install shfmt
	brew list --versions yq >/dev/null 2>&1 || brew install yq

lint: ## Run shellcheck
	$(SHELLCHECK) ./dock

fmt: ## Apply shfmt formatting
	$(SHFMT) -w .

fmt-check: ## Check formatting
	$(SHFMT) -d .

test: ## Run bats tests
	chmod +x $(TESTS_BIN)/* || true
	PATH="$(TESTS_BIN):$$PATH" $(BATS) tests/bats

ci: install lint fmt-check test ## Full CI pipeline
	echo "All checks passed ✅"

.PHONY: help install lint fmt fmt-check test ci
