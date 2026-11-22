"""
nexus.extensions.commerce.inventory.models.recipe_bom_line - Recipe BOM line ingredient model.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class RecipeBOMLine(TenantScopedModel):
    """
    Specific raw material ingredient requirement in a RecipeBOM.
    """

    bom = models.ForeignKey(
        "nexus_inventory_commerce.RecipeBOM",
        on_delete=models.CASCADE,
        related_name="lines",
        help_text=_("Parent recipe BOM header."),
    )
    ingredient = models.ForeignKey(
        "nexus_inventory_commerce.InventoryItem",
        on_delete=models.PROTECT,
        related_name="bom_lines",
        help_text=_("Consumed raw inventory ingredient."),
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text=_("Ingredient requirement per recipe yield portion."),
    )
    uom = models.CharField(
        max_length=16,
        default="GRAM",
        help_text=_("Consumption unit of measure (e.g. GRAM, ML, UNIT)."),
    )

    class Meta:
        db_table = "inv_recipe_bom_line"
        ordering = ["bom", "id"]
        indexes = [
            models.Index(fields=["tenant_id", "bom_id"]),
        ]

    @classmethod
    def add_line(
        cls,
        tenant_id: uuid.UUID,
        bom_id: uuid.UUID,
        ingredient_id: uuid.UUID,
        quantity: Decimal,
    ) -> Self:
        return cls.objects.create(
            tenant_id=tenant_id,
            bom_id=bom_id,
            ingredient_id=ingredient_id,
            quantity=quantity,
            uom="GRAM",
        )

    def __str__(self) -> str:
        return f"RecipeBOMLine(ing={self.ingredient_id}, qty={self.quantity} {self.uom})"
