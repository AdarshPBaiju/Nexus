# mk/40-workers.mk — Background workers orchestration
.PHONY: worker-celery worker-go

worker-celery: ## Start Celery worker with 6 multi-queues
	@echo "==> Starting Celery worker (queues: critical, domain, channels, i18n, beat, maintenance)..."
	uv run celery -A nexus worker -l INFO -Q q.critical,q.domain,q.channels,q.i18n,q.maintenance

worker-go: ## Run Go heavy background processor
	@echo "==> Starting Go heavy worker..."
	cd services/nexus-worker-go && go run main.go
