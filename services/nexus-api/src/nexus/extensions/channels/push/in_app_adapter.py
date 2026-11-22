"""
nexus.extensions.channels.push.in_app_adapter - In-App Notification Center Adapter.
"""

from __future__ import annotations

import uuid
from typing import Any

from nexus.engines.notifications.application.adapters import BaseChannelProviderAdapter
from nexus.engines.notifications.models import InAppNotification


class InAppNotificationAdapter(BaseChannelProviderAdapter):
    """
    In-app notification dispatcher delivering directly to workspace notification center.
    """

    @property
    def provider_code(self) -> str:
        return "IN_APP_CORE"

    @property
    def channel(self) -> str:
        return "IN_APP"

    def send(
        self,
        destination: str,
        template_code: str,
        context: dict[str, Any],
    ) -> tuple[bool, str, int]:
        tenant_id = context.get("tenant_id")
        if not tenant_id:
            return False, "MISSING_TENANT_CONTEXT", 0

        try:
            recipient_uuid = uuid.UUID(destination)
        except (ValueError, TypeError):
            return False, "INVALID_RECIPIENT_UUID", 0

        InAppNotification.objects.create(
            tenant_id=tenant_id,
            recipient_id=recipient_uuid,
            title=context.get("title", "Notification"),
            body=context.get("body", ""),
            category=context.get("category", "SYSTEM"),
            action_url=context.get("action_url", ""),
        )
        return True, "", 0
