"""
nexus.libs.serializers.renderers - High-speed JSON serialization renderer.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any
from uuid import UUID

try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False


class _JsonDefaultEncoder(json.JSONEncoder):
    """Fallback JSON encoder for UUID, Decimal, and date types."""

    def default(self, o: Any) -> Any:
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, Decimal):
            return str(o)
        if hasattr(o, "isoformat"):
            return o.isoformat()
        return super().default(o)


class OrjsonResponseRenderer:
    """High-speed JSON renderer with fallback support."""

    @classmethod
    def render(cls, data: Any) -> bytes:
        """Render data to serialized JSON bytes."""
        if HAS_ORJSON:
            return orjson.dumps(
                data,
                option=orjson.OPT_NON_STR_KEYS | orjson.OPT_UTC_Z,
                default=cls._orjson_default,
            )
        return json.dumps(data, cls=_JsonDefaultEncoder).encode("utf-8")

    @staticmethod
    def _orjson_default(obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return str(obj)
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
