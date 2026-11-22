"""
nexus.libs.field_control.fls_bridge - Field-Level Security projection bridge.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class FlsFieldEvaluation:
    visible_fields: tuple[str, ...]
    masked_fields: tuple[str, ...]


class FlsProjectionBridge:
    """Intersects requested fields with actor FLS permissions."""

    @classmethod
    def evaluate_permissions(
        cls,
        requested_fields: Sequence[str],
        actor_fls_rules: Mapping[str, str],
    ) -> FlsFieldEvaluation:
        """
        Evaluate requested fields against FLS rules:
        - READ: permitted in cleartext
        - MASKED: permitted with redaction/masking
        - HIDDEN / unspecified deny: omitted completely
        """
        visible: list[str] = []
        masked: list[str] = []

        for f in requested_fields:
            permission = actor_fls_rules.get(f, "READ")
            if permission == "READ":
                visible.append(f)
            elif permission == "MASKED":
                masked.append(f)
            # If HIDDEN, field is completely pruned

        return FlsFieldEvaluation(
            visible_fields=tuple(visible),
            masked_fields=tuple(masked),
        )

    @classmethod
    def mask_representation(
        cls,
        data: Mapping[str, Any],
        masked_fields: Sequence[str],
    ) -> dict[str, Any]:
        """Apply masking transformation to output dictionary."""
        result = dict(data)
        for field_name in masked_fields:
            if field_name in result:
                val_str = str(result[field_name])
                result[field_name] = f"**** {val_str[-4:]}" if len(val_str) > 4 else "****"
        return result
