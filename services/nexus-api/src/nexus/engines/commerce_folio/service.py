"""
nexus.engines.commerce_folio.service - Optimistic Concurrency & Folio Settlement Service.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from nexus.engines.commerce_folio.models.folio import CommerceFolio
from nexus.engines.commerce_folio.models.line_item import FolioLineItem


class OptimisticLockError(ValidationError):
    """Raised when an If-Match version precondition fails (HTTP 412)."""


@dataclass(frozen=True)
class AddLineItemDto:
    """Parameters for appending a charge line item to a folio."""

    item_type: str
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_amount: Decimal


class FolioOptimisticLockService:
    """
    Coordinates folio mutations under RFC 9110 If-Match optimistic locking.
    """

    @classmethod
    def assert_version_match(cls, folio: CommerceFolio, expected_version: int) -> None:
        """Verifies client-provided version matches active database version."""
        if folio.version != expected_version:
            raise OptimisticLockError(
                f"Folio version conflict: expected {expected_version}, but database is at {folio.version}."
            )

    @classmethod
    @transaction.atomic
    def add_line_item(
        cls,
        folio: CommerceFolio,
        expected_version: int,
        dto: AddLineItemDto,
    ) -> FolioLineItem:
        """
        Appends charge line item, recalculates totals, and increments version counter.
        """
        if folio.status != CommerceFolio.FolioStatus.OPEN:
            raise ValidationError(f"Cannot add items to folio in {folio.status} state.")

        cls.assert_version_match(folio, expected_version)

        subtotal = dto.quantity * dto.unit_price
        total = subtotal + dto.tax_amount

        line = FolioLineItem.objects.create(
            folio=folio,
            item_type=dto.item_type,
            description=dto.description,
            quantity=dto.quantity,
            unit_price=dto.unit_price,
            tax_amount=dto.tax_amount,
            total_amount=total,
        )

        folio.subtotal_amount += subtotal
        folio.tax_amount += dto.tax_amount
        folio.total_amount += total
        folio.version += 1
        folio.save(
            update_fields=["subtotal_amount", "tax_amount", "total_amount", "version", "updated_at"]
        )
        return line
