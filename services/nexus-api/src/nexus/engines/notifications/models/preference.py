"""
nexus.engines.notifications.models.preference - User Notification Preferences & Quiet Hours.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class NotificationUserPreference(TenantScopedModel):
    """
    Per-user channel opt-in/opt-out matrix and quiet hour preferences.
    """

    user_id = models.UUIDField(
        db_index=True,
        help_text=_("Target identity or customer UUID."),
    )
    channel_matrix = models.JSONField(
        default=dict,
        help_text=_("Channel enabled map, e.g. {'EMAIL': true, 'SMS': false}."),
    )
    quiet_hours_enabled = models.BooleanField(
        default=False,
        help_text=_("Whether quiet hours suppression is enabled for non-critical alerts."),
    )
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        help_text=_("Start time of quiet period in user local time (e.g. 22:00)."),
    )
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        help_text=_("End time of quiet period in user local time (e.g. 08:00)."),
    )
    timezone = models.CharField(
        max_length=64,
        default="UTC",
        help_text=_("IANA timezone identifier (e.g. 'Asia/Kolkata')."),
    )

    class Meta:
        app_label = "notifications"
        db_table = "notif_user_preference"
        unique_together = [("tenant_id", "user_id")]
        ordering = ["user_id", "id"]

    def is_channel_enabled(self, channel: str) -> bool:
        """Returns True if the channel is not explicitly disabled by the user."""
        return self.channel_matrix.get(channel.upper(), True)

    def __str__(self) -> str:
        return f"Preference(user={self.user_id}, quiet={self.quiet_hours_enabled})"
