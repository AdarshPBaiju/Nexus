"""
nexus.extensions.channels.sms.segment_estimator - SMS GSM-7 vs UCS-2 Cost Inflation Guard.
"""
from __future__ import annotations

import math

from nexus.engines.notifications.contracts.types import SmsSegmentEstimate


class SegmentCostEstimator:
    """
    Analyzes SMS copy to prevent unexpected multi-segment billing inflation from non-GSM characters.
    """

    GSM_7_BASIC = frozenset(
        "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ"
        " !\"#¤%&'()*+,-./0123456789:;<=>?"
        "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§"
        "¿abcdefghijklmnopqrstuvwxyzäöñüà"
    )
    GSM_7_EXTENDED = frozenset("|^€{}[~]\\")

    @classmethod
    def find_non_gsm_characters(cls, text: str) -> list[str]:
        """Scans and extracts all characters outside the standard GSM 03.38 alphabet."""
        non_gsm: list[str] = []
        for ch in text:
            if ch not in cls.GSM_7_BASIC and ch not in cls.GSM_7_EXTENDED and ch not in non_gsm:
                non_gsm.append(ch)
        return non_gsm

    @classmethod
    def estimate(cls, text: str) -> SmsSegmentEstimate:
        """Computes billable segment count, encoding format, and non-GSM detection."""
        non_gsm = cls.find_non_gsm_characters(text)
        has_non_gsm = len(non_gsm) > 0
        char_count = len(text)

        if has_non_gsm:
            return cls._calculate_ucs2(char_count, non_gsm)
        return cls._calculate_gsm7(char_count)

    @classmethod
    def _calculate_ucs2(cls, char_count: int, non_gsm: list[str]) -> SmsSegmentEstimate:
        segments = math.ceil(char_count / 67) if char_count > 70 else (1 if char_count > 0 else 0)
        return SmsSegmentEstimate(
            segment_count=max(segments, 1) if char_count > 0 else 0,
            encoding="UCS_2",
            char_count=char_count,
            max_per_segment=70 if char_count <= 70 else 67,
            has_non_gsm=True,
            non_gsm_chars=non_gsm,
        )

    @classmethod
    def _calculate_gsm7(cls, char_count: int) -> SmsSegmentEstimate:
        segments = math.ceil(char_count / 153) if char_count > 160 else (1 if char_count > 0 else 0)
        return SmsSegmentEstimate(
            segment_count=max(segments, 1) if char_count > 0 else 0,
            encoding="GSM_7",
            char_count=char_count,
            max_per_segment=160 if char_count <= 160 else 153,
            has_non_gsm=False,
            non_gsm_chars=[],
        )
