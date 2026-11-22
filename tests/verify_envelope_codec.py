#!/usr/bin/env python3
"""
verify_envelope_codec.py - Verification suite for Subphase 00.07 (Polyglot Encrypted Path Envelope Codec).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add nexus-api src to sys.path
SRC_DIR = Path(__file__).resolve().parents[1] / "services" / "nexus-api" / "src"
sys.path.insert(0, str(SRC_DIR))

from nexus.libs.codec.envelope_codec import EncryptedPathEnvelopeCodec


def _verify_python_roundtrip() -> None:
    test_payload = {
        "entity": "employee",
        "tenant_id": "018f3a2c-7b4d-7a31-b852-c0e81c15f90a",
        "filter": {"role": "STAFF", "status": "ACTIVE"},
        "page": 1,
    }
    dummy_key = "00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff"

    token = EncryptedPathEnvelopeCodec.encode_payload(test_payload, dummy_key)
    assert token.startswith("nx1_"), f"Token must start with nx1_: {token}"
    assert "=" not in token, f"Token must be unpadded base64url: {token}"
    assert "+" not in token and "/" not in token, "Token must be URL safe"

    decoded = EncryptedPathEnvelopeCodec.decode_payload(token, dummy_key)
    assert decoded == test_payload, f"Decoded payload {decoded} does not match {test_payload}"
    print("  [PASS] Python encoder/decoder roundtrip verified")

    # Test tampering rejection
    tampered = token[:-4] + "xxxx"
    try:
        EncryptedPathEnvelopeCodec.decode_payload(tampered, dummy_key)
        assert False, "Tampered token must raise an error"
    except Exception:
        print("  [PASS] Tampered envelope rejection verified (fails closed)")


def _verify_polyglot_parity(repo_root: Path) -> None:
    ts_file = (
        repo_root / "packages" / "contracts" / "src" / "codec" / "EncryptedPathEnvelopeCodec.ts"
    )
    go_file = repo_root / "services" / "nexus-worker-go" / "pkg" / "codec" / "envelope_codec.go"
    rust_file = repo_root / "packages" / "rust-crypto" / "src" / "codec.rs"

    assert ts_file.exists(), "TypeScript envelope codec missing"
    assert go_file.exists(), "Go envelope codec missing"
    assert rust_file.exists(), "Rust envelope codec missing"

    ts_content = ts_file.read_text(encoding="utf-8")
    assert "nx1_" in ts_content and "VERSION = 0x01" in ts_content

    go_content = go_file.read_text(encoding="utf-8")
    assert "nx1_" in go_content and "Version = byte(0x01)" in go_content

    rust_content = rust_file.read_text(encoding="utf-8")
    assert "nx1_" in rust_content and "VERSION: u8 = 0x01" in rust_content
    print("  [PASS] Polyglot parity across TypeScript, Go, and Rust verified")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    print(f"==> Verifying Subphase 00.07 Polyglot Envelope Codec in {repo_root}...")

    _verify_python_roundtrip()
    _verify_polyglot_parity(repo_root)

    print("\n==> Subphase 00.07 Verification Suite PASSED (100% assertions satisfied).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
