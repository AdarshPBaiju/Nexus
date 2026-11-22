"""
nexus.engines.number_series.services.allocator - Monotonic sequence allocator service.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Mapping, Optional

from django.db import transaction

from nexus.engines.number_series.domain.feistel import FeistelCipherPermuter
from nexus.engines.number_series.domain.format_compiler import (
    FormatCompileOptions,
    NumberSeriesFormatCompiler,
)
from nexus.engines.number_series.models import (
    NumberSeriesCounter,
    NumberSeriesDefinition,
    NumberSeriesReservation,
)


@dataclass(frozen=True)
class AllocationRequest:
    """Parameters for sequence number allocation."""

    partition_key: str = "DEFAULT"
    tokens: Mapping[str, str] = field(default_factory=dict)
    operational_date: Optional[date] = None


class NumberSeriesAllocator:
    """Allocates monotonic, gapless, and Feistel-obfuscated dynamic code series."""

    @classmethod
    def allocate_next(
        cls,
        tenant_id: uuid.UUID,
        series_def: NumberSeriesDefinition,
        request: Optional[AllocationRequest] = None,
    ) -> str:
        """In-transaction sequential number allocation with canonical row locking."""
        req = request or AllocationRequest()
        op_date = req.operational_date or date.today()

        with transaction.atomic():
            counter = cls._get_or_create_locked_counter(
                tenant_id, series_def, req.partition_key
            )
            cls._check_lazy_reset(counter, series_def.reset_frequency, op_date)
            seq_num = cls._claim_or_increment(counter)

            raw_seq = seq_num
            if series_def.use_feistel:
                domain_size = 10**series_def.padding_length
                raw_seq = FeistelCipherPermuter.permute(
                    seq_num, domain_size, series_def.feistel_key
                )

            options = FormatCompileOptions(
                radix=series_def.radix,
                tokens=req.tokens,
                operational_date=op_date,
            )
            return NumberSeriesFormatCompiler.compile_code(
                pattern=series_def.format_pattern,
                sequence_num=raw_seq,
                options=options,
            )

    @staticmethod
    def _get_or_create_locked_counter(
        tenant_id: uuid.UUID,
        series_def: NumberSeriesDefinition,
        partition_key: str,
    ) -> NumberSeriesCounter:
        counter, _ = NumberSeriesCounter.objects.get_or_create(
            tenant_id=tenant_id,
            series_def=series_def,
            partition_key=partition_key,
        )
        return (
            NumberSeriesCounter.objects.select_for_update()
            .order_by("id")
            .get(id=counter.id)
        )

    @staticmethod
    def _check_lazy_reset(
        counter: NumberSeriesCounter, frequency: str, op_date: date
    ) -> None:
        if frequency == "YEARLY" and counter.last_reset_date:
            if counter.last_reset_date.year != op_date.year:
                counter.current_value = 0
                counter.last_reset_date = op_date
        elif (
            frequency == "MONTHLY"
            and counter.last_reset_date
            and (counter.last_reset_date.year, counter.last_reset_date.month)
            != (op_date.year, op_date.month)
        ):
            counter.current_value = 0
            counter.last_reset_date = op_date

    @staticmethod
    def _claim_or_increment(counter: NumberSeriesCounter) -> int:
        reclaimed = (
            NumberSeriesReservation.objects.filter(
                counter=counter, status="RECLAIMED"
            )
            .order_by("reserved_number")
            .first()
        )
        if reclaimed:
            num = reclaimed.reserved_number
            reclaimed.delete()
            return num

        counter.current_value += 1
        if counter.current_value > counter.high_water_mark:
            counter.high_water_mark = counter.current_value
        counter.save(
            update_fields=["current_value", "high_water_mark", "last_reset_date", "updated_at"]
        )
        return counter.current_value
