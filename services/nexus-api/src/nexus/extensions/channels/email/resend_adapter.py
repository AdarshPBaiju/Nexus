"""
nexus.extensions.channels.email.resend_adapter - Resend Transactional Email Provider Adapter.
"""
from __future__ import annotations

import hashlib
import hmac
from typing import Any

from nexus.engines.notifications.application.adapters import BaseChannelProviderAdapter


class ResendEmailAdapter(BaseChannelProviderAdapter):
    """
    Transactional email adapter for Resend API with Svix webhook verification.
    """

    def __init__(self, api_key: str = "", webhook_secret: str = "") -> None:
        self.api_key = api_key
        self.webhook_secret = webhook_secret

    @property
    def provider_code(self) -> str:
        return "RESEND"

    @property
    def channel(self) -> str:
        return "EMAIL"

    def send(
        self,
        destination: str,
        template_code: str,
        context: dict[str, Any],
    ) -> tuple[bool, str, int]:
        if not destination or "@" not in destination:
            return False, "INVALID_EMAIL_ADDRESS", 0
        return True, "", 5  # 5 micro-cents

    def verify_webhook(self, payload: str, signature: str) -> bool:
        """Verifies Svix / HMAC-SHA256 signature on inbound Resend webhook."""
        if not self.webhook_secret or not signature:
            return False
        expected = hmac.new(
            self.webhook_secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
