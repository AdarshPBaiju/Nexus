"""
nexus.engines.currency_fx.service - Multi-Currency Tri-Currency Calculation Service.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal

from nexus.libs.money.money import Money


@dataclass(frozen=True)
class FxRatePair:
    """Pair of exchange rates from transaction currency to account and functional currencies."""

    account_currency: str
    functional_currency: str
    rate_tx_to_acc: Decimal
    rate_tx_to_fn: Decimal


@dataclass(frozen=True)
class TriCurrencyRecord:
    """
    Financial record captured across all 3 currency dimensions.
    """

    transaction_money: Money
    account_money: Money
    functional_money: Money
    fx_rate_tx_to_fn: Decimal


class CurrencyFxService:
    """
    Coordinates multi-currency conversions across transaction, account, and functional currencies.
    """

    @classmethod
    def convert_amount(
        cls,
        source_money: Money,
        target_currency: str,
        rate: Decimal,
    ) -> Money:
        """Converts Money to target currency using exact exchange rate and Bankers rounding."""
        if source_money.currency == target_currency:
            return source_money

        converted_amount = (source_money.amount * rate).quantize(
            Decimal("0.0001"),
            rounding=ROUND_HALF_EVEN,
        )
        return Money.of(converted_amount, target_currency)

    @classmethod
    def compute_tri_currency_record(
        cls,
        tx_money: Money,
        rates: FxRatePair,
    ) -> TriCurrencyRecord:
        """Produces tri-currency representation for double-entry ledger lines."""
        acc_money = cls.convert_amount(tx_money, rates.account_currency, rates.rate_tx_to_acc)
        fn_money = cls.convert_amount(tx_money, rates.functional_currency, rates.rate_tx_to_fn)
        return TriCurrencyRecord(
            transaction_money=tx_money,
            account_money=acc_money,
            functional_money=fn_money,
            fx_rate_tx_to_fn=rates.rate_tx_to_fn,
        )

