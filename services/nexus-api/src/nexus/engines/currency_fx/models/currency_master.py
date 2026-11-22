"""
nexus.engines.currency_fx.models.currency_master - Supported ISO 4217 Currency catalog model.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.ids import new_uuid7


class CurrencyMaster(models.Model):
    """
    Catalog of supported ISO 4217 currencies with minor unit decimals and symbols.
    """

    id = models.UUIDField(
        primary_key=True,
        default=new_uuid7,
        editable=False,
    )
    code = models.CharField(
        max_length=3,
        unique=True,
        db_index=True,
        help_text=_("3-letter ISO 4217 currency code (e.g. USD, EUR, AED, INR, JPY)."),
    )
    minor_unit_decimals = models.PositiveSmallIntegerField(
        default=2,
        help_text=_("Number of decimal digits for minor currency unit (0 for JPY, 3 for KWD)."),
    )
    symbol = models.CharField(
        max_length=8,
        help_text=_("Display symbol (e.g. $, €, د.إ, ₹, ¥)."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Designates whether this currency is actively transactable."),
    )

    class Meta:
        app_label = "currency_fx"
        db_table = "cur_currency_master"
        ordering = ["code"]

    def __str__(self) -> str:
        return f"Currency({self.code} [{self.symbol}])"
