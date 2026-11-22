"""
nexus.engines.accounting.models.account - Chart of Accounts (CoA) Ledger Account model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class LedgerAccount(TenantScopedModel):
    """
    Fundamental Chart of Accounts (CoA) ledger account belonging to one of the 5 root categories.
    """

    class AccountType(models.TextChoices):
        ASSET = "ASSET", _("Asset (Normal Balance: DEBIT)")
        LIABILITY = "LIABILITY", _("Liability (Normal Balance: CREDIT)")
        EQUITY = "EQUITY", _("Equity (Normal Balance: CREDIT)")
        REVENUE = "REVENUE", _("Revenue (Normal Balance: CREDIT)")
        EXPENSE = "EXPENSE", _("Expense (Normal Balance: DEBIT)")

    account_code = models.CharField(
        max_length=32,
        db_index=True,
        help_text=_("Standard Chart of Accounts code (e.g. 1010-CASH, 4010-SALES)."),
    )
    account_name = models.CharField(
        max_length=128,
        help_text=_("Human-readable account title."),
    )
    account_type = models.CharField(
        max_length=16,
        choices=AccountType.choices,
        db_index=True,
        help_text=_("Primary financial category governing normal balance."),
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        help_text=_("Nominal currency of this ledger account."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Designates whether new postings can target this account."),
    )

    class Meta:
        app_label = "accounting"
        db_table = "acc_ledger_account"
        unique_together = [("tenant_id", "account_code")]
        ordering = ["account_code", "id"]

    def __str__(self) -> str:
        return f"Account({self.account_code} - {self.account_name} [{self.account_type}])"
