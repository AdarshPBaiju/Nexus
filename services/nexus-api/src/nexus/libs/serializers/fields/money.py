"""
nexus.libs.serializers.fields.money - Exact monetary and currency code fields.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from rest_framework import serializers


class IsoMoneyField(serializers.Field):
    """Serializes and deserializes exact string decimal money object."""

    def to_representation(self, value: Any) -> dict[str, str]:
        if hasattr(value, "amount") and hasattr(value, "currency"):
            return {"amount": str(value.amount), "currency": str(value.currency)}
        if isinstance(value, dict):
            return {
                "amount": str(value.get("amount", "0.00")),
                "currency": str(value.get("currency", "USD")),
            }
        return {"amount": str(value or "0.00"), "currency": "USD"}

    def to_internal_value(self, data: Any) -> dict[str, str]:
        if not isinstance(data, dict):
            raise serializers.ValidationError("Money must be a dict with amount and currency")
        amount_raw = data.get("amount")
        currency_raw = data.get("currency", "USD")
        try:
            dec = Decimal(str(amount_raw))
        except (InvalidOperation, TypeError) as exc:
            raise serializers.ValidationError("Invalid decimal money amount") from exc
        return {"amount": f"{dec:.2f}", "currency": str(currency_raw).upper()}


class IsoCurrencyCodeField(serializers.CharField):
    """ISO 4217 3-letter uppercase currency code."""

    def to_internal_value(self, data: Any) -> str:
        val = super().to_internal_value(data).upper().strip()
        if len(val) != 3 or not val.isalpha():
            raise serializers.ValidationError("Currency must be a 3-letter ISO 4217 code")
        return val


class ZonedRateDecimalField(serializers.Field):
    """Exact decimal field with 4-decimal place precision for rates."""

    def to_representation(self, value: Any) -> str:
        return f"{Decimal(str(value)):.4f}"

    def to_internal_value(self, data: Any) -> Decimal:
        try:
            return Decimal(str(data))
        except (InvalidOperation, TypeError) as exc:
            raise serializers.ValidationError("Invalid rate decimal value") from exc
