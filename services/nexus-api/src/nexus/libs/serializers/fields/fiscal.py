"""
nexus.libs.serializers.fields.fiscal - Statutory fiscal identification and enum fields.
"""

from __future__ import annotations

import re
from typing import Any, Sequence

from rest_framework import serializers

TAX_ID_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


class TaxIdentificationNumberField(serializers.CharField):
    """Statutory tax identification number."""

    def to_internal_value(self, data: Any) -> str:
        val = super().to_internal_value(data).strip().upper()
        if not TAX_ID_PATTERN.match(val):
            raise serializers.ValidationError("Tax ID must be 5-20 uppercase alphanumeric chars")
        return val


class StrictEnumField(serializers.ChoiceField):
    """Strictly validated enum choice field."""

    def __init__(self, choices: Sequence[Any], **kwargs: Any) -> None:
        super().__init__(choices=choices, **kwargs)

    def to_internal_value(self, data: Any) -> str:
        val = str(data)
        if val not in self.choices:
            raise serializers.ValidationError(
                f"Invalid choice '{val}'. Must be one of: {list(self.choices.keys())}"
            )
        return val
