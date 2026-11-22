"""
tests.unit.test_currency_formatter - Comprehensive test suite for DynamicCurrencyFormatter & AmountInWordsEngine.
Verifies all 18 formatting dimensions and multilingual Amount-in-Words scales.
"""

import unittest
from decimal import Decimal

from nexus.engines.currency_fx.formatter import CurrencyFormatProfile, DynamicCurrencyFormatter
from nexus.engines.currency_fx.words import AmountInWordsEngine, WordsOptions
from nexus.libs.money.money import Money


class DynamicCurrencyFormatterTest(unittest.TestCase):
    def test_standard_western_usd_format(self) -> None:
        m = Money.of(Decimal("1234567.89"), "USD")
        res = DynamicCurrencyFormatter.format(m)
        self.assertEqual(res, "$ 1,234,567.89")

    def test_indian_lakhs_crores_grouping(self) -> None:
        m = Money.of(Decimal("1234567.50"), "INR")
        prof = CurrencyFormatProfile(grouping_pattern=(3, 2), symbol_mode="UNICODE_SYMBOL")
        res = DynamicCurrencyFormatter.format(m, prof)
        self.assertEqual(res, "₹ 12,34,567.50")

    def test_european_splitters_and_suffix_symbol(self) -> None:
        m = Money.of(Decimal("1234.56"), "EUR")
        prof = CurrencyFormatProfile(
            decimal_splitter=",",
            thousands_splitter=".",
            symbol_position="SUFFIX",
        )
        res = DynamicCurrencyFormatter.format(m, prof)
        self.assertEqual(res, "1.234,56 €")

    def test_negative_accounting_parens(self) -> None:
        m = Money.of(Decimal("-500.25"), "USD")
        prof = CurrencyFormatProfile(negative_format="ACCOUNTING_PARENS")
        res = DynamicCurrencyFormatter.format(m, prof)
        self.assertEqual(res, "($ 500.25)")

    def test_negative_dr_cr_suffix(self) -> None:
        m = Money.of(Decimal("-1250.00"), "GBP")
        prof = CurrencyFormatProfile(negative_format="DR_CR_SUFFIX")
        res = DynamicCurrencyFormatter.format(m, prof)
        self.assertEqual(res, "£ 1,250.00 DR")

    def test_zero_format_dash(self) -> None:
        m = Money.zero("USD")
        prof = CurrencyFormatProfile(zero_format="DASH")
        res = DynamicCurrencyFormatter.format(m, prof)
        self.assertEqual(res, "—")

    def test_arabic_indic_numeral_script(self) -> None:
        m = Money.of(Decimal("1250.50"), "AED")
        prof = CurrencyFormatProfile(
            decimal_splitter="٫",
            thousands_splitter="٬",
            numeral_script="ARABIC_INDIC",
        )
        res = DynamicCurrencyFormatter.format(m, prof)
        self.assertEqual(res, "د.إ ١٬٢٥٠٫٥٠")

    def test_bidi_isolation(self) -> None:
        m = Money.of(Decimal("99.99"), "USD")
        prof = CurrencyFormatProfile(bidi_isolation=True)
        res = DynamicCurrencyFormatter.format(m, prof)
        self.assertEqual(res, '<bdi dir="ltr">$ 99.99</bdi>')


class AmountInWordsEngineTest(unittest.TestCase):
    def test_western_short_scale(self) -> None:
        m = Money.of(Decimal("1250.50"), "USD")
        res = AmountInWordsEngine.to_words(m)
        self.assertEqual(res, "One Thousand Two Hundred Fifty Dollars and Fifty Cents Only")

    def test_indian_lakhs_scale(self) -> None:
        m = Money.of(Decimal("1234567.50"), "INR")
        res = AmountInWordsEngine.to_words(m)
        expected = (
            "Twelve Lakh Thirty Four Thousand Five Hundred Sixty Seven Rupees and Fifty Paise Only"
        )
        self.assertEqual(res, expected)

    def test_cheque_fraction_and_star_padding(self) -> None:
        m = Money.of(Decimal("2500.50"), "USD")
        opts = WordsOptions(
            subunit_format="FRACTION_100",
            star_padding=True,
            casing="UPPERCASE",
        )
        res = AmountInWordsEngine.to_words(m, opts)
        self.assertEqual(res, "*** TWO THOUSAND FIVE HUNDRED DOLLARS AND 50/100 ONLY ***")

    def test_zero_decimal_jpy(self) -> None:
        m = Money.of(Decimal("50000"), "JPY")
        res = AmountInWordsEngine.to_words(m)
        self.assertEqual(res, "Fifty Thousand Yen Only")


if __name__ == "__main__":
    unittest.main()
