"""
nexus.libs.http.views.base_resource_viewset - Thin-transport resource ViewSet kernel.
"""

from __future__ import annotations

from typing import Any

from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response


class BaseTenantResourceViewSet(viewsets.ViewSet):
    """
    Thin-transport coordinator for tenant-scoped resources.
    Dispatches to domain handlers and enforces RFC 9110 If-Match optimistic locking.
    """

    def check_optimistic_lock(self, request: Request, current_version: int) -> None:
        """Validate RFC 9110 If-Match header against entity version."""
        if_match = request.headers.get("If-Match")
        if if_match:
            clean_match = if_match.strip().strip('"')
            if clean_match != str(current_version):
                from rest_framework.exceptions import APIException

                exc = APIException("Precondition Failed: Resource version conflict")
                exc.status_code = status.HTTP_412_PRECONDITION_FAILED
                raise exc

    def build_envelope_response(
        self,
        data: Any,
        status_code: int = status.HTTP_200_OK,
        headers: dict[str, str] | None = None,
    ) -> Response:
        """Standardized envelope response wrapper."""
        return Response(data, status=status_code, headers=headers)
