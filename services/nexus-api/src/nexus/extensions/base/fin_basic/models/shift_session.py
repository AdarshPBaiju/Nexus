"""
nexus.extensions.base.fin_basic.models.shift_session - Physical cashier register shift session.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


@dataclass(frozen=True)
class OpenShiftSessionDto:
    """Parameter object for opening a register shift session."""

    tenant_id: uuid.UUID
    workstation_id: str
    cashier_user_id: uuid.UUID
    treasury_account_id: uuid.UUID
    opening_float: Decimal = Decimal("0.0000")


class ShiftRegisterSession(TenantScopedModel):
    """
    Tracks physical cash drawer shift sessions from opening float
    through blind closing cash count and variance reconciliation.
    """

    class Status(models.TextChoices):
        OPEN = "OPEN", _("Open Active Shift")
        CLOSED = "CLOSED", _("Closed & Reconciled")
        RECONCILED = "RECONCILED", _("Audited & Finalized")

    workstation_id = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Hardware workstation or POS station identifier."),
    )
    cashier_user_id = models.UUIDField(
        db_index=True,
        help_text=_("Staff member operating register session."),
    )
    treasury_account_id = models.UUIDField(
        db_index=True,
        help_text=_("Foreign key to physical cash drawer container."),
    )
    opened_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text=_("Timestamp when opening float was counted and drawer opened."),
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Timestamp when blind close was recorded."),
    )
    opening_float = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text=_("Starting cash balance in drawer at shift start."),
    )
    system_cash_total = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text=_("Net cash intake calculated by system (cash sales - petty expenses)."),
    )
    actual_cash_count = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        null=True,
        blank=True,
        help_text=_("Cashier blind physical count at shift close."),
    )
    variance_amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        null=True,
        blank=True,
        help_text=_("Computed variance: actual_cash_count - (opening_float + system_cash_total)."),
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    variance_journal_entry_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Balancing General Ledger journal entry correcting cash shortage/overage."),
    )

    class Meta:
        app_label = "nexus_fin_basic"
        db_table = "fin_shift_register_session"
        ordering = ["-opened_at", "id"]
        indexes = [
            models.Index(fields=["tenant_id", "status", "opened_at"]),
            models.Index(fields=["workstation_id", "status"]),
        ]

    @classmethod
    def open_session(cls, dto: OpenShiftSessionDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            workstation_id=dto.workstation_id,
            cashier_user_id=dto.cashier_user_id,
            treasury_account_id=dto.treasury_account_id,
            opening_float=dto.opening_float,
            status=cls.Status.OPEN,
        )

    @property
    def is_active(self) -> bool:
        return self.status == self.Status.OPEN

    @property
    def expected_cash_total(self) -> Decimal:
        return self.opening_float + self.system_cash_total

    def __str__(self) -> str:
        return f"ShiftSession({self.id}, station={self.workstation_id}, status={self.status})"
