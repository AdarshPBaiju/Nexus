"""
nexus.engines.payment_router.gateways.registry - Gateway Adapter Registry.
"""

from __future__ import annotations

from nexus.engines.payment_router.gateways.base import BasePaymentGatewayAdapter
from nexus.engines.payment_router.gateways.razorpay_adapter import RazorpayGatewayAdapter
from nexus.engines.payment_router.gateways.stripe_adapter import StripeGatewayAdapter
from nexus.engines.payment_router.gateways.upi_qr_adapter import DirectUpiQrAdapter


class GatewayAdapterRegistry:
    """Registry coordinating available payment gateway adapters."""

    _adapters: dict[str, BasePaymentGatewayAdapter] = {}

    @classmethod
    def _initialize(cls) -> None:
        if cls._adapters:
            return
        cls.register(StripeGatewayAdapter())
        cls.register(RazorpayGatewayAdapter())
        cls.register(DirectUpiQrAdapter())

    @classmethod
    def register(cls, adapter: BasePaymentGatewayAdapter) -> None:
        cls._adapters[adapter.gateway_code.upper()] = adapter

    @classmethod
    def get(cls, gateway_code: str) -> BasePaymentGatewayAdapter | None:
        cls._initialize()
        return cls._adapters.get(gateway_code.upper())
