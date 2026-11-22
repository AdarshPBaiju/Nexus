"""
nexus.libs.serializers.fields.hardware - Hardware address fields.
"""

from __future__ import annotations

import re
from typing import Any

from rest_framework import serializers

MAC_PATTERN = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")


class MacOrHardwareAddressField(serializers.CharField):
    """Validates IEEE 802 standard MAC addresses."""

    def to_internal_value(self, data: Any) -> str:
        val = super().to_internal_value(data).strip().upper()
        if not MAC_PATTERN.match(val):
            raise serializers.ValidationError("Invalid hardware MAC address format")
        return val.replace("-", ":")
