"""
nexus.libs.ids - Monotonic timestamp-ordered UUIDv7 generator (RFC 9562).
"""

from __future__ import annotations

import os
import time
import uuid


def new_uuid7() -> uuid.UUID:
    """
    Generate a monotonic timestamp-ordered UUIDv7 according to RFC 9562.

    Layout:
    - 48 bits: Unix timestamp in milliseconds
    - 4 bits: Version 7 (0b0111)
    - 12 bits: Random sequence
    - 2 bits: Variant 2 (0b10)
    - 62 bits: Random data
    """
    ms = int(time.time() * 1000)
    rand_bytes = os.urandom(10)

    time_hi = (ms >> 16) & 0xFFFFFFFF
    time_mid = ms & 0xFFFF

    time_hi_and_ver = 0x7000 | ((rand_bytes[0] << 8 | rand_bytes[1]) & 0x0FFF)
    clk_seq_and_var = 0x8000 | ((rand_bytes[2] << 8 | rand_bytes[3]) & 0x3FFF)
    node = int.from_bytes(rand_bytes[4:10], byteorder="big")

    return uuid.UUID(
        fields=(
            time_hi,
            time_mid,
            time_hi_and_ver,
            clk_seq_and_var >> 8,
            clk_seq_and_var & 0xFF,
            node,
        )
    )
