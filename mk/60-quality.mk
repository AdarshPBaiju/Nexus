# mk/60-quality.mk — Code quality, boundaries, and budget auditing
.PHONY: lint lint-fix format format-check audit-rls audit-budget branch-check

lint: ## Run polyglot linters (Ruff, ESLint, Go vet)
	@echo "==> Running Ruff lint check (Python)..."
	uv run ruff check .
	@echo "==> Running Turborepo lint (TypeScript)..."
	pnpm turbo run lint

lint-fix: ## Auto-fix safe lint violations
	@echo "==> Auto-fixing Python violations (Ruff)..."
	uv run ruff check --fix .
	@echo "==> Auto-fixing TypeScript violations..."
	pnpm turbo run lint:fix

format: ## Format Python and TypeScript codebase
	@echo "==> Formatting Python files (Ruff)..."
	uv run ruff format .
	@echo "==> Formatting TypeScript/JSON files (Prettier)..."
	pnpm run format

format-check: ## Assert zero unformatted files
	@echo "==> Checking Python formatting (Ruff)..."
	uv run ruff format --check .
	@echo "==> Checking TypeScript formatting..."
	pnpm run format:check

audit-rls: ## Audit Forced RLS coverage
	python ops/audits/audit_rls_coverage.py

audit-budget: ## Audit structural code ceilings
	python ops/audits/audit_code_budget.py

branch-check: ## Audit active Git branch name against 4-tier taxonomy
	python ops/ci/branch_check.py
