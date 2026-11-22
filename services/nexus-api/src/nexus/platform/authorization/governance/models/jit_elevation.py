"""
nexus.platform.authorization.governance.models.jit_elevation - Just-In-Time Break-Glass Elevation model.
"""
from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class JitElevationGrant(TenantScopedModel):
    """
    Temporary break-glass emergency elevation grant with mandatory justification and automatic expiration.
    """

    class ElevationStatus(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active Elevation")
        EXPIRED = "EXPIRED", _("Expired")
        REVOKED = "REVOKED", _("Manually Revoked")

    membership_id = models.UUIDField(
        db_index=True,
        help_text=_("Staff workspace membership receiving emergency elevation."),
    )
    elevated_permission = models.CharField(
        max_length=128,
        db_index=True,
        help_text=_("Elevated permission code granted (e.g. pos.order.void)."),
    )
    business_justification = models.CharField(
        max_length=255,
        help_text=_("Mandatory justification for emergency elevation."),
    )
    granted_at = models.DateTimeField(
        default=timezone.now,
    )
    expires_at = models.DateTimeField(
        db_index=True,
        help_text=_("Strict timestamp when temporary elevation expires (max 120m)."),
    )
    status = models.CharField(
        max_length=16,
        choices=ElevationStatus.choices,
        default=ElevationStatus.ACTIVE,
        db_index=True,
    )

    class Meta:
        app_label = "authorization"
        db_table = "authz_jit_elevation"
        ordering = ["-granted_at", "id"]
        indexes = [
            models.Index(fields=["tenant_id", "membership_id", "status"]),
        ]

    @property
    def is_currently_valid(self) -> bool:
        return self.status == self.ElevationStatus.ACTIVE and timezone.now() < self.expires_at

    def __str__(self) -> str:
        return f"JIT({self.membership_id} -> {self.elevated_permission} until {self.expires_at})"
