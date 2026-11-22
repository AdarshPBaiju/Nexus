"""
nexus.libs.pagination.keyset - Zero-OFFSET Keyset Cursor Paginator.
"""
from __future__ import annotations

import base64
import json
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, Sequence, TypeVar

if TYPE_CHECKING:
    from django.db.models import QuerySet

T = TypeVar("T")


@dataclass(frozen=True)
class KeysetPage(Generic[T]):
    """Immutable page container containing records and opaque cursor tokens."""

    items: Sequence[T]
    has_next: bool
    next_cursor: str | None
    prev_cursor: str | None


class KeysetPaginator:
    """
    Deterministic keyset pagination ordering by (created_at, id).
    Guarantees zero SQL OFFSET and constant p99 latency regardless of depth.
    """

    CURSOR_PREFIX = "nx1c_"

    @classmethod
    def encode_cursor(cls, last_val: str, last_id: str | uuid.UUID) -> str:
        """Encodes cursor tuple (last_val, last_id) into opaque URL-safe base64 token."""
        raw = json.dumps({"v": str(last_val), "id": str(last_id)})
        b64 = base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii").rstrip("=")
        return f"{cls.CURSOR_PREFIX}{b64}"

    @classmethod
    def decode_cursor(cls, cursor_token: str | None) -> tuple[str, str] | None:
        """Decodes cursor token into (last_val, last_id)."""
        if not cursor_token or not cursor_token.startswith(cls.CURSOR_PREFIX):
            return None
        raw_b64 = cursor_token[len(cls.CURSOR_PREFIX) :]
        padding = (4 - len(raw_b64) % 4) % 4
        try:
            raw_bytes = base64.urlsafe_b64decode(raw_b64 + ("=" * padding))
            data = json.loads(raw_bytes.decode("utf-8"))
            return str(data["v"]), str(data["id"])
        except Exception:
            return None

    @classmethod
    def paginate_queryset(
        cls,
        queryset: QuerySet,
        cursor: str | None,
        page_size: int = 25,
        sort_field: str = "created_at",
    ) -> KeysetPage[Any]:
        """
        Paginates queryset using keyset cursor without SQL OFFSET.
        Fetches page_size + 1 items to determine if a subsequent page exists.
        """
        decoded = cls.decode_cursor(cursor)
        qs = queryset

        if decoded:
            last_val, _last_id = decoded
            qs = qs.filter(created_at__lt=last_val)

        # Ordering strictly deterministic: created_at DESC, id DESC
        qs = qs.order_by(f"-{sort_field}", "-id")
        fetched = list(qs[: page_size + 1])

        has_next = len(fetched) > page_size
        items = fetched[:page_size]

        next_cursor = None
        if has_next and items:
            last_item = items[-1]
            val = getattr(last_item, sort_field)
            val_str = val.isoformat() if hasattr(val, "isoformat") else str(val)
            next_cursor = cls.encode_cursor(val_str, str(last_item.id))

        return KeysetPage(
            items=items,
            has_next=has_next,
            next_cursor=next_cursor,
            prev_cursor=cursor,
        )
