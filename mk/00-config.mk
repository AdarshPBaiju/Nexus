# mk/00-config.mk — Environment and toolchain configuration
SHELL := /bin/bash
.DEFAULT_GOAL := help

PYTHON_BIN ?= uv run python
PNPM_BIN ?= pnpm
GO_BIN ?= go
CARGO_BIN ?= cargo

DOCKER_COMPOSE ?= docker compose -f infra/docker/docker-compose.dev.yml
