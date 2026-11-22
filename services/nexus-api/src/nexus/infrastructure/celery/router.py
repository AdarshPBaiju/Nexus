"""
nexus.infrastructure.celery.router - Deterministic Multi-Queue Task Router.
"""

from __future__ import annotations

from typing import Any

from nexus.infrastructure.celery.config import CeleryQueues


class CeleryTaskRouter:
    """
    Routes Celery tasks to dedicated priority queues based on namespace prefix.
    """

    ROUTING_MAP = {
        "nexus.platform.iam": CeleryQueues.CRITICAL,
        "nexus.platform.auth": CeleryQueues.CRITICAL,
        "nexus.engines.accounting": CeleryQueues.DOMAIN,
        "nexus.engines.commerce_folio": CeleryQueues.DOMAIN,
        "nexus.engines.resource_scheduler": CeleryQueues.DOMAIN,
        "nexus.platform.i18n": CeleryQueues.I18N,
        "nexus.channels": CeleryQueues.CHANNELS,
        "nexus.maintenance": CeleryQueues.MAINTENANCE,
    }

    @classmethod
    def route_task(
        cls,
        task_name: str,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> str:
        """Determines target queue name for a given task function."""
        for prefix, queue in cls.ROUTING_MAP.items():
            if task_name.startswith(prefix):
                return queue
        return CeleryQueues.DOMAIN
