"""
nexus.extensions.commerce.pos.models.pos_order - Counter Point of Sale order header model.
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
class CreatePosOrderDto:
    """Parameter object for POS counter order creation."""

    tenant_id: uuid.UUID
    order_number: str
    branch_id: uuid.UUID
    workstation_id: str
    cashier_user_id: uuid.UUID
    subtotal_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str = "USD"
    discount_amount: Decimal = Decimal("0.0000")
    shift_session_id: uuid.UUID | None = None


class PosOrder(TenantScopedModel):
    """
    Transactional order record for front-counter sales, split tenders, and tab holds.
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Active Cart Draft")
        HELD = "HELD", _("Held Order Tab")
        PAID = "PAID", _("Fully Tendered & Settle")
        VOIDED = "VOIDED", _("Supervised Void")

    order_number = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Sequential business order identifier (e.g. ORD-2026-0001)."),
    )
    branch_id = models.UUIDField(
        db_index=True,
        help_text=_("Venue branch where order was rung up."),
    )
    workstation_id = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("POS register workstation ID."),
    )
    cashier_user_id = models.UUIDField(
        db_index=True,
        help_text=_("Cashier staff user ringing up sale."),
    )
    shift_session_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Active ShiftRegisterSession receiving tender."),
    )
    subtotal_amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text=_("Sum of line items before tax and discount."),
    )
    discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text=_("Total promotional or comp discount applied."),
    )
    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text=_("Total statutory sales tax calculated."),
    )
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text=_("Net payable balance due from customer."),
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        help_text=_("ISO 4217 transaction currency."),
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    journal_entry_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Balancing General Ledger sales journal entry."),
    )

    class Meta:
        app_label = "nexus_pos_commerce"
        db_table = "pos_counter_order"
        unique_together = [("tenant_id", "order_number")]
        ordering = ["-created_at", "id"]

    @classmethod
    def create_order(cls, dto: CreatePosOrderDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            order_number=dto.order_number,
            branch_id=dto.branch_id,
            workstation_id=dto.workstation_id,
            cashier_user_id=dto.cashier_user_id,
            shift_session_id=dto.shift_session_id,
            subtotal_amount=dto.subtotal_amount,
            discount_amount=dto.discount_amount,
            tax_amount=dto.tax_amount,
            total_amount=dto.total_amount,
            currency=dto.currency,
            status=cls.Status.DRAFT,
        )

    def mark_paid(self, journal_id: uuid.UUID) -> None:
        self.status = self.Status.PAID
        self.journal_entry_id = journal_id
        self.save(update_fields=["status", "journal_entry_id", "updated_at"])

    def __str__(self) -> str:
        return (
            f"PosOrder({self.order_number} - {self.total_amount} {self.currency} [{self.status}])"
        )
