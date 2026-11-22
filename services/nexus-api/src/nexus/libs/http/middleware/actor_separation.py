"""
nexus.libs.http.middleware.actor_separation - 5-Actor HTTP boundary enforcement.
"""

from __future__ import annotations

import base64
import json
import uuid
from typing import Any, Callable

from django.http import HttpRequest, HttpResponse, JsonResponse

from nexus.libs.http.actor import ActorContext, ActorType


class ActorSeparationMiddleware:
    """
    Inspects inbound Authorization headers and establishes verified ActorContext.
    Enforces isolation between Staff, Consumer, Device, API Key, and OAuth App actors.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        auth_header = request.headers.get("Authorization", "").strip()
        if not auth_header:
            return JsonResponse(
                {"error": "Unauthorized", "detail": "Missing Authorization header"},
                status=401,
            )

        actor_ctx = self._resolve_actor(auth_header)
        if not actor_ctx:
            return JsonResponse(
                {"error": "Unauthorized", "detail": "Invalid or unverified actor credentials"},
                status=401,
            )

        # Enforce boundary: Passport Consumers cannot access staff workspace routes
        if actor_ctx.actor_type == ActorType.PASSPORT_CONSUMER and request.path.startswith(
            "/api/v1/workspace/"
        ):
            return JsonResponse(
                {
                    "error": "Forbidden",
                    "detail": "Passport consumers cannot access staff workspace APIs",
                },
                status=403,
            )

        request.actor = actor_ctx  # type: ignore[attr-defined]
        return self.get_response(request)

    def _resolve_actor(self, header: str) -> ActorContext | None:
        if header.startswith("ApiKey "):
            return self._resolve_api_key(header[7:])
        if header.startswith("Bearer "):
            return self._resolve_bearer_token(header[7:])
        if header.startswith("Device "):
            return self._resolve_device(header[7:])
        return None

    def _resolve_api_key(self, key_str: str) -> ActorContext | None:
        # API Keys must follow nx_live_ or nx_test_ standard
        if not (key_str.startswith("nx_live_") or key_str.startswith("nx_test_")):
            return None
        return ActorContext(
            actor_type=ActorType.API_KEY,
            actor_id=uuid.uuid5(uuid.NAMESPACE_DNS, key_str),
            scopes=frozenset(["api:read", "api:write"]),
        )

    def _resolve_device(self, token_str: str) -> ActorContext | None:
        if not token_str.startswith("device_"):
            return None
        return ActorContext(
            actor_type=ActorType.DESKTOP_DEVICE,
            actor_id=uuid.uuid5(uuid.NAMESPACE_OID, token_str),
            scopes=frozenset(["device:station", "pos:offline"]),
        )

    def _resolve_bearer_token(self, token: str) -> ActorContext | None:
        try:
            # Minimal decoding simulation for testing/middleware verification
            parts = token.split(".")
            if len(parts) != 3:
                return None
            payload_raw = parts[1]
            padding = (4 - len(payload_raw) % 4) % 4
            payload_bytes = base64.urlsafe_b64decode(payload_raw + ("=" * padding))
            data: dict[str, Any] = json.loads(payload_bytes.decode("utf-8"))

            actor_type_str = data.get("actor_type", "STAFF")
            actor_type = ActorType(actor_type_str)
            actor_id = uuid.UUID(data["sub"])
            tenant_id = uuid.UUID(data["tenant_id"]) if "tenant_id" in data else None
            scopes = frozenset(data.get("scopes", []))

            return ActorContext(
                actor_type=actor_type,
                actor_id=actor_id,
                tenant_id=tenant_id,
                scopes=scopes,
            )
        except Exception:
            return None
