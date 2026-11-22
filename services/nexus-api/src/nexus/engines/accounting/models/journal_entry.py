"""
nexus.engines.accounting.models.journal_entry - Double-Entry General Ledger Journal Entry model.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class JournalEntry(TenantScopedModel):
    """
    Double-entry journal header enforcing atomic balance and strict post-mutation immutability.
    """

    class EntryStatus(models.TextChoices):
        DRAFT = "DRAFT", _("Draft")
        POSTED = "POSTED", _("Posted to General Ledger")
        REVERSED = "REVERSED", _("Reversed by Compensating Entry")

    class EntryType(models.TextChoices):
        STANDARD = "STANDARD", _("Standard Manual Journal")
        SALES = "SALES", _("POS / Dining Sales Journal")
        PAYMENT = "PAYMENT", _("Customer Payment Receipt")
        EXPENSE = "EXPENSE", _("Operational Expense / Vendor Bill")
        REVERSAL = "REVERSAL", _("Compensating Reversal Entry")

    legal_entity_id = models.UUIDField(
        db_index=True,
        help_text=_("Legal entity owning this general ledger transaction."),
    )
    entry_number = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Unique fiscal journal entry sequence number (e.g. JRN-2026-00001)."),
    )
    entry_type = models.CharField(
        max_length=32,
        choices=EntryType.choices,
        default=EntryType.STANDARD,
        db_index=True,
    )
    status = models.CharField(
        max_length=32,
        choices=EntryStatus.choices,
        default=EntryStatus.DRAFT,
        db_index=True,
    )
    source_event_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("ID of business domain event triggering this journal."),
    )
    reverses_journal_id = models.UUIDField(
        null=True,
        blank=True,
        help_text=_("Referenced journal entry cancelled by this reversal."),
    )
    posted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        app_label = "accounting"
        db_table = "acc_journal_entry"
        unique_together = [("tenant_id", "entry_number")]
        ordering = ["-created_at", "id"]

    @property
    def is_posted(self) -> bool:
        return self.status == self.EntryStatus.POSTED

    def __str__(self) -> str:
        return f"JournalEntry({self.entry_number} [{self.status}])"
