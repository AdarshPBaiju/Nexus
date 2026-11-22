"""
nexus.extensions.base.fin_basic.provisioning - Automatic provisioning for FIN_CORE capability.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction

from nexus.engines.accounting.models.account import LedgerAccount
from nexus.extensions.base.fin_basic.models.treasury_account import TreasuryAccount


@dataclass(frozen=True)
class LedgerAccountSpec:
    """Specification for ledger control account creation."""

    code: str
    name: str
    account_type: str
    currency: str


@dataclass(frozen=True)
class TreasuryContainerSpec:
    """Specification for treasury container provisioning."""

    code: str
    name: str
    account_type: str
    control_id: uuid.UUID
    currency: str


class FinCoreProvisioningService:
    """
    Automatically provisions default financial accounts and treasury containers
    for all tenants activating the protected FIN_CORE capability.
    """

    DEFAULT_DRAWER_CODE = "TACC-DRAWER-01"
    DEFAULT_BANK_CODE = "TACC-BANK-01"

    @classmethod
    @transaction.atomic
    def provision_tenant_fin_core(
        cls,
        tenant_id: uuid.UUID,
        base_currency: str = "USD",
    ) -> tuple[TreasuryAccount, TreasuryAccount]:
        """Provisions 2 default TreasuryAccount containers."""
        drawer_acc, bank_acc = cls._provision_control_accounts(tenant_id, base_currency)
        return cls._provision_containers(tenant_id, drawer_acc, bank_acc, base_currency)

    @classmethod
    def _provision_control_accounts(
        cls, tenant_id: uuid.UUID, curr: str
    ) -> tuple[LedgerAccount, LedgerAccount]:
        d = cls._get_or_create_ledger_account(
            tenant_id,
            LedgerAccountSpec(
                "1010", "POS Cash Drawer Control", LedgerAccount.AccountType.ASSET, curr
            ),
        )
        b = cls._get_or_create_ledger_account(
            tenant_id,
            LedgerAccountSpec(
                "1020", "Operating Bank Control", LedgerAccount.AccountType.ASSET, curr
            ),
        )
        cls._get_or_create_ledger_account(
            tenant_id,
            LedgerAccountSpec(
                "5080", "Cash Shortage Expense", LedgerAccount.AccountType.EXPENSE, curr
            ),
        )
        cls._get_or_create_ledger_account(
            tenant_id,
            LedgerAccountSpec(
                "4080", "Cash Overage Revenue", LedgerAccount.AccountType.REVENUE, curr
            ),
        )
        return d, b

    @classmethod
    def _provision_containers(
        cls, tenant_id: uuid.UUID, drawer: LedgerAccount, bank: LedgerAccount, curr: str
    ) -> tuple[TreasuryAccount, TreasuryAccount]:
        pos = cls._get_or_create_treasury_container(
            tenant_id,
            TreasuryContainerSpec(
                cls.DEFAULT_DRAWER_CODE,
                "Front Counter POS Cash Drawer",
                TreasuryAccount.AccountType.CASH_DRAWER,
                drawer.id,
                curr,
            ),
        )
        op_bank = cls._get_or_create_treasury_container(
            tenant_id,
            TreasuryContainerSpec(
                cls.DEFAULT_BANK_CODE,
                "Primary Operating Bank Account",
                TreasuryAccount.AccountType.BANK_ACCOUNT,
                bank.id,
                curr,
            ),
        )
        return pos, op_bank

    @classmethod
    def _get_or_create_ledger_account(
        cls, tenant_id: uuid.UUID, spec: LedgerAccountSpec
    ) -> LedgerAccount:
        acc, _ = LedgerAccount.objects.get_or_create(
            tenant_id=tenant_id,
            account_code=spec.code,
            defaults={
                "account_name": spec.name,
                "account_type": spec.account_type,
                "currency": spec.currency,
                "is_active": True,
            },
        )
        return acc

    @classmethod
    def _get_or_create_treasury_container(
        cls, tenant_id: uuid.UUID, spec: TreasuryContainerSpec
    ) -> TreasuryAccount:
        container, _ = TreasuryAccount.objects.get_or_create(
            tenant_id=tenant_id,
            account_code=spec.code,
            defaults={
                "account_name": spec.name,
                "account_type": spec.account_type,
                "control_ledger_account_id": spec.control_id,
                "current_balance": Decimal("0.0000"),
                "currency": spec.currency,
                "is_active": True,
            },
        )
        return container
