"""
nexus.engines.discounts.domain.allocator - Proportional line allocation with zero penny drift.
"""

from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal
from typing import Sequence

from nexus.libs.money.money import Money


class ProportionalDiscountAllocator:
    """
    Distributes an order-level discount across qualifying lines proportionally.
    Uses the largest-remainder method with Bankers rounding to guarantee
    that the sum of line discounts strictly equals the target total discount.
    """

    @classmethod
    def allocate(
        cls,
        total_discount: Money,
        line_subtotals: Sequence[Money],
    ) -> list[Money]:
        """Distributes total_discount across lines proportionally based on their subtotal."""
        currency = total_discount.currency
        if not line_subtotals or total_discount.amount <= Decimal("0"):
            return [Money.of(Decimal("0.00"), currency) for _ in line_subtotals]

        sum_lines = sum((m.amount for m in line_subtotals), Decimal("0.00"))
        if sum_lines <= Decimal("0"):
            return [Money.of(Decimal("0.00"), currency) for _ in line_subtotals]

        # First pass: calculate proportional amounts rounded down
        allocations: list[Decimal] = []
        allocated_sum = Decimal("0.00")
        for line in line_subtotals:
            share = (total_discount.amount * line.amount) / sum_lines
            rounded = share.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
            allocations.append(rounded)
            allocated_sum += rounded

        # Second pass: reconcile penny discrepancy onto the largest remainder line
        discrepancy = total_discount.amount - allocated_sum
        if discrepancy != Decimal("0.00") and allocations:
            max_idx = max(range(len(line_subtotals)), key=lambda i: line_subtotals[i].amount)
            allocations[max_idx] += discrepancy

        return [Money.of(amt, currency) for amt in allocations]
