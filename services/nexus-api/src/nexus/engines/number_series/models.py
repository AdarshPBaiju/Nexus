"""
nexus.engines.number_series.models - Number series definition, counter & reservation models.
"""

from __future__ import annotations

from django.db import models

from nexus.libs.models import TenantScopedModel


class NumberSeriesDefinition(TenantScopedModel):
    """Declarative definition for dynamic numbering sequence targets."""

    name = models.CharField(max_length=128)
    entity_target = models.CharField(max_length=64, db_index=True)
    format_pattern = models.CharField(max_length=255, default="DOC/{YYYY}/{SEQ:6}")
    radix = models.CharField(max_length=32, default="BASE10")
    padding_length = models.IntegerField(default=6)
    reset_frequency = models.CharField(max_length=32, default="NEVER")
    use_feistel = models.BooleanField(default=False)
    feistel_key = models.BigIntegerField(default=133742)

    class Meta:
        db_table = "num_series_definition"
        ordering = ["name"]


class NumberSeriesCounter(TenantScopedModel):
    """Monotonic high-water-mark counter locked via canonical row locking."""

    series_def = models.ForeignKey(
        NumberSeriesDefinition, on_delete=models.CASCADE, related_name="counters"
    )
    partition_key = models.CharField(max_length=128, default="DEFAULT", db_index=True)
    current_value = models.BigIntegerField(default=0)
    high_water_mark = models.BigIntegerField(default=0)
    last_reset_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "num_series_counter"
        unique_together = [("tenant_id", "series_def", "partition_key")]
        ordering = ["id"]


class NumberSeriesReservation(TenantScopedModel):
    """Temporary lease reservation and reclaim pool for draft checkouts."""

    counter = models.ForeignKey(
        NumberSeriesCounter, on_delete=models.CASCADE, related_name="reservations"
    )
    reserved_number = models.BigIntegerField()
    ttl_expires_at = models.DateTimeField()
    status = models.CharField(max_length=32, default="RESERVED", db_index=True)

    class Meta:
        db_table = "num_series_reservation"
        ordering = ["reserved_number"]
