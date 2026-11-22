"""
nexus.libs.http.views.fast_api_view - Thin-transport high-throughput API view kernel.
"""

from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class BaseFastTenantAPIView(APIView):
    """
    High-throughput, thin-transport API view with built-in Weak ETag evaluation.
    """

    def evaluate_weak_etag(self, request: Request, etag: str) -> bool:
        """Check If-None-Match header against computed ETag."""
        if_none_match = request.headers.get("If-None-Match")
        if if_none_match:
            clean_inm = if_none_match.strip().strip('"')
            clean_etag = etag.strip().strip('"')
            return clean_inm == clean_etag or if_none_match.strip() == etag.strip()
        return False

    def build_etag_response(
        self,
        request: Request,
        data: Any,
        etag: str,
    ) -> Response:
        """Return 304 Not Modified if ETag matches, else 200 with ETag header."""
        if self.evaluate_weak_etag(request, etag):
            res = Response(status=status.HTTP_304_NOT_MODIFIED)
            res["ETag"] = etag
            return res
        res = Response(data, status=status.HTTP_200_OK)
        res["ETag"] = etag
        return res
