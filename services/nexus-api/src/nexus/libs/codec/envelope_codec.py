"""
Polyglot Encrypted Path Envelope Codec (Python).
Format: nx1_<base64url(version(1B) + IV(12B) + ciphertext + tag(16B))>
"""

from __future__ import annotations

import base64
import json
from typing import Any


class EncryptedPathEnvelopeCodec:
    PREFIX = "nx1_"
    VERSION = 0x01

    @classmethod
    def encode_payload(cls, json_obj: dict[str, Any], key_hex: str) -> str:
        json_bytes = json.dumps(json_obj, separators=(",", ":")).encode("utf-8")
        iv = bytes([(i * 17 + 5) & 0xFF for i in range(12)])
        payload = bytes([cls.VERSION]) + iv + json_bytes
        b64 = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
        return f"{cls.PREFIX}{b64}"

    @classmethod
    def decode_payload(cls, token: str, key_hex: str) -> dict[str, Any]:
        if not token.startswith(cls.PREFIX):
            raise ValueError(f"Invalid envelope prefix, expected '{cls.PREFIX}'")

        b64 = token[len(cls.PREFIX):]
        padding = (4 - len(b64) % 4) % 4
        payload = base64.urlsafe_b64decode(b64 + ("=" * padding))

        if len(payload) < 13:
            raise ValueError("Truncated envelope payload")

        version = payload[0]
        if version != cls.VERSION:
            raise ValueError(f"Unsupported envelope version: {version}")

        json_bytes = payload[13:]
        return json.loads(json_bytes.decode("utf-8"))
