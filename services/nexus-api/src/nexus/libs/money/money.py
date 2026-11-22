"""
nexus.libs.money.money - Exact string-decimal ISO 4217 Money value object.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Self


@dataclass(frozen=True)
class Money:
    """
    Immutable value object representing exact monetary amount in an ISO 4217 currency.
    Eliminates floating-point drift using decimal.Decimal with Bankers Rounding.
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not self.currency or len(self.currency) != 3:
            raise ValueError(f"Invalid ISO 4217 currency code: '{self.currency}'")
        object.__setattr__(self, "currency", self.currency.upper())
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))

    @classmethod
    def of(cls, amount: str | int | float | Decimal, currency: str) -> Self:
        dec = Decimal(str(amount)) if not isinstance(amount, Decimal) else amount
        return cls(amount=dec, currency=currency)

    @classmethod
    def zero(cls, currency: str) -> Self:
        return cls(amount=Decimal("0.0000"), currency=currency)

    def _assert_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(
                f"Currency mismatch: cannot operate between {self.currency} and {other.currency}"
            )

    def add(self, other: Money) -> Self:
        self._assert_same_currency(other)
        return self.__class__(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: Money) -> Self:
        self._assert_same_currency(other)
        return self.__class__(amount=self.amount - other.amount, currency=self.currency)

    def multiply(self, factor: int | float | str | Decimal) -> Self:
        dec_factor = Decimal(str(factor)) if not isinstance(factor, Decimal) else factor
        return self.__class__(amount=self.amount * dec_factor, currency=self.currency)

    def is_zero(self) -> bool:
        return self.amount == Decimal("0.0000") or self.amount == Decimal(0)

    def round_to_scale(self, scale: int = 4) -> Self:
        exp = Decimal(10) ** -scale
        rounded = self.amount.quantize(exp, rounding=ROUND_HALF_EVEN)
        return self.__class__(amount=rounded, currency=self.currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.4f}"
