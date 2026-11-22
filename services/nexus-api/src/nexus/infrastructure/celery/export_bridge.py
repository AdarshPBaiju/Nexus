"""
nexus.infrastructure.celery.export_bridge - Polyglot Heavy Export Dispatch Bridge.
Threshold: <= 5,000 rows streams synchronously; > 5,000 rows dispatches to Go Asynq worker.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any

from nexus.libs.ids import new_uuid7


class ExportExecutionMode(str, Enum):
    SYNC_STREAM = "SYNC_STREAM"
    ASYNC_GO_WORKER = "ASYNC_GO_WORKER"


@dataclass(frozen=True)
class ExportDispatchTicket:
    """Execution dispatch ticket returned to API callers."""

    mode: ExportExecutionMode
    task_id: uuid.UUID | None
    estimated_rows: int
    queue_name: str


class ExportDispatchBridge:
    """
    Decides whether an export is streamed directly or offloaded to Go heavy batch workers.
    """

    HEAVY_EXPORT_THRESHOLD = 5000
    GO_BATCH_QUEUE = "go:batch"

    @classmethod
    def evaluate_and_dispatch(
        cls,
        tenant_id: uuid.UUID,
        entity_type: str,
        estimated_row_count: int,
        filter_criteria: dict[str, Any],
    ) -> ExportDispatchTicket:
        """
        Routes export to direct HTTP stream or Go Asynq background worker.
        """
        if estimated_row_count <= cls.HEAVY_EXPORT_THRESHOLD:
            return ExportDispatchTicket(
                mode=ExportExecutionMode.SYNC_STREAM,
                task_id=None,
                estimated_rows=estimated_row_count,
                queue_name="direct_stream",
            )

        task_id = new_uuid7()
        return ExportDispatchTicket(
            mode=ExportExecutionMode.ASYNC_GO_WORKER,
            task_id=task_id,
            estimated_rows=estimated_row_count,
            queue_name=cls.GO_BATCH_QUEUE,
        )
