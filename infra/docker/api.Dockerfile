# ==============================================================================
# Project Nexus Core API & Celery Worker Dockerfile (PNX-REPO-ARCH-004 §5)
# Runtimes: Python 3.12 | Framework: Django 5.1 / DRF / Celery 5.4 / Channels
# Multi-Stage, Non-Root (UID 10001), Read-Only Root FS Compatible
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Builder Stage: Virtualenv Compilation via uv
# ------------------------------------------------------------------------------
FROM python:3.12-slim-bookworm@sha256:7b55db56dfa99f60f64c6a6f19430e37bc903a4eb586efcf448f72df1ce517f8 AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /build

# Install uv installer
COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /uvx /bin/

# Copy workspace pyproject and dependency manifests
COPY pyproject.toml ./
COPY services/nexus-api/pyproject.toml ./services/nexus-api/

# Build virtual environment with dependencies
RUN uv venv /app/.venv && \
    uv pip install --no-cache-dir -r services/nexus-api/pyproject.toml

# ------------------------------------------------------------------------------
# 2. Runner Stage: Hardened, Non-Root Runtime
# ------------------------------------------------------------------------------
FROM python:3.12-slim-bookworm@sha256:7b55db56dfa99f60f64c6a6f19430e37bc903a4eb586efcf448f72df1ce517f8 AS runner

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PORT=8000

# Install runtime dependencies and PID 1 signal handler
RUN apt-get update && apt-get install -y --no-install-recommends \
    tini \
    libpq5 \
    curl \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create unprivileged non-root user (UID 10001)
RUN groupadd -g 10001 nexus && \
    useradd -u 10001 -g nexus -m -s /bin/false nexus

WORKDIR /app

# Copy virtualenv and application code
COPY --from=builder --chown=nexus:nexus /app/.venv /app/.venv
COPY --chown=nexus:nexus pyproject.toml /app/
COPY --chown=nexus:nexus services/nexus-api /app/services/nexus-api

WORKDIR /app/services/nexus-api

USER 10001:10001

EXPOSE 8000

ENTRYPOINT ["tini", "--"]

CMD ["python", "-m", "gunicorn", "nexus.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
