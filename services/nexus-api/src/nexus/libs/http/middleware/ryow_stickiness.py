"""
nexus.libs.http.middleware.ryow_stickiness - Stage 9 RYOW Primary-Replica Stickiness.
"""

from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse


class RyowStickinessMiddleware:
    """Stage 9: Enforces Read-Your-Own-Writes primary routing on active RYOW token."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        ryow_token = request.headers.get("X-Nexus-RYOW-Token")
        request.use_primary_db = bool(ryow_token)

        response = self.get_response(request)
        if (
            request.method in {"POST", "PATCH", "PUT", "DELETE"}
            and 200 <= response.status_code < 300
        ):
            response["X-Nexus-RYOW-Token"] = "ryow_active_token"
        return response
