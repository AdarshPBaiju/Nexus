"""
nexus.extensions.commerce.inventory.models.inventory_movement - Immutable inventory movement event.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Self

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class InventoryMovementEvent(TenantScopedModel):
    """
    Append-only inventory movement audit entry for auto-depletion and adjustments.
    """

    class MovementType(models.TextChoices):
        POS_DEPLETION = "POS_DEPLETION", _("POS Sale Auto-Depletion")
        KDS_BUMP = "KDS_BUMP", _("KDS Bump Auto-Depletion")
        WASTE = "WASTE", _("Barista Spillage / Waste")
        RECEIPT = "RECEIPT", _("Purchase Order Stock Inward")

    ingredient = models.ForeignKey(
        "nexus_inventory_commerce.InventoryItem",
        on_delete=models.PROTECT,
        related_name="movements",
        help_text=_("Impacted stock ingredient."),
    )
    reference_id = models.CharField(
        max_length=128,
        db_index=True,
        help_text=_("External tracking reference (Order ID, KDS Ticket ID)."),
    )
    movement_type = models.CharField(
        max_length=32,
        choices=MovementType.choices,
        default=MovementType.POS_DEPLETION,
        db_index=True,
        help_text=_("Source business reason for inventory delta."),
    )
    quantity_delta = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text=_("Signed stock change (negative for depletion)."),
    )
    balance_after = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        help_text=_("Stock balance immediately following transaction."),
    )
    occurred_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text=_("Audit timestamp."),
    )

    class Meta:
        db_table = "inv_movement_event"
        ordering = ["-occurred_at"]
        indexes = [
            models.Index(fields=["tenant_id", "ingredient_id", "occurred_at"]),
        ]

    @classmethod
    def record_movement(
        cls,
        tenant_id: uuid.UUID,
        ingredient_id: uuid.UUID,
        delta: Decimal,
        balance_after: Decimal,
    ) -> Self:
        return cls.objects.create(
            tenant_id=tenant_id,
            ingredient_id=ingredient_id,
            reference_id="AUTO-DEPLETE",
            movement_type=cls.MovementType.POS_DEPLETION,
            quantity_delta=delta,
            balance_after=balance_after,
            occurred_at=timezone.now(),
        )

    def __str__(self) -> str:
        return (
            f"Movement({self.movement_type}, ing={self.ingredient_id}, delta={self.quantity_delta})"
        )
