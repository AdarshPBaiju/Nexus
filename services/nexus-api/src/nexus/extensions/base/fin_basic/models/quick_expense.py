"""
nexus.extensions.base.fin_basic.models.quick_expense - Petty cash quick disbursement model.
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
class QuickDisbursementDto:
    """Parameter object for petty cash disbursement."""

    tenant_id: uuid.UUID
    treasury_account_id: uuid.UUID
    expense_ledger_account_id: uuid.UUID
    amount: Decimal
    currency: str = "USD"
    reason_code: str = "MISCELLANEOUS"
    description: str = ""
    shift_session_id: uuid.UUID | None = None
    receipt_attachment_url: str = ""


class QuickExpenseRecord(TenantScopedModel):
    """
    Records petty cash disbursements directly from the register cash drawer.
    """

    class ReasonCode(models.TextChoices):
        PETTY_CASH_SUPPLIES = "PETTY_CASH_SUPPLIES", _("Emergency Store / Bar Supplies")
        STAFF_MEAL = "STAFF_MEAL", _("Staff Duty Meal Disbursement")
        DELIVERY_FEE = "DELIVERY_FEE", _("Cash Delivery Rider Tip / Fee")
        EMERGENCY_REPAIR = "EMERGENCY_REPAIR", _("Immediate Equipment / Venue Repair")
        MISCELLANEOUS = "MISCELLANEOUS", _("Other Authorized Register Disbursement")

    shift_session_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Associated open shift session where cash was withdrawn."),
    )
    treasury_account_id = models.UUIDField(
        db_index=True,
        help_text=_("Cash drawer treasury account supplying funds."),
    )
    expense_ledger_account_id = models.UUIDField(
        db_index=True,
        help_text=_("Target operating expense account in Chart of Accounts."),
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text=_("Disbursement amount."),
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        help_text=_("ISO 4217 transaction currency."),
    )
    reason_code = models.CharField(
        max_length=64,
        choices=ReasonCode.choices,
        default=ReasonCode.MISCELLANEOUS,
        db_index=True,
    )
    description = models.TextField(
        blank=True,
        help_text=_("Detailed memorandum explaining business justification."),
    )
    receipt_attachment_url = models.CharField(
        max_length=512,
        blank=True,
        help_text=_("Uploaded photographic receipt or paper invoice voucher URL."),
    )

    class Meta:
        app_label = "nexus_fin_basic"
        db_table = "fin_quick_expense_record"
        ordering = ["-created_at", "id"]

    @classmethod
    def record_disbursement(cls, dto: QuickDisbursementDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            treasury_account_id=dto.treasury_account_id,
            expense_ledger_account_id=dto.expense_ledger_account_id,
            amount=dto.amount,
            currency=dto.currency,
            reason_code=dto.reason_code,
            description=dto.description,
            shift_session_id=dto.shift_session_id,
            receipt_attachment_url=dto.receipt_attachment_url,
        )

    def __str__(self) -> str:
        return f"QuickExpense({self.amount} {self.currency} [{self.reason_code}])"
