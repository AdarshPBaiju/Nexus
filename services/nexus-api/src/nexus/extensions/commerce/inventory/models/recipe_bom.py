"""
nexus.extensions.commerce.inventory.models.recipe_bom - Recipe Bill-of-Materials header model.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class RecipeBOM(TenantScopedModel):
    """
    Standard production recipe bill-of-materials linking a menu item to raw ingredients.
    """

    menu_item_id = models.UUIDField(
        db_index=True,
        help_text=_("Associated sellable MenuItem."),
    )
    yield_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("1.00"),
        help_text=_("Yield count of standard portions produced by this recipe."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Active depletion recipe flag."),
    )

    class Meta:
        db_table = "inv_recipe_bom"
        ordering = ["menu_item_id"]
        indexes = [
            models.Index(fields=["tenant_id", "menu_item_id", "is_active"]),
        ]
        unique_together = ("tenant_id", "menu_item_id")

    @classmethod
    def create_bom(
        cls,
        tenant_id: uuid.UUID,
        menu_item_id: uuid.UUID,
        yield_qty: Decimal = Decimal("1.00"),
    ) -> Self:
        return cls.objects.create(
            tenant_id=tenant_id,
            menu_item_id=menu_item_id,
            yield_quantity=yield_qty,
            is_active=True,
        )

    def __str__(self) -> str:
        return f"RecipeBOM(item={self.menu_item_id}, yield={self.yield_quantity})"
