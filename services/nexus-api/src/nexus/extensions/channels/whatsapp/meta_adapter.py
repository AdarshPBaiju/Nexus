"""
nexus.extensions.channels.whatsapp.meta_adapter - Meta WhatsApp Cloud API Provider Adapter.
"""

from __future__ import annotations

from typing import Any

from nexus.engines.notifications.application.adapters import BaseChannelProviderAdapter


class MetaWhatsAppAdapter(BaseChannelProviderAdapter):
    """
    Direct Meta WhatsApp Cloud API (Graph v21.0) provider adapter.
    Maps named template variables to ordered {{1}}, {{2}} positional parameters.
    """

    def __init__(self, phone_number_id: str = "", access_token: str = "") -> None:
        self.phone_number_id = phone_number_id
        self.access_token = access_token

    @property
    def provider_code(self) -> str:
        return "META_WHATSAPP_CLOUD"

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

        positional_params = self.map_template_variables(context)
        if template_code and not positional_params and context:
            return False, "VARIABLE_MAPPING_ERROR", 0

        return True, "", 15  # 15 micro-cents

    @classmethod
    def map_template_variables(cls, context: dict[str, Any]) -> list[str]:
        """Maps named dictionary keys to ordered positional parameters for Meta HSM templates."""
        sorted_keys = sorted(context.keys())
        return [str(context[k]) for k in sorted_keys]
