"""
nexus.engines.notifications.models.suppression - Destination Suppression & Bounce Registry.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class NotificationSuppression(TenantScopedModel):
    """
    Hard bounce, spam complaint, and unsubscribe suppression registry preventing illegal re-sends.
    """

    class Reason(models.TextChoices):
        HARD_BOUNCE = "HARD_BOUNCE", _("Hard Bounce")
        UNSUBSCRIBED = "UNSUBSCRIBED", _("User Unsubscribed")
        COMPLAINT = "COMPLAINT", _("Spam Complaint")
        INVALID_DESTINATION = "INVALID_DESTINATION", _("Invalid Destination Format")

    channel = models.CharField(
        max_length=16,
        db_index=True,
        help_text=_("Channel code (EMAIL, SMS, WHATSAPP, PUSH)."),
    )
    destination = models.CharField(
        max_length=256,
        db_index=True,
        help_text=_("Normalized destination target (email address, E.164 phone number)."),
    )
    reason = models.CharField(
        max_length=32,
        choices=Reason.choices,
        default=Reason.UNSUBSCRIBED,
        db_index=True,
        help_text=_("Statutory or operational reason for suppression."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Whether this suppression entry is actively blocking dispatches."),
    )

    class Meta:
        app_label = "notifications"
        db_table = "notif_suppression_list"
        unique_together = [("tenant_id", "channel", "destination")]
        ordering = ["channel", "destination", "id"]

    def __str__(self) -> str:
        return f"Suppression({self.channel}:{self.destination} [{self.reason}])"
