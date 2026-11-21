# mk/20-database.mk — Database migrations, RLS, and PgBouncer targets
.PHONY: db-migrate db-shell pgbouncer-reload

db-migrate: ## Execute zero-downtime Django migrations
	@echo "==> Running database migrations..."
	uv run python services/nexus-api/manage.py migrate

db-shell: ## Open PostgreSQL psql interactive console
	@echo "==> Connecting to PostgreSQL 16..."
	docker exec -it nexus-postgres psql -U postgres -d nexus_dev

pgbouncer-reload: ## Reload PgBouncer configuration without dropping connections
	@echo "==> Reloading PgBouncer connection pool..."
	docker exec nexus-pgbouncer pkill -HUP pgbouncer
