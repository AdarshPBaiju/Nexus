"""
nexus.engines.number_series.domain.feistel - Bijective Feistel pseudo-random integer permuter.
"""

from __future__ import annotations

import math


class FeistelCipherPermuter:
    """
    4-round balanced Feistel cipher providing bijective integer permutation.
    Guarantees zero collisions: f(x) != f(y) for x != y, and f^-1(f(x)) == x.
    """

    @classmethod
    def permute(cls, val: int, domain_size: int, key: int) -> int:
        """Permute integer within domain [0, domain_size - 1]."""
        if domain_size <= 1:
            return val
        half_bits = math.ceil(math.log2(domain_size) / 2)
        side_mask = (1 << half_bits) - 1

        cand = val
        while True:
            left = cand >> half_bits
            right = cand & side_mask

            for r in range(4):
                f_val = cls._round_func(right, key, r, side_mask)
                next_right = left ^ f_val
                left = right
                right = next_right

            cand = (left << half_bits) | right
            if cand < domain_size:
                return cand

    @classmethod
    def unpermute(cls, permuted: int, domain_size: int, key: int) -> int:
        """Reverse permutation to recover original sequential value."""
        if domain_size <= 1:
            return permuted
        half_bits = math.ceil(math.log2(domain_size) / 2)
        side_mask = (1 << half_bits) - 1

        cand = permuted
        while True:
            left = cand >> half_bits
            right = cand & side_mask

            for r in reversed(range(4)):
                f_val = cls._round_func(left, key, r, side_mask)
                prev_left = right ^ f_val
                right = left
                left = prev_left

            cand = (left << half_bits) | right
            if cand < domain_size:
                return cand

    @staticmethod
    def _round_func(x: int, key: int, round_idx: int, mask: int) -> int:
        return ((x * 0x5DEECE66D + key + round_idx * 0xB) ^ 0xA5A5A5A5) & mask
