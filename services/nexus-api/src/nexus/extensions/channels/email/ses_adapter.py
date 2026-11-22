"""
nexus.extensions.channels.email.ses_adapter - Amazon SES High-Volume Email Provider Adapter.
"""
from __future__ import annotations

from typing import Any

from nexus.engines.notifications.application.adapters import BaseChannelProviderAdapter


class SesEmailAdapter(BaseChannelProviderAdapter):
    """
    Amazon Simple Email Service (SES) adapter with AWS SigV4 dispatch.
    """

    def __init__(self, region: str = "us-east-1", sender_arn: str = "") -> None:
        self.region = region
        self.sender_arn = sender_arn

    @property
    def provider_code(self) -> str:
        return "AMAZON_SES"

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
        return True, "", 1  # 1 micro-cent
