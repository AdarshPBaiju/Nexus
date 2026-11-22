"""
nexus.platform.licensing.models.pricing_offer - Commercial pricing and licensing model.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7
from nexus.platform.licensing.models.module_package import ModulePackage


class ModulePricingOffer(models.Model):
    """
    Commercial pricing offer associated with a ModulePackage.
    """

    class LicenseModel(models.TextChoices):
        FREE_INCLUDED = "FREE_INCLUDED", _("Free Core Included")
        SUBSCRIPTION_RECURRING = "SUBSCRIPTION_RECURRING", _("Monthly/Annual Recurring SaaS")
        ONE_TIME_PERPETUAL = "ONE_TIME_PERPETUAL", _("One-Time Perpetual License")
        ONE_TIME_PLUS_AMC = "ONE_TIME_PLUS_AMC", _("One-Time Perpetual + Annual Maintenance")
        USAGE_METERED = "USAGE_METERED", _("Pay-As-You-Go Usage Metered")

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    package = models.ForeignKey(
        ModulePackage,
        on_delete=models.CASCADE,
        related_name="pricing_offers",
        help_text=_("Module package this offer applies to."),
    )
    license_model = models.CharField(
        max_length=32,
        choices=LicenseModel.choices,
        default=LicenseModel.FREE_INCLUDED,
        db_index=True,
    )
    recurring_price = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text=_("Price in exact string decimal ISO 4217 currency."),
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        help_text=_("ISO 4217 3-letter currency code."),
    )

    class Meta:
        app_label = "licensing"
        db_table = "licensing_pricing_offer"
        ordering = ["package", "license_model", "id"]

    def __str__(self) -> str:
        return f"Offer({self.package_id}, model={self.license_model}, price={self.recurring_price} {self.currency})"
