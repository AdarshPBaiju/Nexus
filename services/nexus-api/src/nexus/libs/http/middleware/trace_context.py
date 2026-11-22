"""
nexus.libs.http.middleware.trace_context - Stage 2 Request ID & W3C Trace Injection.
"""

from __future__ import annotations

import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse


class TraceContextMiddleware:
    """Stage 2: Ensures W3C distributed trace context and request UUIDs are populated."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        req_id = request.headers.get("X-Nexus-Request-ID") or str(uuid.uuid4())
        trace_id = request.headers.get("traceparent") or f"00-{uuid.uuid4().hex}-{uuid.uuid4().hex[:16]}-01"

        request.request_id = req_id
        request.trace_id = trace_id

        response = self.get_response(request)
        response["X-Nexus-Request-ID"] = req_id
        response["traceparent"] = trace_id
        return response
