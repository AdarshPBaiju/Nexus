"""
nexus.engines.accounting.models.journal_line - Atomic General Ledger Journal Line model.
"""
from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.engines.accounting.models.account import LedgerAccount
from nexus.engines.accounting.models.journal_entry import JournalEntry
from nexus.libs.ids import new_uuid7


class JournalLine(models.Model):
    """
    Individual debit or credit posting leg of a balanced journal entry.
    """

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name="lines",
        help_text=_("Journal header owning this line leg."),
    )
    ledger_account = models.ForeignKey(
        LedgerAccount,
        on_delete=models.PROTECT,
        related_name="journal_lines",
        help_text=_("Chart of accounts target for this debit/credit."),
    )
    debit_amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )
    credit_amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
    )
    fx_rate_snapshot = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        default=Decimal("1.00000000"),
    )
    functional_debit = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )
    functional_credit = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )

    class Meta:
        app_label = "accounting"
        db_table = "acc_journal_line"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"Line({self.journal_entry_id} -> {self.ledger_account.account_code}: DR {self.debit_amount} / CR {self.credit_amount})"
