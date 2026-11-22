"""
nexus.libs.serializers.fields.security - Security and privacy fields.
"""

from __future__ import annotations

import hashlib
from typing import Any

from rest_framework import serializers


class BlindIndexHashField(serializers.Field):
    """Hashes input string into blind index hex digest."""

    def to_representation(self, value: Any) -> str:
        return str(value or "")

    def to_internal_value(self, data: Any) -> str:
        raw = str(data).strip()
        # HMAC/Blind hash simulation
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class MaskedPiiField(serializers.Field):
    """Masks confidential PII fields in representation."""

    def to_representation(self, value: Any) -> str:
        val_str = str(value or "")
        if len(val_str) <= 4:
            return "****"
        return f"**** {val_str[-4:]}"

    def to_internal_value(self, data: Any) -> str:
        return str(data).strip()
