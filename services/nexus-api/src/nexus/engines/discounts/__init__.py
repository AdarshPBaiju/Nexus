"""
nexus.engines.discounts - Discount & Promotions microkernel.
"""

from __future__ import annotations

from nexus.engines.discounts.service import (
    DiscountCalculationResult,
    DiscountEvaluatorService,
)

__all__ = [
    "DiscountCalculationResult",
    "DiscountEvaluatorService",
]
