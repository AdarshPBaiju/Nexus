"""
nexus.extensions.commerce.cafe_qsr.models.combo_rule - Dynamic combo rule domain model.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any, Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class ComboRule(TenantScopedModel):
    """
    Meal deal and bundle rule definition (e.g. Breakfast Duo, Coffee + Croissant).
    """

    name = models.CharField(
        max_length=120,
        help_text=_("Combo deal marketing label."),
    )
    bundle_price = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text=_("Total bundle fixed price."),
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        help_text=_("ISO 4217 currency code."),
    )
    required_category_ids_json = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of category IDs required to complete combo bundle."),
    )
    required_item_ids_json = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Specific item IDs required or permitted in combo bundle."),
    )
    valid_days_hours_json = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Availability schedule (days of week, time window)."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Combo active status."),
    )

    class Meta:
        db_table = "cafe_combo_rule"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant_id", "is_active"]),
        ]

    @classmethod
    def create_combo(
        cls,
        tenant_id: uuid.UUID,
        name: str,
        bundle_price: Decimal,
        required_categories: list[str] | None = None,
    ) -> Self:
        return cls.objects.create(
            tenant_id=tenant_id,
            name=name,
            bundle_price=bundle_price,
            required_category_ids_json=required_categories or [],
            required_item_ids_json=[],
            valid_days_hours_json={"all_day": True},
            is_active=True,
        )

    def is_valid_now(self) -> bool:
        if not self.is_active:
            return False
        rules: dict[str, Any] = self.valid_days_hours_json or {}
        return bool(rules.get("all_day", True))

    def __str__(self) -> str:
        return f"ComboRule({self.name}, bundle={self.bundle_price} {self.currency})"
