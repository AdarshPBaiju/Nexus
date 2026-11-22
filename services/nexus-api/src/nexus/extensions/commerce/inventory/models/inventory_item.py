"""
nexus.extensions.commerce.inventory.models.inventory_item - Raw material inventory stock item.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


@dataclass(frozen=True)
class CreateIngredientDto:
    """Parameter object for raw material inventory item creation."""

    tenant_id: uuid.UUID
    sku_code: str
    name: str
    uom: str = "GRAM"
    initial_stock: Decimal = Decimal("0.0000")


class InventoryItem(TenantScopedModel):
    """
    Raw material stock keeping item (beans, milk, cups, syrups) with atomic balances.
    """

    class UnitOfMeasure(models.TextChoices):
        GRAM = "GRAM", _("Grams (g)")
        ML = "ML", _("Milliliters (ml)")
        UNIT = "UNIT", _("Piece / Unit (ea)")
        KG = "KG", _("Kilograms (kg)")
        LITER = "LITER", _("Liters (L)")

    sku_code = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Stock keeping unit code for ingredient."),
    )
    name = models.CharField(
        max_length=150,
        help_text=_("Ingredient label (e.g. Arabica Espresso Beans, Whole Milk, Oat Milk)."),
    )
    uom_base = models.CharField(
        max_length=16,
        choices=UnitOfMeasure.choices,
        default=UnitOfMeasure.GRAM,
        help_text=_("Base inventory accounting unit of measure."),
    )
    current_stock_qty = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text=_("Real-time available stock balance on hand."),
    )
    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text=_("Weighted average unit acquisition cost."),
    )

    class Meta:
        db_table = "inv_inventory_item"
        ordering = ["sku_code"]
        indexes = [
            models.Index(fields=["tenant_id", "sku_code"]),
        ]
        unique_together = ("tenant_id", "sku_code")

    @classmethod
    def create_ingredient(cls, dto: CreateIngredientDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            sku_code=dto.sku_code,
            name=dto.name,
            uom_base=dto.uom,
            current_stock_qty=dto.initial_stock,
            unit_cost=Decimal("0.0000"),
        )

    def __str__(self) -> str:
        return (
            f"InventoryItem({self.sku_code}: {self.name}, {self.current_stock_qty} {self.uom_base})"
        )
