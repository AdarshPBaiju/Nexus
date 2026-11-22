"""
nexus.libs.serializers.base_output - Strict output serializer kernel.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Optional, Sequence

from rest_framework import serializers


class BaseNexusOutputSerializer(serializers.Serializer):
    """
    Base output serializer enforcing selected-fields pruning and Weak ETag computation.
    """

    def __init__(
        self,
        *args: Any,
        selected_fields: Optional[Sequence[str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.selected_fields = selected_fields

    def to_representation(self, instance: Any) -> dict[str, Any]:
        rep = super().to_representation(instance)
        active_fields = self.selected_fields or self.context.get("selected_fields")
        if active_fields:
            allowed = set(active_fields)
            return {k: v for k, v in rep.items() if k in allowed}
        return rep

    def compute_weak_etag(self, representation: dict[str, Any]) -> str:
        """Compute RFC 9110 compliant Weak ETag for the output representation."""
        serialized = json.dumps(representation, sort_keys=True, separators=(",", ":"), default=str)
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
        return f'W/"nx:ser:{digest}"'
