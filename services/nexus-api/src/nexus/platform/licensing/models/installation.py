"""
nexus.platform.licensing.models.installation - Tenant Plugin Installation lifecycle model.
"""

from __future__ import annotations

from typing import Self

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel
from nexus.platform.licensing.models.module_package import ModulePackage


class TenantPluginInstallation(TenantScopedModel):
    """
    Represents declarative feature enablement for a tenant.
    Install = Enable in PostgreSQL and Redis (< 1ms). Zero server restarts.
    """

    class InstallationStatus(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active & Enabled")
        DRAINING = "DRAINING", _("Draining (settling existing transactions)")
        ARCHIVED = "ARCHIVED", _("Archived & Disabled")

    package = models.ForeignKey(
        ModulePackage,
        on_delete=models.PROTECT,
        related_name="tenant_installations",
        help_text=_("Module package enabled for this tenant."),
    )
    status = models.CharField(
        max_length=32,
        choices=InstallationStatus.choices,
        default=InstallationStatus.ACTIVE,
        db_index=True,
    )
    installed_at = models.DateTimeField(
        default=timezone.now,
        help_text=_("Timestamp when the feature was enabled."),
    )

    class Meta:
        app_label = "licensing"
        db_table = "licensing_tenant_installation"
        unique_together = [("tenant_id", "package")]
        ordering = ["-installed_at", "id"]

    @property
    def is_operational(self) -> bool:
        """Assert package is actively executing business operations."""
        return self.status == self.InstallationStatus.ACTIVE

    def transition_to_draining(self) -> Self:
        """Non-destructive uninstall: block new transactions while active folios settle."""
        if self.status != self.InstallationStatus.ACTIVE:
            raise ValidationError(_("Only ACTIVE installations can transition to DRAINING."))
        self.status = self.InstallationStatus.DRAINING
        return self

    def archive(self) -> Self:
        """Completely disable feature after draining."""
        self.status = self.InstallationStatus.ARCHIVED
        return self

    def reactivate(self) -> Self:
        """Re-enable feature immediately."""
        self.status = self.InstallationStatus.ACTIVE
        return self

    def __str__(self) -> str:
        return f"Installation({self.package_id} @ {self.tenant_id}, status={self.status})"
