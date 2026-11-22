"""
nexus.platform.licensing.models.license_grant - Tenant License Grant model.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel
from nexus.platform.licensing.models.module_package import ModulePackage


class TenantLicenseGrant(TenantScopedModel):
    """
    Formal cryptographic license entitlement binding a package to a tenant.
    """

    package = models.ForeignKey(
        ModulePackage,
        on_delete=models.PROTECT,
        related_name="license_grants",
        help_text=_("Licensed capability package."),
    )
    license_type = models.CharField(
        max_length=64,
        default="COMMERCIAL_STANDARD",
        help_text=_("Commercial license identifier."),
    )
    capacity_limit = models.PositiveIntegerField(
        default=1,
        help_text=_("Concurrency or station capacity limit (e.g. max 5 POS stations)."),
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("License expiration timestamp (null denotes perpetual)."),
    )
    offline_cert_sig = models.TextField(
        blank=True,
        default="",
        help_text=_("Cryptographic Ed25519 signature of the offline certificate."),
    )

    class Meta:
        app_label = "licensing"
        db_table = "licensing_tenant_license_grant"
        unique_together = [("tenant_id", "package")]
        ordering = ["-created_at", "id"]

    @property
    def is_valid(self) -> bool:
        """Check if license has not expired."""
        return not (self.expires_at and timezone.now() > self.expires_at)

    def __str__(self) -> str:
        return f"LicenseGrant({self.package_id} @ {self.tenant_id}, valid={self.is_valid})"
