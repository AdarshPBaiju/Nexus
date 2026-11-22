"""
nexus.libs.serializers.sentinels - Sentinels for partial patch evaluation.
"""

from __future__ import annotations


class _UnsetType:
    """Sentinel class representing omitted fields in partial updates."""

    def __repr__(self) -> str:
        return "<UNSET>"

    def __bool__(self) -> bool:
        return False


UNSET = _UnsetType()


def is_set(value: object) -> bool:
    """Check if a value is provided (not UNSET)."""
    return value is not UNSET
