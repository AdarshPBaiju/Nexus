"""
nexus.engines.currency_fx.words - Universal Multilingual Amount-in-Words Engine.
Converts exact Money amounts to cheque-ready legal text strings (PNX-FX-ARCH-001).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import ClassVar

from nexus.libs.money.money import Money


@dataclass(frozen=True)
class WordsOptions:
    """Options for AmountInWordsEngine conversion."""

    scale: str = "AUTO"  # "AUTO", "WESTERN_SHORT", "INDIAN_LAKHS"
    casing: str = "TITLE_CASE"  # "TITLE_CASE", "UPPERCASE", "LOWERCASE", "SENTENCE_CASE"
    subunit_format: str = "WORDS"  # "WORDS", "FRACTION_100", "FRACTION_1000", "NONE"
    star_padding: bool = False
    include_only_suffix: bool = True
    main_unit_name: str = ""
    subunit_name: str = ""


class AmountInWordsEngine:
    """Exact multilingual amount-in-words converter."""

    ONES: ClassVar[list[str]] = [
        "",
        "One",
        "Two",
        "Three",
        "Four",
        "Five",
        "Six",
        "Seven",
        "Eight",
        "Nine",
    ]
    TEENS: ClassVar[list[str]] = [
        "Ten",
        "Eleven",
        "Twelve",
        "Thirteen",
        "Fourteen",
        "Fifteen",
        "Sixteen",
        "Seventeen",
        "Eighteen",
        "Nineteen",
    ]
    TENS: ClassVar[list[str]] = [
        "",
        "",
        "Twenty",
        "Thirty",
        "Forty",
        "Fifty",
        "Sixty",
        "Seventy",
        "Eighty",
        "Ninety",
    ]

    CURRENCY_META: ClassVar[dict[str, tuple[str, str, int]]] = {
        "INR": ("Rupees", "Paise", 2),
        "USD": ("Dollars", "Cents", 2),
        "EUR": ("Euros", "Cents", 2),
        "GBP": ("Pounds", "Pence", 2),
        "AED": ("Dirhams", "Fils", 2),
        "SAR": ("Riyals", "Halalas", 2),
        "KWD": ("Dinars", "Fils", 3),
        "JPY": ("Yen", "", 0),
    }

    @classmethod
    def to_words(cls, money: Money, options: WordsOptions | None = None) -> str:
        """Converts Money amount to legal words representation."""
        opts = options or WordsOptions()
        abs_amount = abs(money.amount)
        int_val = int(abs_amount)
        meta = cls.CURRENCY_META.get(money.currency, (money.currency, "Cents", 2))
        decimals = meta[2]

        frac_val = cls._extract_fraction(abs_amount, decimals)
        scale = (
            "INDIAN_LAKHS"
            if (opts.scale == "INDIAN_LAKHS" or (opts.scale == "AUTO" and money.currency == "INR"))
            else "WESTERN_SHORT"
        )

        main_name = opts.main_unit_name or meta[0]
        sub_name = opts.subunit_name or meta[1]

        int_words = "Zero" if int_val == 0 else cls._convert_int(int_val, scale)
        frac_words = cls._convert_frac(frac_val, decimals, sub_name, opts.subunit_format)

        body = f"{int_words} {main_name}"
        if frac_words:
            body += f" and {frac_words}"
        if opts.include_only_suffix:
            body += " Only"

        styled = cls._apply_casing(body, opts.casing)
        return f"*** {styled} ***" if opts.star_padding else styled

    @classmethod
    def _extract_fraction(cls, amount: Decimal, decimals: int) -> int:
        if decimals <= 0:
            return 0
        exp = Decimal(10) ** -decimals
        quantized = amount.quantize(exp)
        parts = f"{quantized:.{decimals}f}".split(".")
        return int(parts[1]) if len(parts) > 1 else 0

    @classmethod
    def _convert_int(cls, val: int, scale: str) -> str:
        if scale == "INDIAN_LAKHS":
            return cls._convert_indian(val)
        return cls._convert_western(val)

    @classmethod
    def _convert_western(cls, val: int) -> str:
        denominations = ["", "Thousand", "Million", "Billion", "Trillion"]
        chunks: list[str] = []
        rem = val
        idx = 0
        while rem > 0 and idx < len(denominations):
            part = rem % 1000
            if part > 0:
                words = cls._convert_three_digits(part)
                denom = denominations[idx]
                chunks.insert(0, f"{words} {denom}".strip())
            rem //= 1000
            idx += 1
        return " ".join(chunks)

    @classmethod
    def _convert_indian(cls, val: int) -> str:
        if val < 1000:
            return cls._convert_three_digits(val)
        chunks: list[str] = []
        last_three = val % 1000
        if last_three > 0:
            chunks.insert(0, cls._convert_three_digits(last_three))
        rem = val // 1000

        denominations = ["Thousand", "Lakh", "Crore", "Arab"]
        idx = 0
        while rem > 0 and idx < len(denominations):
            part = rem % 100
            if part > 0:
                chunks.insert(0, f"{cls._convert_two_digits(part)} {denominations[idx]}")
            rem //= 100
            idx += 1
        return " ".join(chunks)

    @classmethod
    def _convert_three_digits(cls, n: int) -> str:
        hundreds = n // 100
        rem = n % 100
        parts: list[str] = []
        if hundreds > 0:
            parts.append(f"{cls.ONES[hundreds]} Hundred")
        if rem > 0:
            parts.append(cls._convert_two_digits(rem))
        return " ".join(parts)

    @classmethod
    def _convert_two_digits(cls, n: int) -> str:
        if n < 10:
            return cls.ONES[n]
        if n < 20:
            return cls.TEENS[n - 10]
        tens = n // 10
        rem = n % 10
        return f"{cls.TENS[tens]} {cls.ONES[rem]}".strip()

    @classmethod
    def _convert_frac(cls, frac: int, decimals: int, sub_name: str, fmt: str) -> str:
        if decimals == 0 or fmt == "NONE" or frac == 0:
            return ""
        if fmt == "FRACTION_100":
            return f"{frac}/100"
        if fmt == "FRACTION_1000":
            return f"{frac}/1000"
        words = cls._convert_two_digits(frac)
        return f"{words} {sub_name}".strip() if sub_name else words

    @classmethod
    def _apply_casing(cls, text: str, casing: str) -> str:
        if casing == "UPPERCASE":
            return text.upper()
        if casing == "LOWERCASE":
            return text.lower()
        if casing == "SENTENCE_CASE":
            return text.capitalize()
        return text
