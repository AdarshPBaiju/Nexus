"""
nexus.platform.audit.domain.hash_chain - Cryptographic SHA-256 hash chain and Merkle root.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Sequence


class HashChainEngine:
    """Computes entry SHA-256, sequential cumulative hash chain, and Merkle root."""

    GENESIS_HASH = "0" * 64

    @staticmethod
    def canonical_json(data: Any) -> str:
        """Produce deterministic sorted JSON string without spaces."""
        return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)

    @classmethod
    def compute_entry_sha256(cls, payload: dict[str, Any]) -> str:
        """Compute SHA-256 of canonical JSON serialized event payload."""
        canonical = cls.canonical_json(payload)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def compute_chained_hash(prev_hash: str, entry_sha256: str) -> str:
        """Compute cumulative chained hash: SHA256(prev_hash || entry_sha256)."""
        combined = f"{prev_hash}{entry_sha256}".encode("utf-8")
        return hashlib.sha256(combined).hexdigest()

    @classmethod
    def compute_merkle_root(cls, hashes: Sequence[str]) -> str:
        """Compute Merkle tree root hash from a sequence of leaf hashes."""
        if not hashes:
            return cls.GENESIS_HASH
        current_layer = list(hashes)
        while len(current_layer) > 1:
            next_layer: list[str] = []
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                right = current_layer[i + 1] if i + 1 < len(current_layer) else left
                combined = f"{left}{right}".encode("utf-8")
                next_layer.append(hashlib.sha256(combined).hexdigest())
            current_layer = next_layer
        return current_layer[0]
