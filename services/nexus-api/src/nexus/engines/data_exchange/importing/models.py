"""
nexus.engines.data_exchange.importing.models - Staging and rollback models for bulk import.
"""

from __future__ import annotations

from django.db import models

from nexus.libs.models import TenantScopedModel


class ImportBatchSession(TenantScopedModel):
    """Tracks a bulk import session lifecycle through 7 ingestion stages."""

    class Status(models.TextChoices):
        STAGED = "STAGED", "Staged"
        VALIDATING = "VALIDATING", "Validating"
        READY = "READY", "Ready"
        COMMITTING = "COMMITTING", "Committing"
        COMPLETED = "COMPLETED", "Completed"
        ROLLED_BACK = "ROLLED_BACK", "Rolled Back"

    name = models.CharField(max_length=128)
    target_entity = models.CharField(max_length=64, db_index=True)
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.STAGED, db_index=True
    )
    total_rows = models.IntegerField(default=0)
    valid_rows = models.IntegerField(default=0)
    error_rows = models.IntegerField(default=0)

    class Meta:
        db_table = "dx_import_batch_session"
        ordering = ["-created_at"]


class ImportBatchRowStaging(TenantScopedModel):
    """Isolated staging row holding raw payloads and dry-run validation results."""

    session = models.ForeignKey(
        ImportBatchSession, on_delete=models.CASCADE, related_name="staged_rows"
    )
    row_index = models.IntegerField()
    raw_data = models.JSONField(default=dict)
    is_valid = models.BooleanField(default=False, db_index=True)
    validation_errors = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "dx_import_batch_row_staging"
        ordering = ["row_index"]
        indexes = [
            models.Index(fields=["tenant_id", "session", "is_valid"]),
        ]


class ImportBatchRollbackLog(TenantScopedModel):
    """Records inserted entity IDs for safe 1-click atomic rollback."""

    session = models.ForeignKey(
        ImportBatchSession, on_delete=models.CASCADE, related_name="rollback_logs"
    )
    target_table = models.CharField(max_length=64)
    inserted_ids = models.JSONField(default=list)

    class Meta:
        db_table = "dx_import_batch_rollback_log"
        ordering = ["-created_at"]
