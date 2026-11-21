# Project Nexus Polyglot Monorepo Makefile
# Modular architecture: includes mk/*.mk domain definitions

include mk/00-config.mk
include mk/10-docker.mk
include mk/20-database.mk
include mk/40-workers.mk
include mk/50-dev.mk
include mk/60-quality.mk
include mk/70-test.mk

help: ## Display available make targets
	@echo "Project Nexus Monorepo Toolchain Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

clean: ## Purge build artifacts, virtualenvs, and dependency caches
	@echo "==> Cleaning cache and build directories..."
	rm -rf .turbo node_modules services/nexus-api/.venv target dist .mypy_cache .ruff_cache
	@echo "==> Clean complete."
