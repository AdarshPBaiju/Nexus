"""
nexus.engines.payment_router.gateways.base - Base Payment Gateway Adapter Protocol.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any

from nexus.engines.payment_router.models.payment_intent import PaymentIntent


class BasePaymentGatewayAdapter(ABC):
    """
    Abstract interface implemented by all payment gateway integrations.
    Zero raw PAN storage: accepts only tokens, customer references, or bank rails.
    """

    @property
    @abstractmethod
    def gateway_code(self) -> str:
        """Standard identifier (STRIPE, RAZORPAY, DIRECT_UPI)."""
        pass

    @abstractmethod
    def process_charge(
        self,
        intent: PaymentIntent,
        payment_data: dict[str, Any],
    ) -> tuple[bool, str, Decimal, dict[str, Any]]:
        """
        Executes authorization and capture.
        Returns: (success: bool, gateway_tx_id: str, fee_amount: Decimal, raw_response: dict)
        """
        pass
