"""
nexus.extensions.commerce.kds.models.kitchen_ticket_line - Kitchen ticket itemized line model.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Self

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


@dataclass(frozen=True)
class CreateTicketLineDto:
    """Parameter object for ticket line item creation."""

    tenant_id: uuid.UUID
    ticket_id: uuid.UUID
    item_name: str
    quantity: Decimal
    modifier_notes: list[str] = field(default_factory=list)
    allergen_flags: list[str] = field(default_factory=list)


class KitchenTicketLine(TenantScopedModel):
    """
    Individual itemized dish or beverage on a KDS ticket with modifiers and allergen tags.
    """

    class LineStatus(models.TextChoices):
        PENDING = "PENDING", _("Pending Preparation")
        COMPLETED = "COMPLETED", _("Completed by Station")

    ticket = models.ForeignKey(
        "nexus_kds_commerce.KitchenTicket",
        on_delete=models.CASCADE,
        related_name="lines",
        help_text=_("Parent kitchen ticket header."),
    )
    item_name = models.CharField(
        max_length=150,
        help_text=_("Menu item label displayed on KDS monitor."),
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("1.00"),
        help_text=_("Preparation item count."),
    )
    modifier_notes_json = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Special instructions and customizations (e.g. Oat Milk, Extra Hot)."),
    )
    allergen_flags_json = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Critical allergen alerts (e.g. ['DAIRY', 'NUTS', 'GLUTEN'])."),
    )
    status = models.CharField(
        max_length=32,
        choices=LineStatus.choices,
        default=LineStatus.PENDING,
        db_index=True,
        help_text=_("Item-level preparation state."),
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Line completion timestamp."),
    )

    class Meta:
        db_table = "kds_kitchen_ticket_line"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["tenant_id", "ticket_id", "status"]),
        ]

    @classmethod
    def create_line(cls, dto: CreateTicketLineDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            ticket_id=dto.ticket_id,
            item_name=dto.item_name,
            quantity=dto.quantity,
            modifier_notes_json=dto.modifier_notes,
            allergen_flags_json=dto.allergen_flags,
            status=cls.LineStatus.PENDING,
        )

    def mark_completed(self) -> None:
        self.status = self.LineStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at", "updated_at"])

    def __str__(self) -> str:
        return f"KitchenTicketLine({self.item_name} x{self.quantity})"
