# Project Nexus Polyglot Monorepo Makefile
# Runtimes: Python (uv) 3.12+, TypeScript (pnpm) 5.6+, Go 1.23+, Rust 1.82+

.PHONY: all help install dev lint lint-fix typecheck test format format-check clean db-up db-down

SHELL := /bin/bash
.DEFAULT_GOAL := help

help: ## Display available make targets
	@echo "Project Nexus Monorepo Toolchain Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies across all polyglot runtimes
	@echo "==> Installing Node & TypeScript packages (pnpm)..."
	pnpm install
	@echo "==> Syncing Python virtual environment (uv)..."
	uv sync
	@echo "==> Downloading Go modules..."
	cd services/nexus-worker-go && go mod download
	@echo "==> Dependencies successfully installed across all runtimes."

dev: ## Boot development servers concurrently
	@echo "==> Starting local infrastructure and application services..."
	pnpm turbo run dev

lint: ## Run static code analysis across Python, TypeScript, and Go
	@echo "==> Running Ruff lint check (Python)..."
	uv run ruff check .
	@echo "==> Running Turborepo lint (TypeScript)..."
	pnpm turbo run lint
	@echo "==> Running Go vet..."
	cd services/nexus-worker-go && go vet ./...

lint-fix: ## Automatically fix lint violations across runtimes
	@echo "==> Auto-fixing Python violations (Ruff)..."
	uv run ruff check --fix .
	@echo "==> Auto-fixing TypeScript / Web violations..."
	pnpm turbo run lint:fix

format: ## Format all Python and TypeScript codebase files
	@echo "==> Formatting Python files (Ruff)..."
	uv run ruff format .
	@echo "==> Formatting TypeScript/JSON/YAML files (Prettier)..."
	pnpm run format

format-check: ## Assert zero unformatted files across runtimes
	@echo "==> Checking Python formatting (Ruff)..."
	uv run ruff format --check .
	@echo "==> Checking TypeScript formatting (Prettier)..."
	pnpm run format:check

typecheck: ## Run static type assertions (mypy, tsc, go vet)
	@echo "==> Typechecking TypeScript packages..."
	pnpm turbo run typecheck
	@echo "==> Typechecking Python services (mypy)..."
	uv run mypy services/nexus-api

test: ## Execute unit and contract test suites
	@echo "==> Running TypeScript & Contract tests..."
	pnpm turbo run test
	@echo "==> Running Python unit tests..."
	uv run pytest services/nexus-api/tests
	@echo "==> Running Go unit tests..."
	cd services/nexus-worker-go && go test -v ./...

audit-rls: ## Audit Django models for PostgreSQL 16 Forced RLS coverage
	@echo "==> Auditing Forced RLS policy coverage on all models..."
	python ops/audits/audit_rls_coverage.py

audit-budget: ## Audit codebase files against structural budget ceilings
	@echo "==> Auditing structural code ceilings and cyclomatic complexity..."
	python ops/audits/audit_code_budget.py

branch-check: ## Audit active Git branch against 4-tier naming taxonomy
	@echo "==> Auditing Git branch naming taxonomy..."
	python ops/ci/branch_check.py

db-up: ## Start local database, cache, and messaging infrastructure
	@echo "==> Launching PostgreSQL 16, PgBouncer, Redis, MinIO, and Mailhog..."
	docker compose -f infra/docker/docker-compose.dev.yml up -d

db-down: ## Stop local database infrastructure
	docker compose -f infra/docker/docker-compose.dev.yml down

clean: ## Purge build artifacts, virtualenvs, and dependency caches
	@echo "==> Cleaning cache and build directories..."
	rm -rf .turbo node_modules services/nexus-api/.venv target dist .mypy_cache .ruff_cache
	@echo "==> Clean complete."
