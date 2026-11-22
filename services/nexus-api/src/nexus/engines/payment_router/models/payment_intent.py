"""
nexus.engines.payment_router.models.payment_intent - Master Payment Intent Model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel
from nexus.libs.money.field import MoneyField


class PaymentIntent(TenantScopedModel):
    """
    Master payment authorization and capture intent bound to Folio and currency amount.
    """

    class Status(models.TextChoices):
        REQUIRES_PAYMENT_METHOD = "REQUIRES_PAYMENT_METHOD", _("Requires Payment Method")
        REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION", _("Requires Confirmation")
        PROCESSING = "PROCESSING", _("Processing")
        SUCCEEDED = "SUCCEEDED", _("Succeeded (Captured)")
        CANCELLED = "CANCELLED", _("Cancelled")
        FAILED = "FAILED", _("Failed")

    folio_id = models.UUIDField(
        db_index=True,
        help_text=_("Commerce Folio or invoice UUID owning this payment intent."),
    )
    customer_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Optional customer UUID."),
    )
    amount = MoneyField(
        help_text=_("Total intent payment amount."),
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        help_text=_("ISO 4217 nominal currency code."),
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.REQUIRES_PAYMENT_METHOD,
        db_index=True,
        help_text=_("Deterministic intent lifecycle status."),
    )
    selected_gateway = models.CharField(
        max_length=32,
        blank=True,
        default="",
        db_index=True,
        help_text=_("Gateway chosen for execution."),
    )
    idempotency_key = models.CharField(
        max_length=128,
        db_index=True,
        help_text=_("Deterministic deduplication key."),
    )

    class Meta:
        app_label = "payment_router"
        db_table = "pay_payment_intent"
        unique_together = [("tenant_id", "idempotency_key")]
        ordering = ["-created_at", "id"]

    def __str__(self) -> str:
        return f"PaymentIntent({self.id} [{self.currency} {self.amount}]: {self.status})"
