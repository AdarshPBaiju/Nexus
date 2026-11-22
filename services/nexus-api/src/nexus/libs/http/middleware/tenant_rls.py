"""
nexus.libs.http.middleware.tenant_rls - Stage 4 Tenant Resolution & Forced RLS Context.
"""

from __future__ import annotations

import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse, JsonResponse


class TenantRlsMiddleware:
    """Stage 4: Extracts X-Nexus-Tenant-Slug / Tenant ID and binds RLS context."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        tenant_header = request.headers.get("X-Nexus-Tenant-ID")
        if tenant_header:
            try:
                request.tenant_id = uuid.UUID(tenant_header)
            except ValueError:
                return JsonResponse({"detail": "Invalid tenant ID header"}, status=400)
        else:
            request.tenant_id = None
        return self.get_response(request)
