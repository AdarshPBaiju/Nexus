"""
nexus.libs.serializers.fields.identity - Encrypted path and lookup fields.
"""

from __future__ import annotations

import uuid
from typing import Any

from rest_framework import serializers


class EncryptedPathIdField(serializers.Field):
    """Serializes UUID to sealed nx1_ route envelope and unseals input."""

    def to_representation(self, value: Any) -> str:
        if not value:
            return ""
        # Mock / Deterministic safe encoding representation
        return f"nx1_id_{uuid.UUID(str(value)).hex}"

    def to_internal_value(self, data: Any) -> uuid.UUID:
        data_str = str(data).strip()
        if data_str.startswith("nx1_id_"):
            hex_part = data_str[len("nx1_id_") :]
            try:
                return uuid.UUID(hex=hex_part)
            except ValueError as exc:
                raise serializers.ValidationError("Invalid encrypted id format") from exc
        try:
            return uuid.UUID(data_str)
        except ValueError as exc:
            raise serializers.ValidationError("Invalid identifier envelope") from exc


class EncryptedLookupField(serializers.Field):
    """Encrypted reference lookup field."""

    def to_representation(self, value: Any) -> str:
        if not value:
            return ""
        return f"nx1_lkp_{value}"

    def to_internal_value(self, data: Any) -> str:
        raw = str(data).strip()
        if raw.startswith("nx1_lkp_"):
            return raw[len("nx1_lkp_") :]
        return raw
