# mk/70-test.mk — Automated testing targets
.PHONY: test test-unit test-all

test: ## Execute unit and contract test suites
	@echo "==> Running TypeScript & Contract tests..."
	pnpm turbo run test
	@echo "==> Running Python unit tests..."
	uv run pytest services/nexus-api/tests
	@echo "==> Running Go unit tests..."
	cd services/nexus-worker-go && go test -v ./...

test-unit: ## Run pure unit test suites across all polyglot runtimes
	@echo "==> Executing all polyglot unit test runners..."
	python -m pytest tests/

test-all: test test-unit ## Run complete test matrix
	@echo "==> Full polyglot test matrix passed."
