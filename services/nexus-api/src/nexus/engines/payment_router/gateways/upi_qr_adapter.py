"""
nexus.engines.payment_router.gateways.upi_qr_adapter - NPCI Direct UPI Intent & QR Adapter.
"""

from __future__ import annotations

import urllib.parse
import uuid
from decimal import Decimal
from typing import Any

from nexus.engines.payment_router.gateways.base import BasePaymentGatewayAdapter
from nexus.engines.payment_router.models.payment_intent import PaymentIntent


class DirectUpiQrAdapter(BasePaymentGatewayAdapter):
    """
    Direct NPCI UPI QR code generator for direct-to-bank settlements with 0% MDR.
    """

    @property
    def gateway_code(self) -> str:
        return "DIRECT_UPI"

    def process_charge(
        self,
        intent: PaymentIntent,
        payment_data: dict[str, Any],
    ) -> tuple[bool, str, Decimal, dict[str, Any]]:
        vpa = payment_data.get("merchant_vpa", "nexus.merchant@hdfcbank")
        merchant_name = payment_data.get("merchant_name", "Nexus Store")
        tx_ref = f"UPI{uuid.uuid4().hex[:12].upper()}"

        upi_payload = {
            "pa": vpa,
            "pn": merchant_name,
            "am": str(intent.amount),
            "cu": intent.currency,
            "tr": tx_ref,
        }
        query_string = urllib.parse.urlencode(upi_payload)
        upi_uri = f"upi://pay?{query_string}"

        raw = {
            "upi_uri": upi_uri,
            "tx_ref": tx_ref,
            "status": "succeeded",
            "mdr_fee": "0.0000",
        }
        return True, tx_ref, Decimal("0.0000"), raw
