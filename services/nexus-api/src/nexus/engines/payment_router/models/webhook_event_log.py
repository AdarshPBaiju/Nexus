"""
nexus.engines.payment_router.models.webhook_event_log - Payment Webhook Event Log Model.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Self

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


@dataclass(frozen=True)
class LogWebhookEventDto:
    """Parameter object for logging an inbound payment processor webhook."""

    tenant_id: uuid.UUID
    installation_id: uuid.UUID
    provider_event_id: str
    event_type: str
    payload: dict[str, Any] | None = None


class PaymentWebhookEventLog(TenantScopedModel):
    """
    Idempotent audit log for inbound payment provider webhook events (Stripe, Razorpay, NPCI).
    """

    gateway_installation = models.ForeignKey(
        "payment_router.GatewayInstallation",
        on_delete=models.CASCADE,
        related_name="webhook_logs",
        help_text=_("Associated payment gateway installation."),
    )
    provider_event_id = models.CharField(
        max_length=128,
        db_index=True,
        help_text=_("Idempotent unique event identifier supplied by payment processor."),
    )
    event_type = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Processor event type (e.g. payment_intent.succeeded, order.paid)."),
    )
    payload_json = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Raw JSON event payload delivered by processor."),
    )
    processed_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text=_("Ingestion and deduplication timestamp."),
    )

    class Meta:
        app_label = "payment_router"
        db_table = "pay_webhook_event_log"
        ordering = ["-processed_at"]
        indexes = [
            models.Index(fields=["tenant_id", "provider_event_id"]),
        ]
        unique_together = ("tenant_id", "gateway_installation_id", "provider_event_id")

    @classmethod
    def record_event(cls, dto: LogWebhookEventDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            gateway_installation_id=dto.installation_id,
            provider_event_id=dto.provider_event_id,
            event_type=dto.event_type,
            payload_json=dto.payload or {},
            processed_at=timezone.now(),
        )

    def __str__(self) -> str:
        return f"PaymentWebhookEventLog({self.provider_event_id}, type={self.event_type})"
