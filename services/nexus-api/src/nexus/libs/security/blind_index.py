"""
nexus.libs.security.blind_index - Searchable blind index hasher for encrypted fields.
"""

from __future__ import annotations

import hashlib
import hmac
import unicodedata


class BlindIndexHasher:
    """
    Computes deterministic HMAC-SHA256 blind index hashes over NFKC-normalized strings.
    Truncated to 16 bytes for indexed equality lookups on encrypted PII.
    """

    INDEX_TRUNCATE_BYTES = 16

    @classmethod
    def compute_index(cls, tenant_salt: bytes | str, value: str) -> bytes:
        """
        Compute a 16-byte blind index hash from a plaintext value.
        """
        salt_bytes = tenant_salt.encode("utf-8") if isinstance(tenant_salt, str) else tenant_salt
        normalized = unicodedata.normalize("NFKC", value).strip().lower()
        val_bytes = normalized.encode("utf-8")

        digest = hmac.new(salt_bytes, val_bytes, hashlib.sha256).digest()
        return digest[: cls.INDEX_TRUNCATE_BYTES]

    @classmethod
    def compute_index_hex(cls, tenant_salt: bytes | str, value: str) -> str:
        """
        Compute hexadecimal representation of the blind index.
        """
        return cls.compute_index(tenant_salt, value).hex()
