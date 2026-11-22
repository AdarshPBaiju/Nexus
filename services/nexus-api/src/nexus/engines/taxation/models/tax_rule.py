"""
nexus.engines.taxation.models.tax_rule - Statutory Tax Rule and Rate Revision model.
"""
from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class TaxRuleRevision(TenantScopedModel):
    """
    Statutory tax rule governing rate percentage, inclusive vs. exclusive math, and tax type.
    """

    class TaxType(models.TextChoices):
        VAT = "VAT", _("Value Added Tax")
        GST = "GST", _("Goods and Services Tax")
        SALES_TAX = "SALES_TAX", _("Retail Sales Tax")
        SERVICE_CHARGE = "SERVICE_CHARGE", _("Statutory Service Charge")

    rule_code = models.CharField(
        max_length=32,
        db_index=True,
        help_text=_("Rule identifier (e.g. VAT-STANDARD-5, GST-18, EXEMPT)."),
    )
    tax_type = models.CharField(
        max_length=32,
        choices=TaxType.choices,
        default=TaxType.VAT,
        db_index=True,
    )
    rate_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text=_("Nominal tax rate percentage (e.g. 5.0000 for 5%)."),
    )
    is_inclusive = models.BooleanField(
        default=False,
        help_text=_("Designates whether price displays already include this tax."),
    )
    effective_from = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )
    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        app_label = "taxation"
        db_table = "tax_rule_revision"
        ordering = ["-effective_from", "id"]

    def __str__(self) -> str:
        mode = "INC" if self.is_inclusive else "EXC"
        return f"TaxRule({self.rule_code} @ {self.rate_percentage}% [{mode}])"
