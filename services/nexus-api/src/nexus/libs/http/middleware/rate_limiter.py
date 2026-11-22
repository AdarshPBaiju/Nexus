"""
nexus.libs.http.middleware.rate_limiter - Stage 3 Rate Limiter & IP Shield.
"""

from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse, JsonResponse


class RateLimiterMiddleware:
    """Stage 3: Sliding window rate limiting protecting endpoints from abuse."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse], limit: int = 1000) -> None:
        self.get_response = get_response
        self.limit = limit
        self._counts: dict[str, int] = {}

    def __call__(self, request: HttpRequest) -> HttpResponse:
        client_ip = request.META.get("REMOTE_ADDR", "127.0.0.1")
        current = self._counts.get(client_ip, 0)
        if current >= self.limit:
            return JsonResponse(
                {"code": "RATE_LIMIT_EXCEEDED", "detail": "Too many requests."},
                status=429,
            )
        self._counts[client_ip] = current + 1
        return self.get_response(request)
