"""
nexus.libs.http.actor - 5-Actor separation domain types and context.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum


class ActorType(str, Enum):
    """
    The 5 distinct canonical actor boundaries in Project Nexus.
    """

    STAFF = "STAFF"
    PASSPORT_CONSUMER = "PASSPORT_CONSUMER"
    DESKTOP_DEVICE = "DESKTOP_DEVICE"
    API_KEY = "API_KEY"
    OAUTH_APP = "OAUTH_APP"


@dataclass(frozen=True)
class ActorContext:
    """
    Immutable security context resolved for each inbound request.
    """

    actor_type: ActorType
    actor_id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    scopes: frozenset[str] = field(default_factory=frozenset)
    is_authenticated: bool = True

    @property
    def is_staff(self) -> bool:
        return self.actor_type == ActorType.STAFF

    @property
    def is_desktop_device(self) -> bool:
        return self.actor_type == ActorType.DESKTOP_DEVICE

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes
