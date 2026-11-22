"""
nexus.engines.currency_fx.models.exchange_rate - Immutable Historical Exchange Rate Snapshot model.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nexus.engines.currency_fx.models.currency_master import CurrencyMaster
from nexus.libs.ids import new_uuid7


class ExchangeRateSnapshot(models.Model):
    """
    Immutable historical exchange rate snapshot with 8 decimal places precision.
    """

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    base_currency = models.ForeignKey(
        CurrencyMaster,
        on_delete=models.PROTECT,
        related_name="rates_as_base",
        help_text=_("Base currency for conversion (usually USD or EUR)."),
    )
    target_currency = models.ForeignKey(
        CurrencyMaster,
        on_delete=models.PROTECT,
        related_name="rates_as_target",
        help_text=_("Target currency being valued."),
    )
    rate = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        help_text=_("Exact exchange rate multiplier: target_amount = base_amount * rate."),
    )
    rate_source = models.CharField(
        max_length=64,
        default="CENTRAL_BANK",
        help_text=_("Source of exchange rate snapshot (e.g. CENTRAL_BANK, OANDA, MANUAL)."),
    )
    valid_from = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )

    class Meta:
        app_label = "currency_fx"
        db_table = "cur_exchange_rate_snapshot"
        ordering = ["-valid_from", "id"]
        indexes = [
            models.Index(fields=["base_currency", "target_currency", "-valid_from"]),
        ]

    def __str__(self) -> str:
        return f"FX({self.base_currency.code} -> {self.target_currency.code} @ {self.rate})"
