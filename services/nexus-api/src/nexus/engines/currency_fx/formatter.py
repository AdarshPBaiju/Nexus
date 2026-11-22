"""
nexus.engines.currency_fx.formatter - Dynamic Currency Formatter Engine.
100% data-driven 18-dimension currency formatter with exact Decimal math (PNX-FX-ARCH-001).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal
from typing import ClassVar

from nexus.libs.money.money import Money


@dataclass(frozen=True)
class CurrencyFormatProfile:
    """Configurable 18-dimension currency format profile."""

    display_decimals: int = 2
    accounting_decimals: int = 2
    trim_trailing_zeros: bool = False
    decimal_splitter: str = "."
    thousands_splitter: str = ","
    grouping_pattern: tuple[int, ...] = (3,)
    symbol_mode: str = "UNICODE_SYMBOL"
    custom_symbol_text: str = ""
    symbol_position: str = "PREFIX_AFTER_SIGN"
    symbol_spacing: str = "SPACE"
    negative_format: str = "MINUS_PREFIX"
    zero_format: str = "STANDARD"
    numeral_script: str = "LATIN"
    bidi_isolation: bool = False
    positive_sign_display: str = "NEVER"


class DynamicCurrencyFormatter:
    """Exact string-decimal currency formatter with zero IEEE-754 precision loss."""

    SYMBOLS: ClassVar[dict[str, str]] = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "AED": "د.إ",
        "SAR": "ر.س",
        "KWD": "KD",
        "JPY": "¥",
        "CAD": "CA$",
        "AUD": "A$",
        "QAR": "QR",
        "OMR": "OMR",
        "BHD": "BD",
    }

    SCRIPTS: ClassVar[dict[str, list[str]]] = {
        "LATIN": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        "ARABIC_INDIC": ["٠", "١", "٢", "٣", "٤", "٥", "٦", "٧", "٨", "٩"],
        "EXTENDED_ARABIC_PERSIAN": ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"],
        "DEVANAGARI": ["०", "१", "२", "३", "४", "५", "६", "७", "८", "९"],
    }

    @classmethod
    def format(cls, money: Money, profile: CurrencyFormatProfile | None = None) -> str:
        """Formats Money according to 18-dimension CurrencyFormatProfile."""
        prof = profile or CurrencyFormatProfile()
        is_zero = money.amount == Decimal(0)
        is_negative = money.amount < Decimal(0)

        if is_zero and prof.zero_format != "STANDARD":
            return cls._format_zero_state(prof.zero_format)

        abs_amount = abs(money.amount)
        int_str, frac_str = cls._quantize_and_split(abs_amount, prof)
        grouped_int = cls._apply_grouping(int_str, prof.thousands_splitter, prof.grouping_pattern)

        num_body = f"{grouped_int}{prof.decimal_splitter}{frac_str}" if frac_str else grouped_int
        num_body = cls._apply_script(num_body, prof.numeral_script)
        symbol = cls._resolve_symbol(money.currency, prof)

        formatted = cls._assemble(num_body, symbol, is_negative, prof)
        return f'<bdi dir="ltr">{formatted}</bdi>' if prof.bidi_isolation else formatted

    @classmethod
    def _format_zero_state(cls, zero_format: str) -> str:
        if zero_format == "DASH":
            return "—"
        if zero_format == "BLANK":
            return ""
        return "FREE"

    @classmethod
    def _quantize_and_split(cls, amount: Decimal, prof: CurrencyFormatProfile) -> tuple[str, str]:
        exp = Decimal(10) ** -prof.display_decimals
        quantized = amount.quantize(exp, rounding=ROUND_HALF_EVEN)
        parts = f"{quantized:.{prof.display_decimals}f}".split(".")
        int_part = parts[0]
        frac_part = parts[1] if len(parts) > 1 else ""
        if prof.trim_trailing_zeros and frac_part:
            frac_part = frac_part.rstrip("0")
        return int_part, frac_part

    @classmethod
    def _apply_grouping(cls, int_str: str, splitter: str, pattern: tuple[int, ...]) -> str:
        if not splitter or not pattern or len(int_str) <= pattern[0]:
            return int_str

        chunks: list[str] = []
        remaining = int_str
        idx = 0
        while remaining:
            take = pattern[min(idx, len(pattern) - 1)]
            if len(remaining) <= take:
                chunks.insert(0, remaining)
                break
            split_at = len(remaining) - take
            chunks.insert(0, remaining[split_at:])
            remaining = remaining[:split_at]
            idx += 1
        return splitter.join(chunks)

    @classmethod
    def _apply_script(cls, value: str, script: str) -> str:
        if script == "LATIN" or script not in cls.SCRIPTS:
            return value
        digits = cls.SCRIPTS[script]
        return "".join(digits[ord(c) - 48] if "0" <= c <= "9" else c for c in value)

    @classmethod
    def _resolve_symbol(cls, currency: str, prof: CurrencyFormatProfile) -> str:
        if prof.symbol_mode == "NONE":
            return ""
        if prof.symbol_mode == "ISO_CODE":
            return currency
        if prof.symbol_mode == "CUSTOM_TEXT" and prof.custom_symbol_text:
            return prof.custom_symbol_text
        return cls.SYMBOLS.get(currency, currency)

    @classmethod
    def _assemble(cls, body: str, symbol: str, is_neg: bool, prof: CurrencyFormatProfile) -> str:
        sp = (
            " "
            if prof.symbol_spacing == "SPACE"
            else ("\u00a0" if prof.symbol_spacing == "NBSP" else "")
        )
        plus = "+" if (not is_neg and prof.positive_sign_display == "EXPLICIT_PLUS") else ""

        if not is_neg:
            if not symbol:
                return f"{plus}{body}"
            return (
                f"{plus}{body}{sp}{symbol}"
                if prof.symbol_position == "SUFFIX"
                else f"{symbol}{sp}{plus}{body}"
            )

        if prof.negative_format == "ACCOUNTING_PARENS":
            return f"({symbol}{sp}{body})" if symbol else f"({body})"
        if prof.negative_format == "MINUS_SUFFIX":
            return f"{symbol}{sp}{body}-" if symbol else f"{body}-"
        if prof.negative_format == "DR_CR_SUFFIX":
            return f"{symbol}{sp}{body} DR" if symbol else f"{body} DR"
        return f"-{symbol}{sp}{body}" if symbol else f"-{body}"
