"""
nexus.libs.http.middleware.path_envelope - Stage 2 Encrypted Path Envelope & Anti-Enumeration Middleware.
Unseals /api/v1/{resource}/nx1{mode}_{token}/ and strictly rejects raw UUIDs and query strings with 404.
"""

from __future__ import annotations

import re
import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse, HttpResponseNotFound

from nexus.libs.security.kms import TenantKmsKeyService
from nexus.libs.security.path_codec import (
    EncryptedPathCodec,
    PathEnvelopeDecryptionError,
)


class EncryptedPathEnvelopeMiddleware:
    """
    Stage 2 middleware in the 10-stage pipeline:
    - Enforces Anti-Enumeration: returns uniform 404 on raw UUIDs or plaintext ?query strings.
    - Transparently unseals nx1{mode}_{token} into request.envelope_context.
    """

    PATH_REGEX = re.compile(r"^/api/v1/(?P<resource>[a-zA-Z0-9_-]+)/(?P<remainder>.*)$")
    UUID_REGEX = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/?$",
        re.IGNORECASE,
    )
    ENVELOPE_REGEX = re.compile(r"^(?P<token>nx1[a-z]_[A-Za-z0-9_-]+)/?$")

    def __init__(
        self,
        get_response: Callable[[HttpRequest], HttpResponse],
        kms_service: TenantKmsKeyService | None = None,
    ) -> None:
        self.get_response = get_response
        self._kms = kms_service or TenantKmsKeyService()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        path = request.path_info
        match = self.PATH_REGEX.match(path)
        if not match:
            return self.get_response(request)

        resource = match.group("resource")
        remainder = match.group("remainder")

        # 1. Anti-Enumeration Rule 1: No plaintext ?query strings on protected endpoints
        query_string = request.META.get("QUERY_STRING", "")
        if query_string:
            return HttpResponseNotFound()

        # 2. Anti-Enumeration Rule 2: Strictly no raw UUIDs in URL paths
        if self.UUID_REGEX.match(remainder):
            return HttpResponseNotFound()

        # 3. Intercept and unseal encrypted path envelope tokens
        env_match = self.ENVELOPE_REGEX.match(remainder)
        if env_match:
            token = env_match.group("token")
            return self._handle_envelope(request, resource, token)

        return self.get_response(request)

    def _handle_envelope(
        self,
        request: HttpRequest,
        resource: str,
        token: str,
    ) -> HttpResponse:
        """Unseals envelope and attaches context to request."""
        tenant_id = self._extract_tenant_id(request)
        dek = self._kms.get_or_create_dek(tenant_id)

        try:
            mode, payload = EncryptedPathCodec.unseal_envelope(
                token=token,
                tenant_id=tenant_id,
                resource=resource,
                key=dek,
            )
        except PathEnvelopeDecryptionError:
            # Uniform 404: never leak error details on corrupted or tampered tokens
            return HttpResponseNotFound()

        request.envelope_context = {
            "mode": mode,
            "id": payload.get("id"),
            "filters": payload.get("f", {}),
            "search": payload.get("s", ""),
            "fields": payload.get("col", []),
            "cursor": payload.get("cur"),
            "page_size": payload.get("ps", 25),
            "sort": payload.get("srt", "-created_at"),
            "tab": payload.get("tab"),
        }
        return self.get_response(request)

    @staticmethod
    def _extract_tenant_id(request: HttpRequest) -> uuid.UUID | str:
        """Extracts tenant ID from header or request attributes."""
        tenant_raw = request.META.get("HTTP_X_NEXUS_TENANT_SLUG") or getattr(
            request, "tenant_id", None
        )
        if tenant_raw:
            try:
                return uuid.UUID(str(tenant_raw))
            except (ValueError, TypeError):
                return str(tenant_raw)
        return uuid.UUID(int=0)
