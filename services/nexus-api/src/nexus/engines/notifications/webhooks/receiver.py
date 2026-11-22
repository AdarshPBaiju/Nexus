"""
nexus.engines.notifications.webhooks.receiver - Inbound DLR Webhook Ingestion Engine.
"""
from __future__ import annotations

import hashlib
import hmac
import uuid
from dataclasses import dataclass
from typing import Any

from nexus.engines.notifications.models import (
    InboundWebhookLog,
    NotificationDeliveryAttempt,
    NotificationSuppression,
)


@dataclass(frozen=True)
class WebhookDlrEnvelope:
    """Envelope wrapping inbound provider webhook payload and cryptographic signature."""

    tenant_id: uuid.UUID
    provider_code: str
    payload: dict[str, Any]
    signature: str = ""
    secret: str = ""


class WebhookReceiver:
    """
    Ingests and cryptographically verifies inbound delivery receipts (DLR) from external providers.
    """

    @classmethod
    def process_dlr(cls, envelope: WebhookDlrEnvelope) -> bool:
        """Processes inbound DLR event, records log, and updates attempt status."""
        verified = cls._verify_signature(envelope.payload, envelope.signature, envelope.secret)
        InboundWebhookLog.objects.create(
            tenant_id=envelope.tenant_id,
            provider_code=envelope.provider_code,
            event_type=envelope.payload.get("event", "dlr.unknown"),
            raw_payload=envelope.payload,
            signature_verified=verified,
        )
        if not verified and envelope.secret:
            return False

        cls._update_delivery_status(envelope.tenant_id, envelope.payload)
        return True

    @classmethod
    def _verify_signature(cls, payload: dict[str, Any], signature: str, secret: str) -> bool:
        if not secret:
            return True
        if not signature:
            return False
        expected = hmac.new(
            secret.encode("utf-8"),
            str(payload).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    @classmethod
    def _update_delivery_status(cls, tenant_id: uuid.UUID, payload: dict[str, Any]) -> None:
        attempt_id_str = payload.get("attempt_id")
        if not attempt_id_str:
            return
        try:
            attempt_uuid = uuid.UUID(attempt_id_str)
        except (ValueError, TypeError):
            return

        status_str = payload.get("status", "").upper()
        attempt = NotificationDeliveryAttempt.objects.filter(
            tenant_id=tenant_id,
            id=attempt_uuid,
        ).first()
        if not attempt:
            return

        if status_str == "DELIVERED":
            attempt.status = NotificationDeliveryAttempt.Status.DELIVERED
            attempt.save(update_fields=["status", "updated_at"])
        elif status_str in ("BOUNCED", "FAILED"):
            attempt.status = NotificationDeliveryAttempt.Status.BOUNCED
            attempt.save(update_fields=["status", "updated_at"])
            cls._record_suppression(tenant_id, attempt.channel, attempt.recipient_destination)

    @classmethod
    def _record_suppression(cls, tenant_id: uuid.UUID, channel: str, destination: str) -> None:
        NotificationSuppression.objects.get_or_create(
            tenant_id=tenant_id,
            channel=channel,
            destination=destination,
            defaults={"reason": NotificationSuppression.Reason.HARD_BOUNCE},
        )
