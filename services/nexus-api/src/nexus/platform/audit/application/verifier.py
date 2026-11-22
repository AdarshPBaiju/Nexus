"""
nexus.platform.audit.application.verifier - Cryptographic hash chain verification.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

from nexus.platform.audit.domain.hash_chain import HashChainEngine
from nexus.platform.audit.models.audit_event import AuditDomainEventLog


@dataclass(frozen=True)
class VerificationResult:
    is_valid: bool
    verified_count: int
    last_cumulative_hash: str
    tampered_event_id: Optional[uuid.UUID] = None
    tamper_reason: Optional[str] = None


class HashChainVerifier:
    """Verifies chronological mathematical continuity of audit event chain."""

    @classmethod
    def verify_tenant_chain(cls, tenant_id: uuid.UUID) -> VerificationResult:
        events = list(
            AuditDomainEventLog.objects.filter(tenant_id=tenant_id).order_by("created_at", "id")
        )
        if not events:
            return VerificationResult(
                is_valid=True,
                verified_count=0,
                last_cumulative_hash=HashChainEngine.GENESIS_HASH,
            )

        expected_prev = HashChainEngine.GENESIS_HASH
        for event in events:
            is_valid, err_msg, next_prev = cls._validate_single_event(event, expected_prev)
            if not is_valid:
                return VerificationResult(
                    is_valid=False,
                    verified_count=0,
                    last_cumulative_hash=expected_prev,
                    tampered_event_id=event.id,
                    tamper_reason=err_msg,
                )
            expected_prev = next_prev

        return VerificationResult(
            is_valid=True,
            verified_count=len(events),
            last_cumulative_hash=expected_prev,
        )

    @classmethod
    def _validate_single_event(
        cls, event: AuditDomainEventLog, expected_prev: str
    ) -> tuple[bool, Optional[str], str]:
        if event.prev_hash != expected_prev:
            return False, f"Previous hash mismatch: expected {expected_prev}", expected_prev

        payload = cls._extract_payload(event)
        computed_entry_sha = HashChainEngine.compute_entry_sha256(payload)
        if computed_entry_sha != event.entry_sha256:
            return False, f"Payload altered: expected {computed_entry_sha}", expected_prev

        computed_cumulative = HashChainEngine.compute_chained_hash(
            expected_prev, computed_entry_sha
        )
        if computed_cumulative != event.cumulative_hash:
            return False, f"Cumulative mismatch: expected {computed_cumulative}", expected_prev

        return True, None, computed_cumulative

    @staticmethod
    def _extract_payload(event: AuditDomainEventLog) -> dict[str, object]:
        return {
            "tenant_id": str(event.tenant_id),
            "category": event.category,
            "event_type": event.event_type,
            "actor_id": str(event.actor_id),
            "supervisor_id": str(event.supervisor_id) if event.supervisor_id else None,
            "target_entity_type": event.target_entity_type,
            "target_entity_id": event.target_entity_id,
            "changed_fields": event.changed_fields,
            "outcome": event.outcome,
        }
