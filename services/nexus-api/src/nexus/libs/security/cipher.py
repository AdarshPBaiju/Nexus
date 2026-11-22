"""
nexus.libs.security.cipher - AES-256-GCM Tenant Envelope Cipher with AAD binding.
Format: v1:<base64url(nonce[12B] || ciphertext || tag[16B])>
"""

from __future__ import annotations

import base64
import os
import uuid
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from nexus.libs.security.kms import TenantKmsKeyService


class CryptographicIntegrityError(ValueError):
    """Raised when ciphertext authentication or AAD validation fails."""


@dataclass(frozen=True)
class CipherContext:
    """
    Immutable parameter context for cryptographic envelope operations.
    """

    tenant_id: uuid.UUID | str
    entity_label: str
    row_id: uuid.UUID | str
    field_name: str


class TenantEnvelopeCipher:
    """
    Field-level envelope cipher using AES-256-GCM.
    Binds Additional Authenticated Data (AAD):
    AAD = f"{tenant_id}:{entity_label}:{row_id}:{field_name}:v1"
    """

    VERSION_PREFIX = "v1:"
    NONCE_BYTES = 12

    def __init__(self, kms_service: TenantKmsKeyService | None = None) -> None:
        self._kms = kms_service or TenantKmsKeyService()

    @staticmethod
    def compute_aad(ctx: CipherContext) -> bytes:
        """
        Compute immutable Additional Authenticated Data (AAD) for ciphertext binding.
        """
        return f"{ctx.tenant_id}:{ctx.entity_label}:{ctx.row_id}:{ctx.field_name}:v1".encode(
            "utf-8"
        )

    def encrypt(self, ctx: CipherContext, plaintext: str) -> str:
        """
        Encrypt plaintext with per-tenant DEK and AAD binding.
        """
        dek = self._kms.get_or_create_dek(ctx.tenant_id)
        aesgcm = AESGCM(dek)
        nonce = os.urandom(self.NONCE_BYTES)
        aad = self.compute_aad(ctx)

        ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), aad)
        payload = nonce + ciphertext
        encoded = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
        return f"{self.VERSION_PREFIX}{encoded}"

    def decrypt(self, ctx: CipherContext, envelope: str) -> str:
        """
        Decrypt and verify ciphertext envelope against AAD.
        """
        if not envelope.startswith(self.VERSION_PREFIX):
            raise CryptographicIntegrityError("Invalid or unsupported envelope version prefix")

        raw_b64 = envelope[len(self.VERSION_PREFIX) :]
        padding = (4 - len(raw_b64) % 4) % 4
        try:
            payload = base64.urlsafe_b64decode(raw_b64 + ("=" * padding))
        except Exception as err:
            raise CryptographicIntegrityError("Corrupted base64url envelope") from err

        if len(payload) < self.NONCE_BYTES + 16:
            raise CryptographicIntegrityError("Truncated ciphertext payload")

        nonce = payload[: self.NONCE_BYTES]
        ciphertext = payload[self.NONCE_BYTES :]
        dek = self._kms.get_or_create_dek(ctx.tenant_id)
        aesgcm = AESGCM(dek)
        aad = self.compute_aad(ctx)

        try:
            decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, aad)
            return decrypted_bytes.decode("utf-8")
        except Exception as err:
            raise CryptographicIntegrityError(
                "Decryption failed: AAD mismatch or tampered ciphertext"
            ) from err
