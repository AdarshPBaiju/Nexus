"""
nexus.engines.taxation.service - Jurisdiction-Agnostic Tax Calculation Engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal

from nexus.libs.money.money import Money


@dataclass(frozen=True)
class TaxCalculationResult:
    """Breakdown of calculated net, tax, and gross amounts."""

    net_money: Money
    tax_money: Money
    gross_money: Money
    effective_rate: Decimal
    is_inclusive: bool


class TaxCalculationEngine:
    """
    Evaluates net, tax, and gross totals with exact Bankers Rounding.
    Handles both tax-inclusive and tax-exclusive items.
    """

    @classmethod
    def calculate_tax(
        cls,
        base_money: Money,
        rate_percentage: Decimal,
        is_inclusive: bool,
    ) -> TaxCalculationResult:
        """
        Calculates exact tax breakdown:
        - If exclusive: Gross = Base + (Base * Rate / 100)
        - If inclusive: Net = Base / (1 + Rate / 100); Tax = Base - Net
        """
        rate_fraction = rate_percentage / Decimal("100.0")

        if is_inclusive:
            gross = base_money.amount
            net = (gross / (Decimal("1.0") + rate_fraction)).quantize(
                Decimal("0.0001"),
                rounding=ROUND_HALF_EVEN,
            )
            tax = (gross - net).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
            return TaxCalculationResult(
                net_money=Money.of(net, base_money.currency),
                tax_money=Money.of(tax, base_money.currency),
                gross_money=Money.of(gross, base_money.currency),
                effective_rate=rate_percentage,
                is_inclusive=True,
            )
        else:
            net = base_money.amount
            tax = (net * rate_fraction).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
            gross = (net + tax).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
            return TaxCalculationResult(
                net_money=Money.of(net, base_money.currency),
                tax_money=Money.of(tax, base_money.currency),
                gross_money=Money.of(gross, base_money.currency),
                effective_rate=rate_percentage,
                is_inclusive=False,
            )
