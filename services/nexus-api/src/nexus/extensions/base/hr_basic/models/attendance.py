"""
nexus.extensions.base.hr_basic.models.attendance - Staff attendance and punch clock record.
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
class RecordAttendanceDto:
    """Parameter object for attendance clock-in record."""

    tenant_id: uuid.UUID
    employee_id: uuid.UUID
    branch_id: uuid.UUID
    business_date: datetime.date
    clock_in_utc: datetime.datetime
    clock_in_method: str = "WEB"


class AttendanceRecord(TenantScopedModel):
    """
    Clock-in and clock-out attendance punches mapped to operational venue business dates.
    """

    class ClockMethod(models.TextChoices):
        WEB = "WEB", _("Web Portal 1-Tap Punch")
        PIN = "PIN", _("POS Terminal Cashier PIN")
        QR = "QR", _("Mobile Badge QR Scan")
        BIOMETRIC = "BIOMETRIC", _("Physical LAN Biometric Terminal")

    employee_id = models.UUIDField(
        db_index=True,
        help_text=_("Associated EmployeeProfile."),
    )
    branch_id = models.UUIDField(
        db_index=True,
        help_text=_("Venue branch where punch occurred."),
    )
    business_date = models.DateField(
        db_index=True,
        help_text=_("Operational business date accounting for cross-midnight shift cutoff."),
    )
    clock_in_utc = models.DateTimeField(
        db_index=True,
        help_text=_("UTC timestamp of clock-in punch."),
    )
    clock_out_utc = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("UTC timestamp of clock-out punch."),
    )
    clock_in_method = models.CharField(
        max_length=32,
        choices=ClockMethod.choices,
        default=ClockMethod.WEB,
        db_index=True,
    )
    is_manual_override = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Designates manager attendance audit correction."),
    )
    correction_reason = models.TextField(
        blank=True,
        help_text=_("Mandatory justification for manager overrides."),
    )

    class Meta:
        app_label = "nexus_hr_basic"
        db_table = "hr_attendance_record"
        ordering = ["-business_date", "-clock_in_utc", "id"]
        indexes = [
            models.Index(fields=["tenant_id", "employee_id", "business_date"]),
        ]

    @classmethod
    def record_clock_in(cls, dto: RecordAttendanceDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            employee_id=dto.employee_id,
            branch_id=dto.branch_id,
            business_date=dto.business_date,
            clock_in_utc=dto.clock_in_utc,
            clock_in_method=dto.clock_in_method,
        )

    @property
    def is_open(self) -> bool:
        return self.clock_out_utc is None

    def __str__(self) -> str:
        return f"Attendance({self.employee_id} on {self.business_date}: In {self.clock_in_utc})"
