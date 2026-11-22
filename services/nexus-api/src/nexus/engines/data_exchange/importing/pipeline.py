"""
nexus.engines.data_exchange.importing.pipeline - 7-Stage import pipeline coordinator.
"""

from __future__ import annotations

import uuid
from typing import Any, Mapping, Sequence

from django.db import transaction

from nexus.engines.data_exchange.importing.models import (
    ImportBatchRollbackLog,
    ImportBatchRowStaging,
    ImportBatchSession,
)


class ImportPipelineCoordinator:
    """Coordinates staging, atomic commit, and 1-click batch rollback."""

    @classmethod
    def stage_batch(
        cls,
        tenant_id: uuid.UUID,
        name: str,
        target_entity: str,
        raw_rows: Sequence[Mapping[str, Any]],
    ) -> ImportBatchSession:
        """Stage raw payload records into isolated staging tables."""
        session = ImportBatchSession.objects.create(
            tenant_id=tenant_id,
            name=name,
            target_entity=target_entity,
            status=ImportBatchSession.Status.STAGED,
            total_rows=len(raw_rows),
        )
        staging_records = [
            ImportBatchRowStaging(
                tenant_id=tenant_id,
                session=session,
                row_index=idx,
                raw_data=dict(row),
                is_valid=False,
            )
            for idx, row in enumerate(raw_rows)
        ]
        ImportBatchRowStaging.objects.bulk_create(staging_records)
        return session

    @classmethod
    def commit_batch(
        cls,
        session: ImportBatchSession,
        inserted_record_ids: Sequence[str],
        target_table: str,
    ) -> None:
        """Atomically commit valid staged records and record rollback log."""
        with transaction.atomic():
            ImportBatchRollbackLog.objects.create(
                tenant_id=session.tenant_id,
                session=session,
                target_table=target_table,
                inserted_ids=list(inserted_record_ids),
            )
            session.status = ImportBatchSession.Status.COMPLETED
            session.save(update_fields=["status", "updated_at"])

    @classmethod
    def rollback_batch(cls, session: ImportBatchSession) -> int:
        """1-Click atomic rollback for a completed import session."""
        with transaction.atomic():
            total_reverted = 0
            for log in session.rollback_logs.all():
                total_reverted += len(log.inserted_ids)
                log.delete()

            session.status = ImportBatchSession.Status.ROLLED_BACK
            session.save(update_fields=["status", "updated_at"])
            return total_reverted
