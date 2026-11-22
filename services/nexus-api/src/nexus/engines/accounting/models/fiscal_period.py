"""
nexus.engines.accounting.models.fiscal_period - Fiscal Accounting Period and Lockout model.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class FiscalPeriod(TenantScopedModel):
    """
    Statutory accounting period enforcing calendar lockouts and preventing backdated entries.
    """

    class PeriodStatus(models.TextChoices):
        PLANNED = "PLANNED", _("Planned")
        OPEN = "OPEN", _("Open for Postings")
        CLOSING_IN_PROGRESS = "CLOSING_IN_PROGRESS", _("Closing in Progress")
        LOCKED = "LOCKED", _("Locked / Closed")
        AUDITED_FINAL = "AUDITED_FINAL", _("Audited Final")

    legal_entity_id = models.UUIDField(
        db_index=True,
        help_text=_("Legal entity governed by this accounting period."),
    )
    period_code = models.CharField(
        max_length=32,
        db_index=True,
        help_text=_("Period code (e.g. FY2026-Q1, 2026-03)."),
    )
    start_date = models.DateField(
        help_text=_("Calendar start date of the period."),
    )
    end_date = models.DateField(
        help_text=_("Calendar end date of the period."),
    )
    status = models.CharField(
        max_length=32,
        choices=PeriodStatus.choices,
        default=PeriodStatus.OPEN,
        db_index=True,
    )

    class Meta:
        app_label = "accounting"
        db_table = "acc_fiscal_period"
        unique_together = [("tenant_id", "legal_entity_id", "period_code")]
        ordering = ["-start_date", "id"]

    @property
    def is_locked_for_posting(self) -> bool:
        return self.status in {self.PeriodStatus.LOCKED, self.PeriodStatus.AUDITED_FINAL}

    def __str__(self) -> str:
        return f"FiscalPeriod({self.period_code} : {self.status})"
