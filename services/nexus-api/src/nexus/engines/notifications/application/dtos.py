"""
nexus.engines.notifications.application.dtos - Notification Transfer Objects.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class NotificationIntentDTO:
    """Immutable dispatch intent from upstream domain engines."""

    tenant_id: uuid.UUID
    intent_id: uuid.UUID
    event_type: str
    priority: str
    destinations: dict[str, str]
    template_code: str
    template_context: dict[str, Any] = field(default_factory=dict)
    recipient_id: uuid.UUID | None = None
    idempotency_key: str = ""

    def __post_init__(self) -> None:
        if not self.idempotency_key:
            generated = f"nx_notif_{self.tenant_id}_{self.intent_id}"
            object.__setattr__(self, "idempotency_key", generated)


@dataclass(frozen=True)
class DeliveryResultDTO:
    """Outcome of orchestrator dispatch and waterfall evaluation."""

    success: bool
    channel_used: str | None = None
    provider_code: str | None = None
    attempt_id: uuid.UUID | None = None
    error_message: str | None = None
    is_duplicate: bool = False
    delayed_quiet_hours: bool = False


@dataclass(frozen=True)
class QuietHoursWindow:
    """Time window defining quiet period in local minutes from midnight."""

    enabled: bool
    start_minute: int
    end_minute: int
