"""
nexus.platform.authorization.models.permission - Canonical Permission Catalog model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7


class PermissionCatalog(models.Model):
    """
    Canonical system registry of all fine-grained namespaced permission codes.
    """

    class RiskTier(models.TextChoices):
        LOW = "LOW", _("Low Risk (Standard read/list)")
        MEDIUM = "MEDIUM", _("Medium Risk (Standard creation/edit)")
        HIGH = "HIGH", _("High Risk (Financial adjustments, voids, discounts)")
        CRITICAL = "CRITICAL", _("Critical Risk (System config, security, payout)")

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    code = models.CharField(
        max_length=128,
        unique=True,
        db_index=True,
        help_text=_("Namespaced permission code (e.g. order.create, folio.settle, pos.void)."),
    )
    description = models.CharField(
        max_length=255,
        help_text=_("Human-readable business action governed by this permission."),
    )
    risk_tier = models.CharField(
        max_length=16,
        choices=RiskTier.choices,
        default=RiskTier.MEDIUM,
        db_index=True,
    )
    requires_step_up = models.BooleanField(
        default=False,
        help_text=_("Designates whether invoking this permission requires Cashier PIN step-up."),
    )

    class Meta:
        app_label = "authorization"
        db_table = "authz_permission_catalog"
        ordering = ["code"]

    def __str__(self) -> str:
        return f"Perm({self.code} [{self.risk_tier}])"
