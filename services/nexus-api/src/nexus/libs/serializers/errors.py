"""
nexus.libs.serializers.errors - RFC 9457 Problem Details for HTTP APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class InvalidParameterDetail:
    """Details on a specific invalid input field."""

    field: str
    reason: str
    code: str = "invalid"


@dataclass(frozen=True)
class RFC9457ProblemDetail:
    """Standard RFC 9457 Problem Details payload."""

    type: str = "urn:nexus:error:validation-failed"
    title: str = "Validation Failed"
    status: int = 400
    detail: str = "The request payload failed statutory validation constraints."
    instance: Optional[str] = None
    code: str = "VALIDATION_FAILED"
    i18n_key: str = "error.validation.failed"
    invalid_params: list[InvalidParameterDetail] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert problem detail to standardized JSON-serializable dictionary."""
        return {
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
            "instance": self.instance,
            "code": self.code,
            "i18n_key": self.i18n_key,
            "invalid_params": [
                {"field": p.field, "reason": p.reason, "code": p.code}
                for p in self.invalid_params
            ],
        }
