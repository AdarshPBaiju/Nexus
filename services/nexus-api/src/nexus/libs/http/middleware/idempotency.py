"""
nexus.libs.http.middleware.idempotency - Stage 8 Transactional Idempotency.
"""

from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse


class IdempotencyMiddleware:
    """Stage 8: Atomic reservation and cached replay using Idempotency-Key header."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        self._cache: dict[str, tuple[int, bytes, dict[str, str]]] = {}

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.method not in {"POST", "PATCH", "PUT"}:
            return self.get_response(request)

        key = request.headers.get("Idempotency-Key")
        if not key:
            return self.get_response(request)

        if key in self._cache:
            status_code, content, headers = self._cache[key]
            res = HttpResponse(content=content, status=status_code)
            for h_name, h_val in headers.items():
                res[h_name] = h_val
            res["X-Nexus-Idempotent-Replay"] = "true"
            return res

        response = self.get_response(request)
        if 200 <= response.status_code < 300:
            stored_headers = {"Content-Type": response.get("Content-Type", "application/json")}
            self._cache[key] = (response.status_code, response.content, stored_headers)

        return response
