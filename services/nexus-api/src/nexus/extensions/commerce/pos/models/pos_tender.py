"""
nexus.extensions.commerce.pos.models.pos_tender - Split payment tender allocation model.
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
class CreatePosTenderDto:
    """Parameter object for payment tender creation."""

    tenant_id: uuid.UUID
    order_id: uuid.UUID
    tender_type: str
    tendered_amount: Decimal
    applied_amount: Decimal
    change_returned: Decimal = Decimal("0.0000")
    reference_code: str = ""


class PosPaymentTender(TenantScopedModel):
    """
    Individual payment rail transaction allocated toward settling an order balance.
    """

    class TenderType(models.TextChoices):
        CASH = "CASH", _("Physical Cash Tender")
        CARD = "CARD", _("Integrated / External Card Terminal")
        DIGITAL_QR = "DIGITAL_QR", _("Instant Digital QR (UPI / Stripe / Razorpay)")

    order_id = models.UUIDField(
        db_index=True,
        help_text=_("Associated PosOrder."),
    )
    tender_type = models.CharField(
        max_length=32,
        choices=TenderType.choices,
        default=TenderType.CASH,
        db_index=True,
    )
    tendered_amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text=_("Total gross amount presented by customer."),
    )
    change_returned = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text=_("Cash change returned to customer."),
    )
    applied_amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text=_("Net amount credited toward settling order total."),
    )
    reference_code = models.CharField(
        max_length=128,
        blank=True,
        help_text=_("Card auth code, transaction ARN, or digital payment reference."),
    )

    class Meta:
        app_label = "nexus_pos_commerce"
        db_table = "pos_payment_tender"
        ordering = ["id"]

    @classmethod
    def create_tender(cls, dto: CreatePosTenderDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            order_id=dto.order_id,
            tender_type=dto.tender_type,
            tendered_amount=dto.tendered_amount,
            change_returned=dto.change_returned,
            applied_amount=dto.applied_amount,
            reference_code=dto.reference_code,
        )

    def __str__(self) -> str:
        return f"Tender({self.tender_type}: {self.applied_amount})"
