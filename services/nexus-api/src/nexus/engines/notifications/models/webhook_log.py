"""
nexus.engines.notifications.models.webhook_log - Inbound DLR Webhook Ingestion Log.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class InboundWebhookLog(TenantScopedModel):
    """
    Forensic log of inbound delivery receipts (DLR) and webhook events from external providers.
    """

    provider_code = models.CharField(
        max_length=32,
        db_index=True,
        help_text=_("Provider origin code (e.g. TWILIO, RESEND, META)."),
    )
    event_type = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Provider native event type (e.g. message.delivered, email.bounced)."),
    )
    raw_payload = models.JSONField(
        default=dict,
        help_text=_("Full raw JSON payload received on webhook endpoint."),
    )
    signature_verified = models.BooleanField(
        default=False,
        help_text=_("Whether cryptographic HMAC / asymmetric signature passed verification."),
    )

    class Meta:
        app_label = "notifications"
        db_table = "notif_inbound_webhook_log"
        ordering = ["-created_at", "id"]

    def __str__(self) -> str:
        return f"WebhookLog({self.provider_code}:{self.event_type} [verified={self.signature_verified}])"
