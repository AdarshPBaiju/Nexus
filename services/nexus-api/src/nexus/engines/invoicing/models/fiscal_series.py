"""
nexus.engines.invoicing.models.fiscal_series - Gapless Monotonic Fiscal Number Series Model.
"""

from __future__ import annotations

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


class FiscalSeries(TenantScopedModel):
    """
    Allocates gapless sequential fiscal invoice and receipt numbers using serialized row locks.
    """

    legal_entity_id = models.UUIDField(
        db_index=True,
        help_text=_("Legal entity owning this fiscal series."),
    )
    branch_id = models.UUIDField(
        db_index=True,
        help_text=_("Operating branch or store UUID."),
    )
    fiscal_year = models.IntegerField(
        db_index=True,
        help_text=_("Calendar or financial fiscal year (e.g. 2026)."),
    )
    series_code = models.CharField(
        max_length=32,
        db_index=True,
        help_text=_("Series identifier (e.g. TAX_INV, POS_RECEIPT, CREDIT_NOTE)."),
    )
    prefix = models.CharField(
        max_length=32,
        help_text=_("Prefix string (e.g. 'INV-2026-')."),
    )
    current_number = models.IntegerField(
        default=0,
        help_text=_("Monotonically increasing integer sequence counter."),
    )
    padding = models.IntegerField(
        default=6,
        help_text=_("Zero-padding width (e.g. 6 -> 000001)."),
    )

    class Meta:
        app_label = "invoicing"
        db_table = "inv_fiscal_series"
        unique_together = [
            ("tenant_id", "legal_entity_id", "branch_id", "fiscal_year", "series_code")
        ]
        ordering = ["series_code", "id"]

    def allocate_next(self) -> str:
        """
        Locks the series row, increments counter, and returns formatted gapless number.
        """
        with transaction.atomic():
            locked = FiscalSeries.objects.select_for_update().get(id=self.id)
            locked.current_number += 1
            locked.save(update_fields=["current_number", "updated_at"])
            self.current_number = locked.current_number
            return f"{self.prefix}{self.current_number:0{self.padding}d}"

    def __str__(self) -> str:
        return f"FiscalSeries({self.series_code} [curr={self.current_number}])"
