"""
nexus.engines.notifications.models.in_app - In-App Notification Center Record.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class InAppNotification(TenantScopedModel):
    """
    In-app notification delivered to user workspace bell center.
    """

    recipient_id = models.UUIDField(
        db_index=True,
        help_text=_("Recipient identity or staff user UUID."),
    )
    title = models.CharField(
        max_length=256,
        help_text=_("Notification title header."),
    )
    body = models.TextField(
        help_text=_("Notification body copy."),
    )
    category = models.CharField(
        max_length=32,
        default="SYSTEM",
        db_index=True,
        help_text=_("Category filter (ALL, ORDERS, SYSTEM, ALERTS)."),
    )
    action_url = models.CharField(
        max_length=512,
        blank=True,
        default="",
        help_text=_("Optional deep link URL when user clicks notification."),
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Read status flag."),
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp when user marked notification as read."),
    )

    class Meta:
        app_label = "notifications"
        db_table = "notif_in_app"
        ordering = ["-created_at", "id"]

    def __str__(self) -> str:
        return f"InAppNotif({self.recipient_id}: {self.title} [read={self.is_read}])"
