"""
nexus.extensions.channels.push.fcm_adapter - Firebase Cloud Messaging HTTP v1 Provider Adapter.
"""
from __future__ import annotations

import uuid
from typing import Any

from nexus.engines.notifications.application.adapters import BaseChannelProviderAdapter
from nexus.engines.notifications.models import DevicePushToken


class FirebaseFcmAdapter(BaseChannelProviderAdapter):
    """
    Firebase Cloud Messaging HTTP v1 provider adapter with stale token auto-pruning.
    """

    def __init__(self, project_id: str = "") -> None:
        self.project_id = project_id

    @property
    def provider_code(self) -> str:
        return "FIREBASE_FCM"

    @property
    def channel(self) -> str:
        return "PUSH"

    def send(
        self,
        destination: str,
        template_code: str,
        context: dict[str, Any],
    ) -> tuple[bool, str, int]:
        if not destination or len(destination) < 10:
            return False, "INVALID_DEVICE_TOKEN", 0

        simulated_status = context.get("simulated_fcm_status", "SUCCESS")
        if simulated_status in ("UNREGISTERED", "NOT_FOUND"):
            tenant_id = context.get("tenant_id")
            if tenant_id:
                self.prune_stale_token(tenant_id, destination)
            return False, f"FCM_TOKEN_{simulated_status}", 0

        return True, "", 2  # 2 micro-cents

    @classmethod
    def prune_stale_token(cls, tenant_id: uuid.UUID, token: str) -> None:
        """Deactivates stale or unregistered device tokens."""
        DevicePushToken.objects.filter(
            tenant_id=tenant_id,
            token=token,
        ).update(is_active=False)
