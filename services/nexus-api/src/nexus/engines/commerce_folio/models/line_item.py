"""
nexus.engines.commerce_folio.models.line_item - Individual Folio Charge Line Item model.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.engines.commerce_folio.models.folio import CommerceFolio
from nexus.libs.ids import new_uuid7


class FolioLineItem(models.Model):
    """
    Polymorphic transactional charge line item added to a CommerceFolio.
    """

    class ItemType(models.TextChoices):
        FOOD_BEV = "FOOD_BEV", _("Food & Beverage")
        GAMING_TIME = "GAMING_TIME", _("Gaming Station Time")
        RETAIL = "RETAIL", _("Retail Merchandise")
        SERVICE = "SERVICE", _("Venue Service Charge")
        MEMBERSHIP = "MEMBERSHIP", _("Membership / Pass")

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    folio = models.ForeignKey(
        CommerceFolio,
        on_delete=models.CASCADE,
        related_name="lines",
        help_text=_("Parent commerce folio."),
    )
    item_type = models.CharField(
        max_length=32,
        choices=ItemType.choices,
        default=ItemType.FOOD_BEV,
        db_index=True,
    )
    description = models.CharField(
        max_length=255,
        help_text=_("Human-readable item title or SKU name."),
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("1.00"),
    )
    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=4,
    )
    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
    )
    tax_line_snapshot_json = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Immutable tax breakdown snapshot captured at line entry."),
    )

    class Meta:
        app_label = "commerce_folio"
        db_table = "com_folio_line_item"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"LineItem({self.description} x{self.quantity} = {self.total_amount})"
