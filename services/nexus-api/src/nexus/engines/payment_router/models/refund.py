"""
nexus.engines.payment_router.models.refund - Payment Refund Model.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.engines.payment_router.models.payment_attempt import PaymentAttempt
from nexus.libs.models.tenant_scoped import TenantScopedModel
from nexus.libs.money.field import MoneyField


class PaymentRefund(TenantScopedModel):
    """
    Partial or full refund against a captured payment attempt.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending Approval")
        COMPLETED = "COMPLETED", _("Completed")
        REJECTED = "REJECTED", _("Rejected")

    payment_attempt = models.ForeignKey(
        PaymentAttempt,
        on_delete=models.CASCADE,
        related_name="refunds",
        help_text=_("Target captured payment attempt."),
    )
    amount = MoneyField(
        help_text=_("Amount to refund to customer."),
    )
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text=_("Refund status."),
    )
    reason = models.CharField(
        max_length=128,
        blank=True,
        default="CUSTOMER_REQUEST",
        help_text=_("Auditable business reason for refund."),
    )

    class Meta:
        app_label = "payment_router"
        db_table = "pay_refund"
        ordering = ["-created_at", "id"]

    def __str__(self) -> str:
        return f"Refund({self.id}: {self.amount} [{self.status}])"
