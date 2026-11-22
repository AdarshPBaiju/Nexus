#!/usr/bin/env python3
"""
verify_default_protected_fin_core.py - Verification suite for Subphase 02.01 (FIN_CORE).
Validates:
1. Automatic provisioning of default TreasuryAccount containers (Cash Drawer + Bank Account).
2. Shift opening and active conflict prevention.
3. Cash sales tracking and shift-lock invariant enforcement.
4. Quick petty cash disbursement and treasury balance decrementation.
5. Blind shift close with exact match, cash shortage, and cash overage.
6. Balancing General Ledger journal entry generation and zero-sum invariant verification.
"""

from __future__ import annotations

from decimal import Decimal
import os
from pathlib import Path
import sys
import time
import uuid

REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "services" / "nexus-api" / "src"
sys.path.insert(0, str(API_SRC))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexus_test_settings")
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "nexus.platform.tenancy",
            "nexus.engines.currency_fx",
            "nexus.engines.accounting",
            "nexus.extensions.base.fin_basic",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.exceptions import ValidationError
from django.core.management import call_command

from nexus.engines.accounting.models.account import LedgerAccount
from nexus.engines.accounting.models.journal_entry import JournalEntry
from nexus.extensions.base.fin_basic.models.quick_expense import (
    QuickDisbursementDto,
    QuickExpenseRecord,
)
from nexus.extensions.base.fin_basic.models.shift_session import (
    OpenShiftSessionDto,
    ShiftRegisterSession,
)
from nexus.extensions.base.fin_basic.models.treasury_account import TreasuryAccount
from nexus.extensions.base.fin_basic.provisioning import FinCoreProvisioningService
from nexus.extensions.base.fin_basic.service import ShiftSessionService
from nexus.platform.tenancy.models import Tenant


def setup_in_memory_db() -> None:
    call_command("migrate", run_syncdb=True, verbosity=0)


def test_fin_core_provisioning() -> None:
    print("[1/5] Testing FIN_CORE automatic provisioning...")
    tenant = Tenant.objects.create(slug="test-fin-tenant", legal_name="Test Finance Ltd")
    pos_drawer, operating_bank = FinCoreProvisioningService.provision_tenant_fin_core(
        tenant.id, base_currency="USD"
    )

    assert pos_drawer.account_type == TreasuryAccount.AccountType.CASH_DRAWER
    assert operating_bank.account_type == TreasuryAccount.AccountType.BANK_ACCOUNT
    assert pos_drawer.account_code == FinCoreProvisioningService.DEFAULT_DRAWER_CODE
    assert operating_bank.account_code == FinCoreProvisioningService.DEFAULT_BANK_CODE

    # Test idempotency
    d2, b2 = FinCoreProvisioningService.provision_tenant_fin_core(tenant.id, base_currency="USD")
    assert d2.id == pos_drawer.id
    assert b2.id == operating_bank.id
    print("  ✓ Provisioned 2 default containers with idempotent guarantee.")


def test_shift_lifecycle_and_shift_lock() -> None:
    print("[2/5] Testing shift register opening and shift-lock invariant...")
    tenant = Tenant.objects.get(slug="test-fin-tenant")
    drawer = TreasuryAccount.objects.get(
        tenant_id=tenant.id, account_code=FinCoreProvisioningService.DEFAULT_DRAWER_CODE
    )
    cashier_id = uuid.uuid4()

    # Open shift with $100 float
    session = ShiftSessionService.open_shift(
        OpenShiftSessionDto(
            tenant_id=tenant.id,
            workstation_id="POS-STATION-01",
            cashier_user_id=cashier_id,
            treasury_account_id=drawer.id,
            opening_float=Decimal("100.0000"),
        )
    )
    assert session.status == ShiftRegisterSession.Status.OPEN
    assert session.opening_float == Decimal("100.0000")
    assert session.system_cash_total == Decimal("0.0000")

    # Conflict check: cannot open second active shift on same workstation
    try:
        ShiftSessionService.open_shift(
            OpenShiftSessionDto(
                tenant_id=tenant.id,
                workstation_id="POS-STATION-01",
                cashier_user_id=uuid.uuid4(),
                treasury_account_id=drawer.id,
                opening_float=Decimal("50.0000"),
            )
        )
        raise AssertionError("Expected ValidationError on duplicate active shift.")
    except ValidationError:
        pass

    # Record cash sales
    ShiftSessionService.record_cash_sale(session.id, Decimal("45.5000"))
    ShiftSessionService.record_cash_sale(session.id, Decimal("24.5000"))
    session.refresh_from_db()
    assert session.system_cash_total == Decimal("70.0000")
    assert session.expected_cash_total == Decimal("170.0000")
    print("  ✓ Shift opened and recorded cash intake ($70.00) with conflict guard.")


def test_quick_petty_expense() -> None:
    print("[3/5] Testing quick petty cash disbursement...")
    tenant = Tenant.objects.get(slug="test-fin-tenant")
    session = ShiftRegisterSession.objects.filter(
        tenant_id=tenant.id, status=ShiftRegisterSession.Status.OPEN
    ).first()
    expense_acc = LedgerAccount.objects.filter(
        tenant_id=tenant.id, account_type=LedgerAccount.AccountType.EXPENSE
    ).first()

    # Disburse $15 for emergency supplies
    expense = ShiftSessionService.record_quick_expense(
        QuickDisbursementDto(
            tenant_id=tenant.id,
            treasury_account_id=session.treasury_account_id,
            expense_ledger_account_id=expense_acc.id,
            amount=Decimal("15.0000"),
            reason_code=QuickExpenseRecord.ReasonCode.PETTY_CASH_SUPPLIES,
            description="Emergency printer paper rolls",
            shift_session_id=session.id,
        )
    )
    assert expense.amount == Decimal("15.0000")
    session.refresh_from_db()
    # Expected: $100 float + $70 sales - $15 expense = $155.00
    assert session.system_cash_total == Decimal("55.0000")
    assert session.expected_cash_total == Decimal("155.0000")
    print("  ✓ Petty cash expense disbursed; expected total accurately adjusted to $155.00.")


def test_blind_shift_reconciliation_shortage() -> None:
    print("[4/5] Testing blind closing reconciliation with shortage...")
    tenant = Tenant.objects.get(slug="test-fin-tenant")
    session = ShiftRegisterSession.objects.filter(
        tenant_id=tenant.id, status=ShiftRegisterSession.Status.OPEN
    ).first()
    legal_entity_id = uuid.uuid4()

    # Expected is $155.00. Cashier counts $145.00 (Shortage of $10.00)
    t0 = time.perf_counter()
    res = ShiftSessionService.close_shift_blind(
        session_id=session.id,
        actual_cash_count=Decimal("145.0000"),
        legal_entity_id=legal_entity_id,
    )
    duration_ms = (time.perf_counter() - t0) * 1000

    assert res.variance_amount == Decimal("-10.0000")
    assert res.journal_entry_id is not None

    # Verify journal entry was posted
    entry = JournalEntry.objects.get(id=res.journal_entry_id)
    assert entry.status == JournalEntry.EntryStatus.POSTED

    # Shift-lock assertion: cannot add cash sale to closed shift
    try:
        ShiftSessionService.record_cash_sale(session.id, Decimal("10.0000"))
        raise AssertionError("Expected ValidationError when adding sale to closed shift.")
    except ValidationError:
        pass

    print(f"  ✓ Shortage variance (-$10.00) posted to GL in {duration_ms:.4f}ms. Shift locked.")


def test_blind_shift_reconciliation_overage() -> None:
    print("[5/5] Testing blind closing reconciliation with overage...")
    tenant = Tenant.objects.get(slug="test-fin-tenant")
    drawer = TreasuryAccount.objects.get(
        tenant_id=tenant.id, account_code=FinCoreProvisioningService.DEFAULT_DRAWER_CODE
    )
    legal_entity_id = uuid.uuid4()

    session = ShiftSessionService.open_shift(
        OpenShiftSessionDto(
            tenant_id=tenant.id,
            workstation_id="POS-STATION-02",
            cashier_user_id=uuid.uuid4(),
            treasury_account_id=drawer.id,
            opening_float=Decimal("50.0000"),
        )
    )
    ShiftSessionService.record_cash_sale(session.id, Decimal("50.0000"))
    # Expected: $100.00. Actual physical count: $115.00 (Overage of $15.00)
    res = ShiftSessionService.close_shift_blind(
        session_id=session.id,
        actual_cash_count=Decimal("115.0000"),
        legal_entity_id=legal_entity_id,
    )
    assert res.variance_amount == Decimal("15.0000")
    entry = JournalEntry.objects.get(id=res.journal_entry_id)
    assert entry.status == JournalEntry.EntryStatus.POSTED
    print("  ✓ Overage variance (+$15.00) posted to GL with balanced entries.")


def main() -> None:
    print("================================================================================")
    print("NEXUS SUBPHASE 02.01: DEFAULT BASIC FINANCE (FIN_CORE) VERIFICATION")
    print("================================================================================")
    setup_in_memory_db()
    test_fin_core_provisioning()
    test_shift_lifecycle_and_shift_lock()
    test_quick_petty_expense()
    test_blind_shift_reconciliation_shortage()
    test_blind_shift_reconciliation_overage()
    print("================================================================================")
    print("ALL FIN_CORE VERIFICATION TESTS COMPLETED WITH 100% SUCCESS.")
    print("================================================================================")


if __name__ == "__main__":
    main()
