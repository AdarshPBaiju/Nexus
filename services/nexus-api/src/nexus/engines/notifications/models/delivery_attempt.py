"""
nexus.engines.notifications.models.delivery_attempt - Partitioned Delivery Ledger.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class NotificationDeliveryAttempt(TenantScopedModel):
    """
    Immutable delivery ledger tracking each dispatch attempt, provider, status, and cost.
    """

    class Status(models.TextChoices):
        QUEUED = "QUEUED", _("Queued for Dispatch")
        SENDING = "SENDING", _("In Flight with Provider")
        SENT = "SENT", _("Accepted by Provider")
        DELIVERED = "DELIVERED", _("Confirmed Delivered to Handset")
        READ = "READ", _("Message Opened or Read")
        BOUNCED = "BOUNCED", _("Hard or Soft Bounced")
        FAILED = "FAILED", _("Terminal Provider Failure")

    intent_id = models.UUIDField(
        db_index=True,
        help_text=_("UUID of the parent NotificationIntentDTO."),
    )
    recipient_destination = models.CharField(
        max_length=256,
        help_text=_("Destination address used for this attempt (email, phone, token)."),
    )
    channel = models.CharField(
        max_length=16,
        db_index=True,
        help_text=_("Channel code for this attempt (PUSH, WHATSAPP, SMS, EMAIL)."),
    )
    provider_code = models.CharField(
        max_length=32,
        db_index=True,
        help_text=_("Provider adapter code (e.g. FCM_HTTPV1, META_WHATSAPP, RESEND)."),
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.QUEUED,
        db_index=True,
        help_text=_("Current delivery status state machine value."),
    )
    cost_cents = models.IntegerField(
        default=0,
        help_text=_("Actual billed or estimated provider transit cost in micro-cents."),
    )
    error_code = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text=_("Normalized provider error code on failure."),
    )
    idempotency_key = models.CharField(
        max_length=128,
        db_index=True,
        help_text=_("Deterministic hash preventing duplicate paid dispatches."),
    )

    class Meta:
        app_label = "notifications"
        db_table = "notif_delivery_attempt"
        unique_together = [("tenant_id", "idempotency_key")]
        ordering = ["-created_at", "id"]

    def __str__(self) -> str:
        return f"Attempt({self.intent_id} [{self.channel}:{self.provider_code}]: {self.status})"
