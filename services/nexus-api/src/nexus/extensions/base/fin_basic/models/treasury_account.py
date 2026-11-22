"""
nexus.extensions.base.fin_basic.models.treasury_account - Dedicated financial container model.
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
class CreateTreasuryAccountDto:
    """Parameter object for container provisioning."""

    tenant_id: uuid.UUID
    name: str
    code: str
    account_type: str
    control_ledger_account_id: uuid.UUID
    currency: str = "USD"
    branch_id: uuid.UUID | None = None


class TreasuryAccount(TenantScopedModel):
    """
    Dedicated physical or institutional financial container holding operational funds.
    """

    class AccountType(models.TextChoices):
        CASH_DRAWER = "CASH_DRAWER", _("Physical POS Cash Drawer")
        BANK_ACCOUNT = "BANK_ACCOUNT", _("Operating Commercial Bank Account")
        GATEWAY_CLEARING = "GATEWAY_CLEARING", _("Payment Gateway Clearing Container")

    account_name = models.CharField(
        max_length=128,
        help_text=_("Human-readable container title (e.g. Counter #1 Cash Drawer)."),
    )
    account_code = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Internal unique identifier code within tenant (e.g. TACC-DRAWER-01)."),
    )
    account_type = models.CharField(
        max_length=32,
        choices=AccountType.choices,
        default=AccountType.CASH_DRAWER,
        db_index=True,
    )
    control_ledger_account_id = models.UUIDField(
        db_index=True,
        help_text=_("Foreign key to Chart of Accounts control ledger account."),
    )
    branch_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Branch location where container physically resides."),
    )
    custodian_user_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Primary staff custodian responsible for balance."),
    )
    current_balance = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text=_("Real-time running balance in nominal currency."),
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        help_text=_("ISO 4217 nominal currency."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Designates whether container is available for active shift transactions."),
    )

    class Meta:
        app_label = "nexus_fin_basic"
        db_table = "fin_treasury_account"
        unique_together = [("tenant_id", "account_code")]
        ordering = ["account_code", "id"]

    @classmethod
    def create_container(cls, dto: CreateTreasuryAccountDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            account_name=dto.name,
            account_code=dto.code,
            account_type=dto.account_type,
            control_ledger_account_id=dto.control_ledger_account_id,
            currency=dto.currency,
            branch_id=dto.branch_id,
        )

    def __str__(self) -> str:
        return f"TreasuryAccount({self.account_code} - {self.account_name} [{self.currency}])"
