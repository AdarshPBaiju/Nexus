"""
nexus.platform.licensing.models.module_package - Plugin Module Package catalog model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7


class ModulePackage(models.Model):
    """
    First-party capability package or ecosystem plugin specification.
    """

    class Tier(models.TextChoices):
        KERNEL = "KERNEL", _("Tier 1: Platform Kernel")
        SHARED_SERVICES = "SHARED_SERVICES", _("Tier 2: Shared Business Services")
        FIRST_PARTY_CAPABILITY = "FIRST_PARTY_CAPABILITY", _("Tier 3: First-Party Capabilities")
        ECOSYSTEM_APP = "ECOSYSTEM_APP", _("Tier 4: Ecosystem Marketplace Apps")

    class ExecutionSurface(models.TextChoices):
        WEB_ALL = "WEB_ALL", _("Web Browser and Desktop Shell")
        DESKTOP_ONLY = "DESKTOP_ONLY", _("Desktop Native Runtime (Tauri 2.0 Rust)")
        HYBRID_WEB_DESKTOP = "HYBRID_WEB_DESKTOP", _("Hybrid Web Control Plane + Desktop Bridge")

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    code = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text=_(
            "Unique capability code (e.g. POS, CAFE_QSR, KDS, GAME_CORE, HW_PRINTER_LOCAL)."
        ),
    )
    name = models.CharField(
        max_length=128,
        help_text=_("Human-readable capability name (e.g. Café First QSR POS)."),
    )
    tier = models.CharField(
        max_length=32,
        choices=Tier.choices,
        default=Tier.FIRST_PARTY_CAPABILITY,
        db_index=True,
    )
    execution_surface = models.CharField(
        max_length=32,
        choices=ExecutionSurface.choices,
        default=ExecutionSurface.WEB_ALL,
        db_index=True,
    )
    manifest_json = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Capability manifest declaring dependencies, routes, and DYN_CONFIG schema."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Designates whether this package is available in the marketplace."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        app_label = "licensing"
        db_table = "licensing_module_package"
        ordering = ["code", "id"]

    @property
    def requires_desktop(self) -> bool:
        """Check if package strictly requires Desktop Runtime."""
        return self.execution_surface == self.ExecutionSurface.DESKTOP_ONLY

    def __str__(self) -> str:
        return f"Package({self.code}, surface={self.execution_surface})"
