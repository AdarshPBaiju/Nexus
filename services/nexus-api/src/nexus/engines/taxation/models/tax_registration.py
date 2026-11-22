"""
nexus.engines.taxation.models.tax_registration - Statutory Tax Registration model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class TaxRegistration(TenantScopedModel):
    """
    Statutory tax registration holding Tax Authority identification (GSTIN, VAT TRN, EIN).
    """

    jurisdiction_code = models.CharField(
        max_length=8,
        db_index=True,
        help_text=_("ISO 3166-1 alpha-2 or alpha-3 jurisdiction (e.g. AE, IN, US-CA)."),
    )
    tax_authority_name = models.CharField(
        max_length=128,
        help_text=_("Official name of tax administration (e.g. FTA, GST Council, IRS)."),
    )
    registration_number = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Statutory tax registration number (e.g. TRN 100200300400003)."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Designates whether this tax registration is active for billing."),
    )

    class Meta:
        app_label = "taxation"
        db_table = "tax_registration"
        unique_together = [("tenant_id", "jurisdiction_code", "registration_number")]
        ordering = ["jurisdiction_code", "id"]

    def __str__(self) -> str:
        return f"TaxReg({self.jurisdiction_code} - {self.registration_number})"
