"""
nexus.engines.resource_scheduler.models.resource - Unified Venue Resource Master model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class VenueResource(TenantScopedModel):
    """
    Physical station, dining table, room, console, or VR bay available for scheduling.
    Supports hierarchical grouping via self-referential parent.
    """

    class ResourceType(models.TextChoices):
        PC = "PC", _("Gaming PC Station")
        CONSOLE = "CONSOLE", _("Console Station (PS5 / Xbox)")
        VR = "VR", _("Virtual Reality Booth")
        TABLE = "TABLE", _("Dining Table")
        ROOM = "ROOM", _("Private Room / Suite")
        BED = "BED", _("Hotel Bed / Capsule")

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        help_text=_("Parent compound resource or grouping node."),
    )
    zone_id = models.UUIDField(
        db_index=True,
        help_text=_("Physical zone owning this resource."),
    )
    code = models.CharField(
        max_length=32,
        db_index=True,
        help_text=_("Human-readable station identifier (e.g. PC-01, TBL-14)."),
    )
    name = models.CharField(
        max_length=128,
        help_text=_("Descriptive name (e.g. VIP Gaming Rig Alpha)."),
    )
    resource_type = models.CharField(
        max_length=32,
        choices=ResourceType.choices,
        default=ResourceType.PC,
        db_index=True,
    )
    capacity = models.PositiveSmallIntegerField(
        default=1,
        help_text=_("Maximum concurrent occupancy capacity."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    class Meta:
        app_label = "resource_scheduler"
        db_table = "res_venue_resource"
        unique_together = [("tenant_id", "code")]
        ordering = ["code", "id"]

    def __str__(self) -> str:
        return f"Resource({self.code} [{self.resource_type}])"
