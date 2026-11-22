"""
nexus.engines.accounting.service - General Ledger Posting Service with Invariant & Lock Enforcement.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from nexus.engines.accounting.models.account import LedgerAccount
from nexus.engines.accounting.models.fiscal_period import FiscalPeriod
from nexus.engines.accounting.models.journal_entry import JournalEntry
from nexus.engines.accounting.models.journal_line import JournalLine


@dataclass(frozen=True)
class JournalLineDto:
    """Input specification for a single debit or credit line."""

    account_id: uuid.UUID
    debit: Decimal
    credit: Decimal
    currency: str
    fx_rate: Decimal
    functional_debit: Decimal
    functional_credit: Decimal


class LedgerPostingService:
    """
    Coordinates posting of journal entries to the General Ledger with:
    1. Zero-sum balancing invariant assertion in transaction and functional currencies.
    2. Fiscal period lockout verification.
    3. Canonical ascending lock acquisition (ORDER BY id ASC) to eliminate deadlocks.
    4. Immutability protection against post-mutation.
    """

    @classmethod
    def assert_zero_sum_balance(cls, lines: Sequence[JournalLineDto]) -> None:
        """Enforces: Sum(Debit) == Sum(Credit) in transaction and functional currencies."""
        total_tx_dr = sum((line.debit for line in lines), Decimal("0.0000"))
        total_tx_cr = sum((line.credit for line in lines), Decimal("0.0000"))
        total_fn_dr = sum((line.functional_debit for line in lines), Decimal("0.0000"))
        total_fn_cr = sum((line.functional_credit for line in lines), Decimal("0.0000"))

        if total_tx_dr != total_tx_cr:
            raise ValidationError(
                f"Imbalanced transaction currency: Debit ({total_tx_dr}) != Credit ({total_tx_cr})"
            )
        if total_fn_dr != total_fn_cr:
            raise ValidationError(
                f"Imbalanced functional currency: Debit ({total_fn_dr}) != Credit ({total_fn_cr})"
            )

    @classmethod
    def assert_period_open(cls, tenant_id: uuid.UUID, legal_entity_id: uuid.UUID, posting_date) -> None:
        """Asserts posting date does not fall within a locked fiscal period."""
        locked_periods = FiscalPeriod.objects.filter(
            tenant_id=tenant_id,
            legal_entity_id=legal_entity_id,
            start_date__lte=posting_date,
            end_date__gte=posting_date,
            status__in=[FiscalPeriod.PeriodStatus.LOCKED, FiscalPeriod.PeriodStatus.AUDITED_FINAL],
        )
        if locked_periods.exists():
            raise ValidationError("FiscalPeriodClosedError: Posting to a locked fiscal period is strictly prohibited.")

    @classmethod
    @transaction.atomic
    def post_journal_entry(
        cls,
        entry: JournalEntry,
        lines: Sequence[JournalLineDto],
    ) -> JournalEntry:
        """
        Atomically posts journal lines with canonical lock ordering and balance checks.
        """
        if entry.status == JournalEntry.EntryStatus.POSTED:
            raise ValidationError("POSTED_GL_ENTRY_IMMUTABLE: Cannot modify an already posted journal.")

        cls.assert_zero_sum_balance(lines)
        now_date = timezone.now().date()
        cls.assert_period_open(entry.tenant_id, entry.legal_entity_id, now_date)

        # Canonical lock acquisition: Sort account IDs in ASC order before locking
        account_ids = sorted([line.account_id for line in lines])
        list(
            LedgerAccount.objects.select_for_update()
            .filter(tenant_id=entry.tenant_id, id__in=account_ids)
            .order_by("id")
        )

        for line_dto in lines:
            account = LedgerAccount.objects.get(id=line_dto.account_id)
            JournalLine.objects.create(
                journal_entry=entry,
                ledger_account=account,
                debit_amount=line_dto.debit,
                credit_amount=line_dto.credit,
                currency=line_dto.currency,
                fx_rate_snapshot=line_dto.fx_rate,
                functional_debit=line_dto.functional_debit,
                functional_credit=line_dto.functional_credit,
            )

        entry.status = JournalEntry.EntryStatus.POSTED
        entry.posted_at = timezone.now()
        entry.save(update_fields=["status", "posted_at", "updated_at"])
        return entry
