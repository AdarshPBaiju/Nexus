"""
nexus.platform.licensing.certs - Ed25519 offline license certificate generation and validation.
"""

from __future__ import annotations

import base64
import json
import uuid
from dataclasses import dataclass
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ed25519


@dataclass(frozen=True)
class LicenseCertPayload:
    """Parameters defining an offline cryptographic license certificate."""

    tenant_id: uuid.UUID | str
    package_code: str
    capacity_limit: int
    expires_epoch: int


class OfflineLicenseCertificateService:
    """
    Generates and verifies Ed25519-signed JSON license certificates for offline desktop execution.
    """

    @classmethod
    def generate_key_pair(cls) -> tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
        private_key = ed25519.Ed25519PrivateKey.generate()
        return private_key, private_key.public_key()

    @classmethod
    def sign_certificate(
        cls,
        private_key: ed25519.Ed25519PrivateKey,
        payload_data: LicenseCertPayload,
    ) -> str:
        payload: dict[str, Any] = {
            "v": 1,
            "tenant_id": str(payload_data.tenant_id),
            "package": payload_data.package_code,
            "capacity": payload_data.capacity_limit,
            "exp": payload_data.expires_epoch,
        }
        canonical_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        signature = private_key.sign(canonical_bytes)

        cert_envelope = {
            "payload": payload,
            "sig": base64.b64encode(signature).decode("ascii"),
        }
        return base64.b64encode(json.dumps(cert_envelope).encode("utf-8")).decode("ascii")

    @classmethod
    def verify_certificate(
        cls,
        public_key: ed25519.Ed25519PublicKey,
        cert_b64: str,
    ) -> dict[str, Any] | None:
        try:
            raw_bytes = base64.b64decode(cert_b64.encode("ascii"))
            envelope = json.loads(raw_bytes.decode("utf-8"))
            payload = envelope["payload"]
            sig_bytes = base64.b64decode(envelope["sig"].encode("ascii"))

            canonical_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
            public_key.verify(sig_bytes, canonical_bytes)
            return payload
        except Exception:
            return None
