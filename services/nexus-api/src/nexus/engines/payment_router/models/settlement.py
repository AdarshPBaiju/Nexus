"""
nexus.engines.payment_router.models.settlement - Gateway T+1 Settlement Batch Model.
"""
from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel
from nexus.libs.money.field import MoneyField


class SettlementBatch(TenantScopedModel):
    """
    T+1 gateway payout reconciliation batch summary.
    """

    batch_id = models.CharField(
        max_length=128,
        db_index=True,
        help_text=_("External payout or settlement batch reference."),
    )
    gateway_code = models.CharField(
        max_length=32,
        db_index=True,
        help_text=_("Gateway provider code (e.g. STRIPE, RAZORPAY)."),
    )
    total_gross = MoneyField(
        default=Decimal("0.0000"),
        help_text=_("Total gross transactions in batch."),
    )
    total_fee = MoneyField(
        default=Decimal("0.0000"),
        help_text=_("Total MDR and processing fees deducted."),
    )
    total_net = MoneyField(
        default=Decimal("0.0000"),
        help_text=_("Net payout deposited into bank."),
    )
    reconciled = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Reconciliation audit status flag."),
    )

    class Meta:
        app_label = "payment_router"
        db_table = "pay_settlement_batch"
        unique_together = [("tenant_id", "batch_id")]
        ordering = ["-created_at", "id"]

    def __str__(self) -> str:
        return f"SettlementBatch({self.batch_id} [{self.gateway_code}]: net={self.total_net})"
