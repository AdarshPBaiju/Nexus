"""
nexus.engines.payment_router.models.payment_attempt - Payment Attempt Model.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.engines.payment_router.models.payment_intent import PaymentIntent
from nexus.libs.models.tenant_scoped import TenantScopedModel
from nexus.libs.money.field import MoneyField


class PaymentAttempt(TenantScopedModel):
    """
    Individual transaction execution attempt under a PaymentIntent.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        AUTHORIZED = "AUTHORIZED", _("Authorized (Hold)")
        CAPTURED = "CAPTURED", _("Captured")
        FAILED = "FAILED", _("Failed")

    intent = models.ForeignKey(
        PaymentIntent,
        on_delete=models.CASCADE,
        related_name="attempts",
        help_text=_("Parent master payment intent."),
    )
    gateway_tx_id = models.CharField(
        max_length=128,
        db_index=True,
        help_text=_("External transaction identifier returned by gateway."),
    )
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text=_("Lifecycle status of this attempt."),
    )
    amount_captured = MoneyField(
        default=Decimal("0.0000"),
        help_text=_("Net amount captured successfully."),
    )
    fee_amount = MoneyField(
        default=Decimal("0.0000"),
        help_text=_("Gateway processing fee or MDR deducted."),
    )
    raw_response = models.JSONField(
        default=dict,
        help_text=_("Full provider response payload for forensics."),
    )

    class Meta:
        app_label = "payment_router"
        db_table = "pay_payment_attempt"
        ordering = ["-created_at", "id"]

    def __str__(self) -> str:
        return f"Attempt({self.gateway_tx_id} [{self.status}]: {self.amount_captured})"
