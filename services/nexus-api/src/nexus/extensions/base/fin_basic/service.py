"""
nexus.extensions.base.fin_basic.service - Shift session management and blind reconciliation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from nexus.engines.accounting.models.account import LedgerAccount
from nexus.engines.accounting.models.journal_entry import JournalEntry
from nexus.engines.accounting.service import JournalLineDto, LedgerPostingService
from nexus.extensions.base.fin_basic.models.quick_expense import (
    QuickDisbursementDto,
    QuickExpenseRecord,
)
from nexus.extensions.base.fin_basic.models.shift_session import (
    OpenShiftSessionDto,
    ShiftRegisterSession,
)
from nexus.extensions.base.fin_basic.models.treasury_account import TreasuryAccount


@dataclass(frozen=True)
class ShiftReconciliationResult:
    """Outcome of a blind closing shift reconciliation."""

    session_id: uuid.UUID
    opening_float: Decimal
    system_cash_total: Decimal
    expected_cash_total: Decimal
    actual_cash_count: Decimal
    variance_amount: Decimal
    journal_entry_id: uuid.UUID | None


class ShiftSessionService:
    """
    Coordinates cashier shift register lifecycles, cash movements,
    petty cash disbursements, and blind closing variance accounting.
    """

    @classmethod
    @transaction.atomic
    def open_shift(cls, dto: OpenShiftSessionDto) -> ShiftRegisterSession:
        """Opens a new shift session if none is currently active for workstation."""
        active = ShiftRegisterSession.objects.filter(
            tenant_id=dto.tenant_id,
            workstation_id=dto.workstation_id,
            status=ShiftRegisterSession.Status.OPEN,
        ).exists()
        if active:
            raise ValidationError(
                f"ShiftConflictError: Workstation '{dto.workstation_id}' already has an active OPEN shift."
            )

        session = ShiftRegisterSession.open_session(dto)
        TreasuryAccount.objects.filter(id=dto.treasury_account_id).update(
            current_balance=dto.opening_float
        )
        return session

    @classmethod
    @transaction.atomic
    def record_cash_sale(cls, session_id: uuid.UUID, amount: Decimal) -> ShiftRegisterSession:
        """Records incoming cash transaction, asserting shift-lock invariant."""
        session = cls._get_open_session_for_update(session_id)
        session.system_cash_total += amount
        session.save(update_fields=["system_cash_total", "updated_at"])

        TreasuryAccount.objects.filter(id=session.treasury_account_id).update(
            current_balance=models.F("current_balance") + amount
        )
        return session

    @classmethod
    @transaction.atomic
    def record_quick_expense(cls, dto: QuickDisbursementDto) -> QuickExpenseRecord:
        """Disburses petty cash from drawer, decrementing system cash total."""
        session = cls._get_open_session_for_update(dto.shift_session_id)  # type: ignore[arg-type]
        expense = QuickExpenseRecord.record_disbursement(dto)
        session.system_cash_total -= dto.amount
        session.save(update_fields=["system_cash_total", "updated_at"])

        TreasuryAccount.objects.filter(id=session.treasury_account_id).update(
            current_balance=models.F("current_balance") - dto.amount
        )
        return expense

    @classmethod
    @transaction.atomic
    def close_shift_blind(
        cls,
        session_id: uuid.UUID,
        actual_cash_count: Decimal,
        legal_entity_id: uuid.UUID | None = None,
    ) -> ShiftReconciliationResult:
        """
        Executes blind count close, computes variance, and posts balancing GL entry.
        """
        session = cls._get_open_session_for_update(session_id)
        expected = session.opening_float + session.system_cash_total
        variance = actual_cash_count - expected

        journal_id = cls._post_variance_if_needed(session, variance, legal_entity_id)
        cls._finalize_session(session, actual_cash_count, variance, journal_id)

        return ShiftReconciliationResult(
            session_id=session.id,
            opening_float=session.opening_float,
            system_cash_total=session.system_cash_total,
            expected_cash_total=expected,
            actual_cash_count=actual_cash_count,
            variance_amount=variance,
            journal_entry_id=journal_id,
        )

    @classmethod
    def _get_open_session_for_update(cls, session_id: uuid.UUID) -> ShiftRegisterSession:
        session = ShiftRegisterSession.objects.select_for_update().get(id=session_id)
        if session.status != ShiftRegisterSession.Status.OPEN:
            raise ValidationError(
                "ShiftLockViolation: Closed or reconciled shift sessions cannot receive transactions."
            )
        return session

    @classmethod
    def _post_variance_if_needed(
        cls,
        session: ShiftRegisterSession,
        variance: Decimal,
        legal_entity_id: uuid.UUID | None,
    ) -> uuid.UUID | None:
        if variance == Decimal("0.0000") or legal_entity_id is None:
            return None
        return cls._create_variance_journal(session, variance, legal_entity_id)

    @classmethod
    def _create_variance_journal(
        cls,
        session: ShiftRegisterSession,
        variance: Decimal,
        legal_entity_id: uuid.UUID,
    ) -> uuid.UUID:
        drawer_acc = LedgerAccount.objects.get(tenant_id=session.tenant_id, account_code="1010")
        entry = JournalEntry.objects.create(
            tenant_id=session.tenant_id,
            legal_entity_id=legal_entity_id,
            entry_number=f"JRN-VAR-{uuid.uuid4().hex[:12].upper()}",
            entry_type=JournalEntry.EntryType.STANDARD,
            status=JournalEntry.EntryStatus.DRAFT,
        )
        lines = cls._build_variance_lines(session.tenant_id, drawer_acc, variance)
        LedgerPostingService.post_journal_entry(entry, lines)
        return entry.id

    @classmethod
    def _build_variance_lines(
        cls, tenant_id: uuid.UUID, drawer_acc: LedgerAccount, variance: Decimal
    ) -> list[JournalLineDto]:
        if variance < Decimal("0.0000"):
            shortage_acc = LedgerAccount.objects.get(tenant_id=tenant_id, account_code="5080")
            amt = abs(variance)
            return [
                JournalLineDto(
                    shortage_acc.id, amt, Decimal("0"), "USD", Decimal("1"), amt, Decimal("0")
                ),
                JournalLineDto(
                    drawer_acc.id, Decimal("0"), amt, "USD", Decimal("1"), Decimal("0"), amt
                ),
            ]
        overage_acc = LedgerAccount.objects.get(tenant_id=tenant_id, account_code="4080")
        return [
            JournalLineDto(
                drawer_acc.id, variance, Decimal("0"), "USD", Decimal("1"), variance, Decimal("0")
            ),
            JournalLineDto(
                overage_acc.id, Decimal("0"), variance, "USD", Decimal("1"), Decimal("0"), variance
            ),
        ]

    @classmethod
    def _finalize_session(
        cls,
        session: ShiftRegisterSession,
        actual_cash: Decimal,
        variance: Decimal,
        journal_id: uuid.UUID | None,
    ) -> None:
        session.actual_cash_count = actual_cash
        session.variance_amount = variance
        session.status = ShiftRegisterSession.Status.CLOSED
        session.closed_at = timezone.now()
        session.variance_journal_entry_id = journal_id
        session.save(
            update_fields=[
                "actual_cash_count",
                "variance_amount",
                "status",
                "closed_at",
                "variance_journal_entry_id",
                "updated_at",
            ]
        )
        TreasuryAccount.objects.filter(id=session.treasury_account_id).update(
            current_balance=actual_cash
        )
