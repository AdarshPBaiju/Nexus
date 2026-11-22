"""
nexus.libs.http.middleware.security_headers - Stage 1 Security Headers & CSP Nonce.
"""

from __future__ import annotations

import secrets
from typing import Callable

from django.http import HttpRequest, HttpResponse


class SecurityHeadersMiddleware:
    """Stage 1: Generates per-request CSP nonce and attaches enterprise security headers."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        nonce = secrets.token_urlsafe(16)
        request.csp_nonce = nonce

        response = self.get_response(request)
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response["Content-Security-Policy"] = f"default-src 'self'; script-src 'self' 'nonce-{nonce}'"
        return response
