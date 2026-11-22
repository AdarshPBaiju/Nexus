"""
nexus.engines.notifications.models.routing_rule - Notification Fallback Routing Rule.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class NotificationRoutingRule(TenantScopedModel):
    """
    Priority-based fallback chains governing omnichannel waterfall routing.
    """

    class Priority(models.TextChoices):
        CRITICAL_AUTH = "CRITICAL_AUTH", _("Critical Auth & Security (Bypasses Quiet Hours)")
        OPERATIONAL = "OPERATIONAL", _("Operational Transactional")
        MARKETING = "MARKETING", _("Marketing & Engagement")

    event_type = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Standard event key (e.g. AUTH_OTP, ORDER_CONFIRMED)."),
    )
    priority = models.CharField(
        max_length=32,
        choices=Priority.choices,
        default=Priority.OPERATIONAL,
        db_index=True,
        help_text=_("Priority tier governing quiet-hour and rate-limit handling."),
    )
    fallback_channels = models.JSONField(
        default=list,
        help_text=_("Ordered list of channels (e.g. ['PUSH', 'WHATSAPP', 'SMS', 'EMAIL'])."),
    )
    timeout_seconds = models.IntegerField(
        default=300,
        help_text=_("Timeout before attempting next waterfall fallback channel."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Whether this routing rule is actively evaluated."),
    )

    class Meta:
        app_label = "notifications"
        db_table = "notif_routing_rule"
        unique_together = [("tenant_id", "event_type")]
        ordering = ["event_type", "id"]

    def __str__(self) -> str:
        return f"RoutingRule({self.event_type} [{self.priority}]: {self.fallback_channels})"
