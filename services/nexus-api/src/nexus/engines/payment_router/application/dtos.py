"""
nexus.engines.payment_router.application.dtos - Payment Router Data Transfer Objects.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class CreatePaymentIntentCmd:
    """Command payload for initiating a payment transaction."""

    tenant_id: uuid.UUID
    folio_id: uuid.UUID
    amount: Decimal
    currency: str = "USD"
    customer_id: uuid.UUID | None = None
    idempotency_key: str = ""

    def __post_init__(self) -> None:
        if not self.idempotency_key:
            generated = f"nx_pay_{self.tenant_id}_{self.folio_id}_{uuid.uuid4().hex[:8]}"
            object.__setattr__(self, "idempotency_key", generated)


@dataclass(frozen=True)
class ConfirmPaymentCmd:
    """Command payload for confirming and capturing a payment."""

    tenant_id: uuid.UUID
    intent_id: uuid.UUID
    gateway_code: str
    payment_data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ClearingPosting:
    """Double-entry clearing journal line representation."""

    account_name: str
    direction: str  # DEBIT or CREDIT
    amount: Decimal
    description: str
