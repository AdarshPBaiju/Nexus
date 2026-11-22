"""
nexus.extensions.commerce.cafe_qsr.models.modifier_option - Modifier option domain model.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class MenuModifierOption(TenantScopedModel):
    """
    Individual modifier selection option with price adjustment and BOM impact.
    """

    group = models.ForeignKey(
        "nexus_cafe_qsr_commerce.MenuModifierGroup",
        on_delete=models.CASCADE,
        related_name="options",
        help_text=_("Parent modifier group classification."),
    )
    name = models.CharField(
        max_length=100,
        help_text=_("Option name (e.g. Oat Milk, Extra Shot, Sugar Free Vanilla)."),
    )
    price_delta = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text=_("Price adjustment added to item base price."),
    )
    is_default = models.BooleanField(
        default=False,
        help_text=_("Pre-selected default option when item is added to cart."),
    )
    recipe_bom_delta_json = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("BOM inventory consumption deltas (e.g. {'ING_OAT_MILK_ML': 250})."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Option active status."),
    )
    sort_order = models.IntegerField(
        default=0,
        db_index=True,
        help_text=_("Display sequence in group."),
    )

    class Meta:
        db_table = "cafe_modifier_option"
        ordering = ["group", "sort_order", "name"]
        indexes = [
            models.Index(fields=["tenant_id", "group_id", "is_active"]),
        ]

    @classmethod
    def create_option(
        cls,
        tenant_id: uuid.UUID,
        group_id: uuid.UUID,
        name: str,
        price_delta: Decimal = Decimal("0.0000"),
    ) -> Self:
        return cls.objects.create(
            tenant_id=tenant_id,
            group_id=group_id,
            name=name,
            price_delta=price_delta,
            is_default=False,
            is_active=True,
            sort_order=0,
        )

    def __str__(self) -> str:
        sign = "+" if self.price_delta >= 0 else ""
        return f"MenuModifierOption({self.name}, delta={sign}{self.price_delta})"
