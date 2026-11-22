"""
nexus.platform.authorization.governance.models.sod_rule - Segregation of Duties (SoD) Conflict Rule model.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class SodConflictRule(TenantScopedModel):
    """
    Statutory Segregation of Duties rule prohibiting assignment of conflicting permissions.
    """

    rule_code = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Standard SoD rule identifier (e.g. SOD-CASHIER-AUDITOR)."),
    )
    description = models.CharField(
        max_length=255,
        help_text=_("Business rationale for separating these roles."),
    )
    first_permission = models.CharField(
        max_length=128,
        db_index=True,
        help_text=_("First mutually conflicting permission code."),
    )
    conflicting_permission = models.CharField(
        max_length=128,
        db_index=True,
        help_text=_("Second mutually conflicting permission code."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    class Meta:
        app_label = "authorization"
        db_table = "authz_sod_conflict_rule"
        unique_together = [("tenant_id", "first_permission", "conflicting_permission")]
        ordering = ["rule_code", "id"]

    def __str__(self) -> str:
        return f"SoD({self.rule_code}: {self.first_permission} <-> {self.conflicting_permission})"
