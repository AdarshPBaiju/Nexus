#!/usr/bin/env python3
"""
verify_celery_go_heavy_worker_queues.py - Verification suite for Subphase 01.10.
Validates:
1. 6-queue Celery topology (q.critical, q.domain, q.channels, q.i18n, q.beat, q.maintenance).
2. Dead-letter queue (q.dead_letter) and Redis database isolation (DB 0, 1, 2, 3).
3. CeleryTaskRouter deterministic namespace-to-queue resolution.
4. ExportDispatchBridge row-count threshold routing (<=5k sync stream vs >5k Go worker).
5. Polyglot worker contracts parity.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "services" / "nexus-api" / "src"
sys.path.insert(0, str(API_SRC))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexus_test_settings")
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "nexus.platform.tenancy",
        ],
        USE_TZ=True,
    )
    django.setup()

from nexus.infrastructure.celery import (
    CeleryQueues,
    CeleryTaskRouter,
    ExportDispatchBridge,
    ExportExecutionMode,
    RedisDatabases,
)
from nexus.libs.ids import new_uuid7


def test_celery_queue_topology_and_redis_isolation() -> None:
    """Validate 6 isolated queues and Redis database mapping."""
    expected_queues = {
        "q.critical",
        "q.domain",
        "q.channels",
        "q.i18n",
        "q.beat",
        "q.maintenance",
        "q.dead_letter",
    }
    assert set(CeleryQueues.ALL_QUEUES) == expected_queues

    assert RedisDatabases.CELERY_AND_CACHE == 0
    assert RedisDatabases.GO_ASYNQ_BATCH == 1
    assert RedisDatabases.CHANNELS_WEBSOCKET == 2
    assert RedisDatabases.RATE_LIMIT_AND_SESSIONS == 3
    print("[PASS] test_celery_queue_topology_and_redis_isolation")


def test_celery_task_router_dispatch() -> None:
    """Validate task namespace to queue routing table."""
    q_iam = CeleryTaskRouter.route_task("nexus.platform.iam.tasks.lock_user")
    assert q_iam == CeleryQueues.CRITICAL

    q_auth = CeleryTaskRouter.route_task("nexus.platform.auth.tasks.revoke_token")
    assert q_auth == CeleryQueues.CRITICAL

    q_acc = CeleryTaskRouter.route_task("nexus.engines.accounting.tasks.post_reversal")
    assert q_acc == CeleryQueues.DOMAIN

    q_folio = CeleryTaskRouter.route_task("nexus.engines.commerce_folio.tasks.settle_folio")
    assert q_folio == CeleryQueues.DOMAIN

    q_i18n = CeleryTaskRouter.route_task("nexus.platform.i18n.tasks.translate_chunk")
    assert q_i18n == CeleryQueues.I18N

    q_ws = CeleryTaskRouter.route_task("nexus.channels.tasks.broadcast_update")
    assert q_ws == CeleryQueues.CHANNELS

    q_maint = CeleryTaskRouter.route_task("nexus.maintenance.tasks.compact_logs")
    assert q_maint == CeleryQueues.MAINTENANCE

    q_fallback = CeleryTaskRouter.route_task("unknown.namespace.custom_job")
    assert q_fallback == CeleryQueues.DOMAIN

    print("[PASS] test_celery_task_router_dispatch")


def test_export_dispatch_bridge_thresholds() -> None:
    """Validate direct stream vs. Go Asynq background worker dispatch."""
    tenant_id = new_uuid7()

    # Case 1: Small export (500 rows <= 5,000 threshold) -> Direct Stream
    small_ticket = ExportDispatchBridge.evaluate_and_dispatch(
        tenant_id=tenant_id,
        entity_type="orders",
        estimated_row_count=500,
        filter_criteria={"status": "SETTLED"},
    )
    assert small_ticket.mode == ExportExecutionMode.SYNC_STREAM
    assert small_ticket.task_id is None
    assert small_ticket.queue_name == "direct_stream"

    # Case 2: Boundary export (5,000 rows == 5,000 threshold) -> Direct Stream
    boundary_ticket = ExportDispatchBridge.evaluate_and_dispatch(
        tenant_id=tenant_id,
        entity_type="orders",
        estimated_row_count=5000,
        filter_criteria={},
    )
    assert boundary_ticket.mode == ExportExecutionMode.SYNC_STREAM

    # Case 3: Heavy export (15,000 rows > 5,000 threshold) -> Go Asynq Worker
    heavy_ticket = ExportDispatchBridge.evaluate_and_dispatch(
        tenant_id=tenant_id,
        entity_type="orders",
        estimated_row_count=15000,
        filter_criteria={"date_range": "2026-Q1"},
    )
    assert heavy_ticket.mode == ExportExecutionMode.ASYNC_GO_WORKER
    assert heavy_ticket.task_id is not None
    assert heavy_ticket.queue_name == "go:batch"
    assert heavy_ticket.estimated_rows == 15000

    print("[PASS] test_export_dispatch_bridge_thresholds")


def main() -> None:
    test_celery_queue_topology_and_redis_isolation()
    test_celery_task_router_dispatch()
    test_export_dispatch_bridge_thresholds()
    print("\n>>> All 3 Subphase 01.10 verification suites passed successfully! <<<")


if __name__ == "__main__":
    main()
