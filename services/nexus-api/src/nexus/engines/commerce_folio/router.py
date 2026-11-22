"""
nexus.engines.commerce_folio.router - Order Fulfillment Router for physical and digital dispatch.
"""
from __future__ import annotations

from enum import Enum
from typing import Sequence

from nexus.engines.commerce_folio.models.line_item import FolioLineItem


class FulfillmentTarget(str, Enum):
    """Physical printer or digital KDS screen destination."""

    BARISTA_KDS = "BARISTA_KDS"
    KITCHEN_KDS = "KITCHEN_KDS"
    EXPEDITE_KDS = "EXPEDITE_KDS"
    RECEIPT_PRINTER = "RECEIPT_PRINTER"


class OrderFulfillmentRouter:
    """
    Routes folio line items to physical thermal printers or digital KDS screens.
    """

    @classmethod
    def route_line_item(cls, line: FolioLineItem) -> FulfillmentTarget:
        """Determines target dispatch destination based on item type and description."""
        if line.item_type == FolioLineItem.ItemType.FOOD_BEV:
            desc_lower = line.description.lower()
            if any(term in desc_lower for term in ("coffee", "latte", "tea", "espresso", "beverage")):
                return FulfillmentTarget.BARISTA_KDS
            return FulfillmentTarget.KITCHEN_KDS
        return FulfillmentTarget.RECEIPT_PRINTER

    @classmethod
    def dispatch_batch(cls, lines: Sequence[FolioLineItem]) -> dict[FulfillmentTarget, list[FolioLineItem]]:
        """Groups items by their target dispatch destination."""
        routed: dict[FulfillmentTarget, list[FolioLineItem]] = {
            FulfillmentTarget.BARISTA_KDS: [],
            FulfillmentTarget.KITCHEN_KDS: [],
            FulfillmentTarget.RECEIPT_PRINTER: [],
        }
        for item in lines:
            target = cls.route_line_item(item)
            if target not in routed:
                routed[target] = []
            routed[target].append(item)
        return routed
