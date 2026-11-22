"""
nexus.engines.number_series.domain.radix - Multi-radix encoding engine.
"""

from __future__ import annotations

ALPHABETS: dict[str, str] = {
    "BASE10": "0123456789",
    "BASE16": "0123456789ABCDEF",
    "BASE32_CROCKFORD": "0123456789ABCDEFGHJKMNPQRSTVWXYZ",  # No I, L, O, U
    "BASE36": "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "BASE62": "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
}


class RadixEncoder:
    """Encodes integers into 6 statutory and compact radices."""

    @classmethod
    def encode(cls, value: int, radix: str = "BASE10", min_length: int = 1) -> str:
        """Convert integer into radix string with zero-padding."""
        alphabet = ALPHABETS.get(radix, ALPHABETS["BASE10"])
        base = len(alphabet)

        if value == 0:
            res = alphabet[0]
        else:
            digits: list[str] = []
            curr = abs(value)
            while curr > 0:
                digits.append(alphabet[curr % base])
                curr //= base
            res = "".join(reversed(digits))

        pad_char = alphabet[0]
        if len(res) < min_length:
            res = (pad_char * (min_length - len(res))) + res
        return res
