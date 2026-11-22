"""
nexus.extensions.channels.whatsapp.twilio_adapter - Twilio WhatsApp Messaging Adapter.
"""
from __future__ import annotations

from typing import Any

from nexus.engines.notifications.application.adapters import BaseChannelProviderAdapter


class TwilioWhatsAppAdapter(BaseChannelProviderAdapter):
    """
    Twilio Messaging API bridge for WhatsApp sandbox and production numbers.
    """

    def __init__(self, account_sid: str = "", auth_token: str = "") -> None:
        self.account_sid = account_sid
        self.auth_token = auth_token

    @property
    def provider_code(self) -> str:
        return "TWILIO_WHATSAPP"

    @property
    def channel(self) -> str:
        return "WHATSAPP"

    def send(
        self,
        destination: str,
        template_code: str,
        context: dict[str, Any],
    ) -> tuple[bool, str, int]:
        if not destination or not destination.startswith("+"):
            return False, "INVALID_E164_PHONE", 0
        return True, "", 20  # 20 micro-cents
