"""
nexus.engines.taxation.service - Jurisdiction-Agnostic Tax Calculation Engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Sequence

from nexus.libs.money.money import Money


@dataclass(frozen=True)
class TaxComponent:
    """Individual tax breakdown component (e.g. CGST, SGST, Cess)."""

    name: str
    rate: Decimal
    amount: Money


@dataclass(frozen=True)
class TaxCalculationResult:
    """Breakdown of calculated net, tax, and gross amounts."""

    net_money: Money
    tax_money: Money
    gross_money: Money
    effective_rate: Decimal
    is_inclusive: bool
    components: tuple[TaxComponent, ...] = ()


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

    @classmethod
    def calculate_composite_tax(
        cls,
        base_money: Money,
        components: Sequence[tuple[str, Decimal]],
        is_inclusive: bool,
    ) -> TaxCalculationResult:
        """
        Calculates composite multi-rate tax with penny-accurate component distribution
        (e.g. GST 18% -> CGST 9% + SGST 9%).
        """
        total_rate = sum((rate for _, rate in components), Decimal("0.0"))
        base_res = cls.calculate_tax(base_money, total_rate, is_inclusive)

        comp_list: list[TaxComponent] = []
        if total_rate > Decimal("0.0"):
            for name, rate in components:
                fraction = rate / total_rate
                c_tax = (base_res.tax_money.amount * fraction).quantize(
                    Decimal("0.0001"), rounding=ROUND_HALF_EVEN
                )
                comp_list.append(
                    TaxComponent(name=name, rate=rate, amount=Money.of(c_tax, base_money.currency))
                )

        return TaxCalculationResult(
            net_money=base_res.net_money,
            tax_money=base_res.tax_money,
            gross_money=base_res.gross_money,
            effective_rate=total_rate,
            is_inclusive=is_inclusive,
            components=tuple(comp_list),
        )
