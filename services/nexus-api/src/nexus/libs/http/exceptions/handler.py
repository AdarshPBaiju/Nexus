"""
nexus.libs.http.exceptions.handler - RFC 9457 unified exception handler.
"""

from __future__ import annotations

from typing import Any

from rest_framework import exceptions, status
from rest_framework.response import Response

from nexus.libs.serializers.errors import (
    InvalidParameterDetail,
    RFC9457ProblemDetail,
)


def nexus_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Unified DRF exception handler emitting standardized RFC 9457 Problem Details."""
    if isinstance(exc, exceptions.ValidationError):
        invalid_params: list[InvalidParameterDetail] = []
        if isinstance(exc.detail, dict):
            for field, msgs in exc.detail.items():
                reason = msgs[0] if isinstance(msgs, list) else str(msgs)
                invalid_params.append(InvalidParameterDetail(field=str(field), reason=str(reason)))
        problem = RFC9457ProblemDetail(
            title="Validation Failed",
            status=status.HTTP_400_BAD_REQUEST,
            detail="The request failed statutory validation constraints.",
            code="VALIDATION_FAILED",
            invalid_params=invalid_params,
        )
        return Response(problem.to_dict(), status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)):
        problem = RFC9457ProblemDetail(
            title="Authentication Required",
            status=status.HTTP_401_UNAUTHORIZED,
            detail="Valid authentication credentials were not provided.",
            code="UNAUTHORIZED",
        )
        return Response(problem.to_dict(), status=status.HTTP_401_UNAUTHORIZED)

    if isinstance(exc, exceptions.PermissionDenied):
        problem = RFC9457ProblemDetail(
            title="Access Denied",
            status=status.HTTP_403_FORBIDDEN,
            detail="You do not possess the required permissions to perform this action.",
            code="PERMISSION_DENIED",
        )
        return Response(problem.to_dict(), status=status.HTTP_403_FORBIDDEN)

    return None
