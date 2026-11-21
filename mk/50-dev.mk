# mk/50-dev.mk — Development environment lifecycle
.PHONY: dev-api dev-web dev-desktop clean

dev-api: ## Start Django ASGI API server
	@echo "==> Starting Django API service (uvicorn)..."
	uv run uvicorn nexus.asgi:application --reload --port 8000

dev-web: ## Start Next.js web application
	@echo "==> Starting Next.js App Router (port 3000)..."
	pnpm --filter @nexus/web run dev

dev-desktop: ## Start Tauri desktop client in development mode
	@echo "==> Launching Tauri desktop shell..."
	pnpm --filter @nexus/desktop run tauri dev
