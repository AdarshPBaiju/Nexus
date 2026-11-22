"""
nexus.engines.payment_router.gateways.razorpay_adapter - Razorpay Payment Gateway Adapter.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from nexus.engines.payment_router.gateways.base import BasePaymentGatewayAdapter
from nexus.engines.payment_router.models.payment_intent import PaymentIntent


class RazorpayGatewayAdapter(BasePaymentGatewayAdapter):
    """
    Razorpay enterprise order and payment gateway adapter.
    """

    @property
    def gateway_code(self) -> str:
        return "RAZORPAY"

    def process_charge(
        self,
        intent: PaymentIntent,
        payment_data: dict[str, Any],
    ) -> tuple[bool, str, Decimal, dict[str, Any]]:
        order_id = payment_data.get("order_id", f"order_{uuid.uuid4().hex[:14]}")
        payment_id = f"pay_{uuid.uuid4().hex[:14]}"
        # Standard Razorpay fee: 2.0%
        fee = (Decimal(str(intent.amount)) * Decimal("0.020")).quantize(Decimal("0.0001"))
        raw = {
            "id": payment_id,
            "order_id": order_id,
            "status": "captured",
            "method": payment_data.get("method", "card"),
        }
        return True, payment_id, fee, raw
