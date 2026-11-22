"""
nexus.extensions.commerce.pos.models.pos_order_line - Itemized counter sale line model.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


@dataclass(frozen=True)
class CreatePosLineDto:
    """Parameter object for order line creation."""

    tenant_id: uuid.UUID
    order_id: uuid.UUID
    item_name: str
    sku_code: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal
    modifiers_json: list[dict[str, Any]] = field(default_factory=list)


class PosOrderLine(TenantScopedModel):
    """
    Individual itemized beverage, pastry, or merchandise item in a counter order.
    """

    order_id = models.UUIDField(
        db_index=True,
        help_text=_("Associated PosOrder."),
    )
    item_name = models.CharField(
        max_length=128,
        help_text=_("Product name (e.g. Vanilla Oat Latte)."),
    )
    sku_code = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Unique stock keeping unit code."),
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal("1.0000"),
        help_text=_("Quantity ordered."),
    )
    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text=_("Unit base price including applied modifiers."),
    )
    line_total = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text=_("Total extended amount (quantity * unit_price)."),
    )
    modifiers_json = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of selected modifier options (syrups, milk, size)."),
    )
    is_voided = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Designates manager-authorized item void."),
    )
    void_reason = models.CharField(
        max_length=256,
        blank=True,
        help_text=_("Mandatory justification for voiding line item."),
    )

    class Meta:
        app_label = "nexus_pos_commerce"
        db_table = "pos_counter_order_line"
        ordering = ["id"]

    @classmethod
    def create_line(cls, dto: CreatePosLineDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            order_id=dto.order_id,
            item_name=dto.item_name,
            sku_code=dto.sku_code,
            quantity=dto.quantity,
            unit_price=dto.unit_price,
            line_total=dto.line_total,
            modifiers_json=dto.modifiers_json,
        )

    def void_line(self, reason: str) -> None:
        self.is_voided = True
        self.void_reason = reason
        self.save(update_fields=["is_voided", "void_reason", "updated_at"])

    def __str__(self) -> str:
        return f"Line({self.quantity}x {self.item_name} @ {self.unit_price})"
