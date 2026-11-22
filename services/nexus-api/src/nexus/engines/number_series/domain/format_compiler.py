"""
nexus.engines.number_series.domain.format_compiler - Sub-0.25ms format pattern compiler.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Mapping, Optional

from nexus.engines.number_series.domain.radix import RadixEncoder

SEQ_TOKEN_PATTERN = re.compile(r"\{SEQ(?::(\d+))?\}")


@dataclass(frozen=True)
class FormatCompileOptions:
    """Options for compiling formatted dynamic codes."""

    radix: str = "BASE10"
    tokens: Mapping[str, str] = field(default_factory=dict)
    operational_date: Optional[date] = None


class NumberSeriesFormatCompiler:
    """Compiles dynamic code patterns with date, branch, and sequence tokens."""

    @classmethod
    def compile_code(
        cls,
        pattern: str,
        sequence_num: int,
        options: Optional[FormatCompileOptions] = None,
    ) -> str:
        """Replace all placeholders with values and format sequence representation."""
        opts = options or FormatCompileOptions()
        dt = opts.operational_date or date.today()

        code = pattern
        code = code.replace("{YYYY}", f"{dt.year:04d}")
        code = code.replace("{YY}", f"{dt.year % 100:02d}")
        code = code.replace("{MM}", f"{dt.month:02d}")
        code = code.replace("{DD}", f"{dt.day:02d}")

        for k, v in opts.tokens.items():
            code = code.replace(f"{{{k}}}", str(v))

        m = SEQ_TOKEN_PATTERN.search(code)
        if m:
            pad_len = int(m.group(1)) if m.group(1) else 6
            encoded_seq = RadixEncoder.encode(sequence_num, radix=opts.radix, min_length=pad_len)
            code = code[: m.start()] + encoded_seq + code[m.end() :]

        return code
