"""
nexus.libs.serializers.fields.temporal - UTC datetime fields.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from rest_framework import serializers


class UtcDateTimeField(serializers.DateTimeField):
    """Ensures ISO 8601 UTC output representation ending in Z."""

    def to_representation(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, datetime):
            utc_dt = value.astimezone(timezone.utc)
            return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        return super().to_representation(value)

    def to_internal_value(self, data: Any) -> datetime:
        dt = super().to_internal_value(data)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
