"""
nexus.platform.audit.models.audit_event - Core audit event models (Tiers A, B, C).
"""

from __future__ import annotations

from django.db import models

from nexus.libs.models import TenantScopedModel


class AuditDomainEventLog(TenantScopedModel):
    """
    Tier A: Synchronous, in-transaction business & security domain audit events.
    Captures actor, supervisor dual attribution, and cryptographic hash chain.
    """

    class Severity(models.TextChoices):
        INFO = "INFO", "Info"
        WARNING = "WARNING", "Warning"
        CRITICAL = "CRITICAL", "Critical"

    class Outcome(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        DENIED = "DENIED", "Denied"
        FAILED = "FAILED", "Failed"

    category = models.CharField(max_length=64, db_index=True)
    event_type = models.CharField(max_length=128, db_index=True)
    severity = models.CharField(max_length=16, choices=Severity.choices, default=Severity.INFO)
    outcome = models.CharField(max_length=16, choices=Outcome.choices, default=Outcome.SUCCESS)

    actor_id = models.UUIDField(db_index=True)
    actor_type = models.CharField(max_length=32, default="STAFF")
    supervisor_id = models.UUIDField(null=True, blank=True)

    target_entity_type = models.CharField(max_length=64, db_index=True)
    target_entity_id = models.CharField(max_length=128, db_index=True)

    before_state = models.JSONField(default=dict, blank=True)
    after_state = models.JSONField(default=dict, blank=True)
    changed_fields = models.JSONField(default=dict, blank=True)

    entry_sha256 = models.CharField(max_length=64)
    prev_hash = models.CharField(max_length=64, default="0" * 64)
    cumulative_hash = models.CharField(max_length=64, db_index=True)

    class Meta:
        db_table = "audit_domain_event_log"
        ordering = ["created_at", "id"]


class AuditDbRowChangeLog(TenantScopedModel):
    """
    Tier B: Low-level CDC row-change log capturing trigger diffs.
    """

    table_name = models.CharField(max_length=128, db_index=True)
    db_operation = models.CharField(max_length=16)  # INSERT, UPDATE, DELETE
    row_id = models.CharField(max_length=128, db_index=True)

    changed_columns = models.JSONField(default=list)
    before_state = models.JSONField(default=dict, blank=True)
    after_state = models.JSONField(default=dict, blank=True)

    actor_id = models.UUIDField(null=True, blank=True)
    actor_type = models.CharField(max_length=32, default="STAFF")
    db_session_user = models.CharField(max_length=64, default="nexus_app_rw")
    txid = models.BigIntegerField(default=0)

    entry_sha256 = models.CharField(max_length=64)

    class Meta:
        db_table = "audit_db_row_change_log"
        ordering = ["created_at", "id"]


class AuditDataAccessLog(TenantScopedModel):
    """
    Tier C: Read audit tracking sensitive PII reveals and batch export downloads.
    """

    access_type = models.CharField(max_length=32)  # PII_UNMASK, EXPORT_DOWNLOAD
    target_entity = models.CharField(max_length=64)
    accessed_fields = models.JSONField(default=list)
    row_count = models.IntegerField(default=1)
    export_artifact_sha256 = models.CharField(max_length=64, null=True, blank=True)

    actor_id = models.UUIDField(db_index=True)
    reason = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "audit_data_access_log"
        ordering = ["-created_at"]
