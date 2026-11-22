"""
nexus.extensions.channels.sms.msg91_dlt_adapter - India TRAI DLT Compliant SMS Gateway Adapter.
"""
from __future__ import annotations

from typing import Any

from nexus.engines.notifications.application.adapters import BaseChannelProviderAdapter


class Msg91DltSmsAdapter(BaseChannelProviderAdapter):
    """
    Direct India telecom gateway enforcing TRAI DLT entity, header, and template compliance.
    """

    MAX_DLT_VAR_LENGTH = 30

    def __init__(self, auth_key: str = "", default_pe_id: str = "") -> None:
        self.auth_key = auth_key
        self.default_pe_id = default_pe_id

    @property
    def provider_code(self) -> str:
        return "MSG91_DLT_SMS"

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

        dlt_err = self._validate_dlt_compliance(context)
        if dlt_err:
            return False, dlt_err, 0

        return True, "", 12  # 12 micro-cents

    def _validate_dlt_compliance(self, context: dict[str, Any]) -> str | None:
        pe_id = context.get("pe_id") or self.default_pe_id
        template_id = context.get("template_id")
        if not pe_id or not template_id:
            return "MISSING_DLT_HEADERS"

        variables = context.get("variables", {})
        for var_name, var_val in variables.items():
            if len(str(var_val)) > self.MAX_DLT_VAR_LENGTH:
                return f"DLT_VARIABLE_LENGTH_EXCEEDED:{var_name}"
        return None
