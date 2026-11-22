"""
nexus.infrastructure.celery.config - 6-Queue Celery Configuration & Redis DB Topology.
"""
from __future__ import annotations

from typing import Final


class CeleryQueues:
    """Canonical 6 dedicated Celery queues with priorities and Dead Letter Queue."""

    CRITICAL: Final[str] = "q.critical"
    DOMAIN: Final[str] = "q.domain"
    CHANNELS: Final[str] = "q.channels"
    I18N: Final[str] = "q.i18n"
    BEAT: Final[str] = "q.beat"
    MAINTENANCE: Final[str] = "q.maintenance"
    DEAD_LETTER: Final[str] = "q.dead_letter"

    ALL_QUEUES: Final[tuple[str, ...]] = (
        CRITICAL,
        DOMAIN,
        CHANNELS,
        I18N,
        BEAT,
        MAINTENANCE,
        DEAD_LETTER,
    )


class RedisDatabases:
    """Redis logical database isolation mapping."""

    CELERY_AND_CACHE: Final[int] = 0
    GO_ASYNQ_BATCH: Final[int] = 1
    CHANNELS_WEBSOCKET: Final[int] = 2
    RATE_LIMIT_AND_SESSIONS: Final[int] = 3
