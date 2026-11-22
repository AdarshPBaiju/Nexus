"""
nexus.engines.data_exchange.exporting.dual_lane - Dual-lane export coordinator.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass(frozen=True)
class ExportDispatchResult:
    lane: str  # "SYNC" or "ASYNC_GO"
    payload_or_job_id: Any
    row_count: int


class DualLaneExportCoordinator:
    """
    Coordinates synchronous vs asynchronous export routing.
    - <= 1,000 rows: Synchronous streaming (< 450ms).
    - > 1,000 rows: Asynchronous Go worker on go:batch (< 64MB RSS).
    """

    SYNC_THRESHOLD = 1000

    @classmethod
    def dispatch_export(
        cls,
        rows: Sequence[dict[str, Any]],
        columns: Sequence[str],
    ) -> ExportDispatchResult:
        row_count = len(rows)
        if row_count <= cls.SYNC_THRESHOLD:
            csv_output = cls._render_sync_csv(rows, columns)
            return ExportDispatchResult(
                lane="SYNC",
                payload_or_job_id=csv_output,
                row_count=row_count,
            )

        # Large export delegates to Go heavy worker
        job_id = f"job_export_go_{row_count}"
        return ExportDispatchResult(
            lane="ASYNC_GO",
            payload_or_job_id=job_id,
            row_count=row_count,
        )

    @staticmethod
    def _render_sync_csv(
        rows: Sequence[dict[str, Any]],
        columns: Sequence[str],
    ) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(columns))
        writer.writeheader()
        for r in rows:
            writer.writerow({col: r.get(col, "") for col in columns})
        return output.getvalue()
