"""
nexus.libs.security.kms - Tenant KMS Key Service for Data Encryption Key (DEK) lifecycle.
"""

from __future__ import annotations

import os
import threading
import time
import uuid


class TenantKmsKeyService:
    """
    Thread-safe in-memory cache for per-tenant Data Encryption Keys (DEKs).
    Simulates Regional KMS envelope key wrapping with automatic 1-hour expiration.
    """

    DEFAULT_TTL_SECONDS: int = 3600
    KEY_LENGTH_BYTES: int = 32

    def __init__(self, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        self._ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[bytes, float]] = {}
        self._lock = threading.Lock()

    def get_or_create_dek(self, tenant_id: uuid.UUID | str) -> bytes:
        """
        Retrieve or generate a 256-bit DEK for the specified tenant.
        """
        tid = str(tenant_id)
        now = time.monotonic()

        with self._lock:
            if tid in self._cache:
                key, expiry = self._cache[tid]
                if now < expiry:
                    return key

            new_key = os.urandom(self.KEY_LENGTH_BYTES)
            self._cache[tid] = (new_key, now + self._ttl_seconds)
            return new_key

    def evict_dek(self, tenant_id: uuid.UUID | str) -> None:
        """
        Evict a specific tenant DEK from memory.
        """
        tid = str(tenant_id)
        with self._lock:
            self._cache.pop(tid, None)

    def purge_all_keys(self) -> None:
        """
        Synchronously purge all cached keys on tenant switch or system reset.
        """
        with self._lock:
            self._cache.clear()
