"""
nexus.libs.http.middleware.audit_context_middleware - Stage 10 Audit Context Populator.
"""

from __future__ import annotations

import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse

from nexus.libs.db.audit_context import (
    AuditRequestContext,
    clear_current_audit_context,
    set_current_audit_context,
)


class AuditContextMiddleware:
    """Stage 10: Injects active request audit context for GUC and logging propagation."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        tenant_id = getattr(request, "tenant_id", None) or uuid.uuid4()
        actor_id = getattr(request, "actor_id", None) or uuid.uuid4()
        ctx = AuditRequestContext(
            tenant_id=tenant_id,
            actor_id=actor_id,
            request_id=getattr(request, "request_id", None),
            trace_id=getattr(request, "trace_id", None),
            client_ip=request.META.get("REMOTE_ADDR"),
        )
        set_current_audit_context(ctx)
        try:
            return self.get_response(request)
        finally:
            clear_current_audit_context()
