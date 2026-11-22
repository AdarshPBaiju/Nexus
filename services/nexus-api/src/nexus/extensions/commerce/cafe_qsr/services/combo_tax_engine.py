"""
nexus.extensions.commerce.cafe_qsr.services.combo_tax_engine - Proportional tax calculation.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


@dataclass(frozen=True)
class ComboItemInputDto:
    """Input parameters for an individual item bundled in a combo."""

    item_id: str
    name: str
    base_price: Decimal
    tax_rate_percent: Decimal


@dataclass(frozen=True)
class ComboItemTaxBreakdownDto:
    """Calculated proportional tax and discount breakdown for a combo item."""

    item_id: str
    name: str
    base_price: Decimal
    allocated_discount: Decimal
    net_price: Decimal
    tax_rate_percent: Decimal
    tax_amount: Decimal
    line_total: Decimal


@dataclass(frozen=True)
class ComboTaxSplitResultDto:
    """Aggregated tax breakdown for a complete combo meal bundle."""

    bundle_price: Decimal
    total_base_price: Decimal
    total_discount: Decimal
    total_tax: Decimal
    total_charge: Decimal
    items: tuple[ComboItemTaxBreakdownDto, ...]


class ComboTaxEngine:
    """
    Statutory tax engine executing proportional discount and tax split for combo bundles.
    """

    CENT = Decimal("0.01")

    @classmethod
    def calculate_proportional_tax_split(
        cls,
        bundle_price: Decimal,
        items: list[ComboItemInputDto],
    ) -> ComboTaxSplitResultDto:
        if not items:
            raise ValueError("Combo bundle must contain at least one item.")
        total_base = sum((item.base_price for item in items), Decimal("0.00"))
        if total_base <= Decimal("0.00"):
            raise ValueError("Total base price of bundled items must be positive.")
        bundle_price = bundle_price.quantize(cls.CENT, rounding=ROUND_HALF_UP)
        total_discount = (total_base - bundle_price).quantize(cls.CENT, rounding=ROUND_HALF_UP)
        discounts = cls._allocate_proportional_discounts(total_base, total_discount, items)
        breakdowns = cls._compute_item_breakdowns(items, discounts)
        total_tax = sum((b.tax_amount for b in breakdowns), Decimal("0.00"))
        total_charge = bundle_price + total_tax
        return ComboTaxSplitResultDto(
            bundle_price=bundle_price,
            total_base_price=total_base.quantize(cls.CENT),
            total_discount=total_discount,
            total_tax=total_tax,
            total_charge=total_charge,
            items=tuple(breakdowns),
        )

    @classmethod
    def _allocate_proportional_discounts(
        cls,
        total_base: Decimal,
        total_discount: Decimal,
        items: list[ComboItemInputDto],
    ) -> list[Decimal]:
        raw_discounts = [
            (total_discount * (item.base_price / total_base)).quantize(
                cls.CENT, rounding=ROUND_HALF_UP
            )
            for item in items
        ]
        penny_diff = total_discount - sum(raw_discounts)
        if penny_diff != Decimal("0.00") and raw_discounts:
            raw_discounts[0] += penny_diff
        return raw_discounts

    @classmethod
    def _compute_item_breakdowns(
        cls,
        items: list[ComboItemInputDto],
        discounts: list[Decimal],
    ) -> list[ComboItemTaxBreakdownDto]:
        results: list[ComboItemTaxBreakdownDto] = []
        for item, disc in zip(items, discounts, strict=True):
            net = (item.base_price - disc).quantize(cls.CENT, rounding=ROUND_HALF_UP)
            multiplier = item.tax_rate_percent / Decimal("100.00")
            tax = (net * multiplier).quantize(cls.CENT, rounding=ROUND_HALF_UP)
            results.append(
                ComboItemTaxBreakdownDto(
                    item_id=item.item_id,
                    name=item.name,
                    base_price=item.base_price.quantize(cls.CENT),
                    allocated_discount=disc,
                    net_price=net,
                    tax_rate_percent=item.tax_rate_percent,
                    tax_amount=tax,
                    line_total=net + tax,
                )
            )
        return results
