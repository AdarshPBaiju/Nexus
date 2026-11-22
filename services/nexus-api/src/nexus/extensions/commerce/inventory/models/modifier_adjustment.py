"""
nexus.extensions.commerce.inventory.models.modifier_adjustment - Modifier recipe adjustment model.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class ModifierRecipeAdjustment(TenantScopedModel):
    """
    Dynamic ingredient consumption adjustment triggered by an order customization modifier.
    """

    modifier_option_id = models.UUIDField(
        db_index=True,
        help_text=_("Associated MenuModifierOption UUID."),
    )
    ingredient = models.ForeignKey(
        "nexus_inventory_commerce.InventoryItem",
        on_delete=models.PROTECT,
        related_name="modifier_adjustments",
        help_text=_("Ingredient impacted by customization."),
    )
    quantity_delta = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text=_(
            "Incremental or decremental ingredient delta (+18g espresso, +220ml oat milk)."
        ),
    )
    is_substitution = models.BooleanField(
        default=False,
        help_text=_("True if this modifier substitutes another ingredient entirely."),
    )
    substituted_ingredient_id = models.UUIDField(
        null=True,
        blank=True,
        help_text=_("Ingredient replaced if is_substitution is True."),
    )

    class Meta:
        db_table = "inv_modifier_adjustment"
        ordering = ["modifier_option_id"]
        indexes = [
            models.Index(fields=["tenant_id", "modifier_option_id"]),
        ]

    @classmethod
    def create_adjustment(
        cls,
        tenant_id: uuid.UUID,
        modifier_option_id: uuid.UUID,
        ingredient_id: uuid.UUID,
        quantity_delta: Decimal,
    ) -> Self:
        return cls.objects.create(
            tenant_id=tenant_id,
            modifier_option_id=modifier_option_id,
            ingredient_id=ingredient_id,
            quantity_delta=quantity_delta,
            is_substitution=False,
        )

    def __str__(self) -> str:
        sign = "+" if self.quantity_delta >= 0 else ""
        return (
            f"ModifierAdjustment(mod={self.modifier_option_id}, delta={sign}{self.quantity_delta})"
        )
