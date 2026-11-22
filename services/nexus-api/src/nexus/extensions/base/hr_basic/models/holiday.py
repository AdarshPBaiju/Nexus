"""
nexus.extensions.base.hr_basic.models.holiday - Branch statutory holiday calendar model.
"""

from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass
from typing import Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


@dataclass(frozen=True)
class CreateHolidayDto:
    """Parameter object for calendar holiday declaration."""

    tenant_id: uuid.UUID
    holiday_date: datetime.date
    name: str
    is_statutory: bool = True
    branch_id: uuid.UUID | None = None


class HolidayDate(TenantScopedModel):
    """
    Statutory or venue-specific official holiday dates.
    """

    branch_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Branch location (null for tenant-wide holidays)."),
    )
    holiday_date = models.DateField(
        db_index=True,
        help_text=_("Calendar date of the holiday."),
    )
    name = models.CharField(
        max_length=128,
        help_text=_("Official holiday title (e.g. New Year's Day, Labor Day)."),
    )
    is_statutory = models.BooleanField(
        default=True,
        help_text=_("Designates government mandated paid holiday."),
    )

    class Meta:
        app_label = "nexus_hr_basic"
        db_table = "hr_holiday_date"
        unique_together = [("tenant_id", "branch_id", "holiday_date")]
        ordering = ["holiday_date", "id"]

    @classmethod
    def declare_holiday(cls, dto: CreateHolidayDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            branch_id=dto.branch_id,
            holiday_date=dto.holiday_date,
            name=dto.name,
            is_statutory=dto.is_statutory,
        )

    def __str__(self) -> str:
        return f"Holiday({self.holiday_date} - {self.name})"
