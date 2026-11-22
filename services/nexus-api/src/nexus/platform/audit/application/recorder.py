"""
nexus.platform.audit.application.recorder - Forensic audit recorders.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from nexus.libs.db.audit_context import get_current_audit_context
from nexus.platform.audit.domain.hash_chain import HashChainEngine
from nexus.platform.audit.domain.redaction import PiiRedactionDiffEngine
from nexus.platform.audit.models.audit_event import (
    AuditDataAccessLog,
    AuditDomainEventLog,
)


@dataclass(frozen=True)
class AuditEventIntent:
    """Parameters for recording a domain audit event."""

    category: str
    event_type: str
    target_entity_type: str
    target_entity_id: str
    before_state: Mapping[str, Any] = field(default_factory=dict)
    after_state: Mapping[str, Any] = field(default_factory=dict)
    severity: str = "INFO"
    outcome: str = "SUCCESS"
    actor_id: Optional[uuid.UUID] = None
    supervisor_id: Optional[uuid.UUID] = None


class ForensicAuditService:
    """Synchronous in-transaction recording service for Tier A audit events."""

    @classmethod
    def record_event(
        cls,
        tenant_id: uuid.UUID,
        intent: AuditEventIntent,
    ) -> AuditDomainEventLog:
        """Record domain event with PII redaction and cryptographic hash chaining."""
        before = dict(intent.before_state)
        after = dict(intent.after_state)
        changed_fields, _ = PiiRedactionDiffEngine.compute_diff(before, after)

        actor_id, sup_id, actor_type = cls._resolve_actors(intent)
        prev_hash = cls._get_latest_cumulative_hash(tenant_id)

        payload = cls._build_canonical_payload(
            tenant_id, intent, (actor_id, sup_id), changed_fields
        )
        entry_sha256 = HashChainEngine.compute_entry_sha256(payload)
        cumulative_hash = HashChainEngine.compute_chained_hash(prev_hash, entry_sha256)

        return AuditDomainEventLog.objects.create(
            tenant_id=tenant_id,
            category=intent.category,
            event_type=intent.event_type,
            severity=intent.severity,
            outcome=intent.outcome,
            actor_id=actor_id,
            actor_type=actor_type,
            supervisor_id=sup_id,
            target_entity_type=intent.target_entity_type,
            target_entity_id=intent.target_entity_id,
            before_state=PiiRedactionDiffEngine.scrub_dict(before),
            after_state=PiiRedactionDiffEngine.scrub_dict(after),
            changed_fields=changed_fields,
            entry_sha256=entry_sha256,
            prev_hash=prev_hash,
            cumulative_hash=cumulative_hash,
        )

    @staticmethod
    def _resolve_actors(
        intent: AuditEventIntent,
    ) -> tuple[uuid.UUID, Optional[uuid.UUID], str]:
        audit_ctx = get_current_audit_context()
        actor_id = intent.actor_id or (audit_ctx.actor_id if audit_ctx else uuid.uuid4())
        sup_id = intent.supervisor_id or (audit_ctx.supervisor_id if audit_ctx else None)
        actor_type = audit_ctx.actor_type if audit_ctx else "STAFF"
        return actor_id, sup_id, actor_type

    @staticmethod
    def _build_canonical_payload(
        tenant_id: uuid.UUID,
        intent: AuditEventIntent,
        actors: tuple[uuid.UUID, Optional[uuid.UUID]],
        changed_fields: dict[str, Any],
    ) -> dict[str, Any]:
        actor_id, sup_id = actors
        return {
            "tenant_id": str(tenant_id),
            "category": intent.category,
            "event_type": intent.event_type,
            "actor_id": str(actor_id),
            "supervisor_id": str(sup_id) if sup_id else None,
            "target_entity_type": intent.target_entity_type,
            "target_entity_id": intent.target_entity_id,
            "changed_fields": changed_fields,
            "outcome": intent.outcome,
        }

    @classmethod
    def _get_latest_cumulative_hash(cls, tenant_id: uuid.UUID) -> str:
        latest = (
            AuditDomainEventLog.objects.filter(tenant_id=tenant_id)
            .order_by("-created_at", "-id")
            .first()
        )
        return latest.cumulative_hash if latest else HashChainEngine.GENESIS_HASH


class DataAccessAuditService:
    """Service for recording sensitive read access and export downloads (Tier C)."""

    @staticmethod
    def record_pii_access(
        tenant_id: uuid.UUID,
        target_entity: str,
        accessed_fields: list[str],
        actor_id: uuid.UUID,
    ) -> AuditDataAccessLog:
        return AuditDataAccessLog.objects.create(
            tenant_id=tenant_id,
            access_type="PII_UNMASK",
            target_entity=target_entity,
            accessed_fields=accessed_fields,
            row_count=1,
            actor_id=actor_id,
        )

    @staticmethod
    def record_export_download(
        tenant_id: uuid.UUID,
        target_entity: str,
        export_sha256: str,
        actor_id: uuid.UUID,
    ) -> AuditDataAccessLog:
        return AuditDataAccessLog.objects.create(
            tenant_id=tenant_id,
            access_type="EXPORT_DOWNLOAD",
            target_entity=target_entity,
            accessed_fields=[],
            row_count=1,
            export_artifact_sha256=export_sha256,
            actor_id=actor_id,
        )
