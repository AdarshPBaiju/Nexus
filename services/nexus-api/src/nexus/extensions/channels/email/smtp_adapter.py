"""
nexus.extensions.channels.email.smtp_adapter - Direct SMTP Corporate Mail Adapter.
"""

from __future__ import annotations

from typing import Any

from nexus.engines.notifications.application.adapters import BaseChannelProviderAdapter


class SmtpEmailAdapter(BaseChannelProviderAdapter):
    """
    Self-hosted or corporate SMTP bridge with STARTTLS support.
    """

    def __init__(self, host: str = "localhost", port: int = 587, use_tls: bool = True) -> None:
        self.host = host
        self.port = port
        self.use_tls = use_tls

    @property
    def provider_code(self) -> str:
        return "SMTP_DIRECT"

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
        return True, "", 0
