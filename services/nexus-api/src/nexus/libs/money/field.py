"""
nexus.libs.money.field - Django Model Field for Money amounts.
"""
from __future__ import annotations

from decimal import Decimal

from django.db import models


class MoneyField(models.DecimalField):
    """
    Standard monetary decimal field: max_digits=18, decimal_places=4.
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("max_digits", 18)
        kwargs.setdefault("decimal_places", 4)
        kwargs.setdefault("default", Decimal("0.0000"))
        super().__init__(*args, **kwargs)
