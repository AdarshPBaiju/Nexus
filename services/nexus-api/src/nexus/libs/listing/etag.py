"""
nexus.libs.listing.etag - Listing Weak ETag Builder & 304 Fast Path Evaluator.
"""
from __future__ import annotations

import hashlib


class ListingETagBuilder:
    """
    Generates and matches deterministic Weak ETags for instant 304 Not Modified responses.
    """

    @classmethod
    def build_weak_etag(
        cls,
        entity_type: str,
        fav_version: int,
        filter_hash: str,
        cursor_token: str | None,
    ) -> str:
        """Constructs Weak ETag: W/\"nx:{entity}:{fav_ver}:{filter_8}:{cur_8}\"."""
        cur_clean = cursor_token or "root"
        cur_h = hashlib.sha256(cur_clean.encode("utf-8")).hexdigest()[:8]
        f_h = hashlib.sha256(filter_hash.encode("utf-8")).hexdigest()[:8]
        return f'W/"nx:{entity_type}:{fav_version}:{f_h}:{cur_h}"'

    @classmethod
    def is_304_match(cls, if_none_match: str | None, current_etag: str) -> bool:
        """Asserts whether incoming client If-None-Match matches server Weak ETag."""
        if not if_none_match:
            return False
        clean_client = if_none_match.strip()
        clean_server = current_etag.strip()
        return clean_client == clean_server or clean_client == f'W/"{clean_server.strip("W/\"")}"'
