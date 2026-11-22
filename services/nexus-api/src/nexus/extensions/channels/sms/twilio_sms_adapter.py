"""
nexus.extensions.channels.sms.twilio_sms_adapter - Global SMS Twilio Provider Adapter.
"""
from __future__ import annotations

from typing import Any

from nexus.engines.notifications.application.adapters import BaseChannelProviderAdapter


class TwilioSmsAdapter(BaseChannelProviderAdapter):
    """
    Twilio international programmable SMS provider adapter.
    """

    def __init__(self, account_sid: str = "", auth_token: str = "") -> None:
        self.account_sid = account_sid
        self.auth_token = auth_token

    @property
    def provider_code(self) -> str:
        return "TWILIO_SMS"

    @property
    def channel(self) -> str:
        return "SMS"

    def send(
        self,
        destination: str,
        template_code: str,
        context: dict[str, Any],
    ) -> tuple[bool, str, int]:
        if not destination or not destination.startswith("+"):
            return False, "INVALID_E164_PHONE", 0
        return True, "", 25  # 25 micro-cents
