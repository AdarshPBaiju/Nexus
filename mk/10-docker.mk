# mk/10-docker.mk — Docker infrastructure and Buildx Bake targets
.PHONY: docker-build docker-bake docker-up docker-down

docker-build: ## Build containers with local Dockerfile context
	@echo "==> Building services via docker compose..."
	$(DOCKER_COMPOSE) build

docker-bake: ## Build multi-arch pinned containers via Buildx Bake
	@echo "==> Executing Buildx Bake multi-arch compilation..."
	docker buildx bake -f infra/docker/docker-bake.hcl

docker-up: ## Start full dev stack in background
	@echo "==> Starting local infrastructure stack..."
	$(DOCKER_COMPOSE) up -d

docker-down: ## Stop all local containers
	@echo "==> Tearing down local infrastructure stack..."
	$(DOCKER_COMPOSE) down
