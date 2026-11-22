"""
nexus.libs.security.path_codec - Polyglot Encrypted Path Envelope Codec (AES-256-GCM + AAD).
Format: nx1{mode}_{base64url(nonce[12B] || ciphertext || tag[16B])}
Modes: 'q' (query), 'd' (detail), 's' (share), 'e' (ephemeral), 'c' (cursor).
"""
from __future__ import annotations

import base64
import json
import os
import uuid
from dataclasses import dataclass
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class PathEnvelopeDecryptionError(ValueError):
    """Raised when an encrypted path envelope is invalid, corrupted, or tampered."""


@dataclass(frozen=True)
class EnvelopeContext:
    """Security context binding tenant, resource, and envelope mode."""

    tenant_id: str | uuid.UUID
    resource: str
    mode: str = "q"


class EncryptedPathCodec:
    """
    Seals and unseals path envelopes eliminating raw UUIDs and query strings from URLs.
    Binds AAD: f"{tenant_id}:{resource}:{mode}:v1" to prevent replay across endpoints.
    """

    PREFIX = "nx1"
    NONCE_BYTES = 12

    @classmethod
    def compute_aad(cls, ctx: EnvelopeContext) -> bytes:
        """Compute Additional Authenticated Data binding tenant, resource, and mode."""
        return f"{ctx.tenant_id}:{ctx.resource}:{ctx.mode}:v1".encode("utf-8")

    @classmethod
    def seal_envelope(
        cls,
        payload: dict[str, Any],
        ctx: EnvelopeContext,
        key: bytes,
    ) -> str:
        """
        Encrypts payload into an opaque URL token: nx1{mode}_{base64url}.
        """
        aesgcm = AESGCM(key)
        nonce = os.urandom(cls.NONCE_BYTES)
        aad = cls.compute_aad(ctx)
        plaintext = json.dumps(payload, separators=(",", ":")).encode("utf-8")

        ciphertext = aesgcm.encrypt(nonce, plaintext, aad)
        raw_token = nonce + ciphertext
        encoded = base64.urlsafe_b64encode(raw_token).decode("ascii").rstrip("=")
        return f"{cls.PREFIX}{ctx.mode}_{encoded}"

    @classmethod
    def unseal_envelope(
        cls,
        token: str,
        tenant_id: str | uuid.UUID,
        resource: str,
        key: bytes,
    ) -> tuple[str, dict[str, Any]]:
        """
        Decrypts and authenticates token, returning (mode, payload).
        """
        if not token.startswith(cls.PREFIX) or "_" not in token:
            raise PathEnvelopeDecryptionError("Invalid token format prefix.")

        prefix_and_mode, raw_b64 = token.split("_", 1)
        mode = prefix_and_mode[len(cls.PREFIX) :]
        if not mode:
            raise PathEnvelopeDecryptionError("Missing envelope mode character.")

        padding = (4 - len(raw_b64) % 4) % 4
        try:
            raw_token = base64.urlsafe_b64decode(raw_b64 + ("=" * padding))
        except Exception as err:
            raise PathEnvelopeDecryptionError("Corrupted base64url encoding.") from err

        if len(raw_token) < cls.NONCE_BYTES + 16:
            raise PathEnvelopeDecryptionError("Truncated ciphertext payload.")

        nonce = raw_token[: cls.NONCE_BYTES]
        ciphertext = raw_token[cls.NONCE_BYTES :]
        ctx = EnvelopeContext(tenant_id=tenant_id, resource=resource, mode=mode)
        aad = cls.compute_aad(ctx)
        aesgcm = AESGCM(key)

        try:
            decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, aad)
            payload = json.loads(decrypted_bytes.decode("utf-8"))
            return mode, payload
        except Exception as err:
            raise PathEnvelopeDecryptionError("Envelope decryption failed or AAD mismatch.") from err
