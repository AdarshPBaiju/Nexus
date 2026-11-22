"""
nexus.engines.notifications.models.push_token - Device Push Registration Token.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class DevicePushToken(TenantScopedModel):
    """
    Device FCM/APNs registration tokens with automatic stale token tracking.
    """

    class Platform(models.TextChoices):
        FCM = "FCM", _("Firebase Cloud Messaging (Android/Web)")
        APNS = "APNS", _("Apple Push Notification Service (iOS/macOS)")
        WEB = "WEB", _("Web Push API (W3C Push API)")

    user_id = models.UUIDField(
        db_index=True,
        help_text=_("Identity or customer user UUID owning this device token."),
    )
    token = models.CharField(
        max_length=512,
        db_index=True,
        help_text=_("Raw FCM registration token or APNs hex token."),
    )
    platform = models.CharField(
        max_length=16,
        choices=Platform.choices,
        default=Platform.FCM,
        help_text=_("Underlying push transport platform."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Active validity flag (disabled on Unregistered / NotRegistered DLRs)."),
    )
    last_seen_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Timestamp when device was last active or verified."),
    )

    class Meta:
        app_label = "notifications"
        db_table = "notif_device_push_token"
        unique_together = [("tenant_id", "token")]
        ordering = ["-last_seen_at", "id"]

    def __str__(self) -> str:
        return f"PushToken(user={self.user_id}, platform={self.platform}, active={self.is_active})"
