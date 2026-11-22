"""
nexus.extensions.base.hr_basic.attendance_service - Shift clocking and cross-midnight attendance.
"""

from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction

from nexus.extensions.base.hr_basic.models.attendance import (
    AttendanceRecord,
    RecordAttendanceDto,
)
from nexus.extensions.base.hr_basic.models.employee import EmployeeProfile


@dataclass(frozen=True)
class ClockInRequestDto:
    """Parameter object for employee clock-in."""

    tenant_id: uuid.UUID
    employee_id: uuid.UUID
    branch_id: uuid.UUID
    clock_in_utc: datetime.datetime
    clock_in_method: str = "WEB"
    cutoff_hour: int = 4


@dataclass(frozen=True)
class ClockOutRequestDto:
    """Parameter object for employee clock-out."""

    tenant_id: uuid.UUID
    employee_id: uuid.UUID
    clock_out_utc: datetime.datetime


@dataclass(frozen=True)
class ManagerCorrectionDto:
    """Parameter object for manager attendance manual correction."""

    record_id: uuid.UUID
    manager_user_id: uuid.UUID
    reason: str
    clock_in_utc: datetime.datetime | None = None
    clock_out_utc: datetime.datetime | None = None


class HrAttendanceService:
    """
    Coordinates shift clock-in, clock-out, cross-midnight business date calculations,
    and audited manager attendance adjustments.
    """

    @classmethod
    def calculate_business_date(
        cls, punch_utc: datetime.datetime, cutoff_hour: int = 4
    ) -> datetime.date:
        """Attributes early morning punches (< cutoff) to the prior business day."""
        if punch_utc.hour < cutoff_hour:
            return punch_utc.date() - datetime.timedelta(days=1)
        return punch_utc.date()

    @classmethod
    @transaction.atomic
    def clock_in(cls, dto: ClockInRequestDto) -> AttendanceRecord:
        """Records clock-in with cross-midnight date calculation and active check."""
        emp = EmployeeProfile.objects.filter(id=dto.employee_id, is_active=True).first()
        if not emp:
            raise ValidationError(
                f"InactiveEmployeeError: Employee '{dto.employee_id}' not found or inactive."
            )

        bdate = cls.calculate_business_date(dto.clock_in_utc, dto.cutoff_hour)
        existing_open = AttendanceRecord.objects.filter(
            tenant_id=dto.tenant_id,
            employee_id=dto.employee_id,
            clock_out_utc__isnull=True,
        ).first()
        if existing_open:
            raise ValidationError(
                "OpenShiftConflictError: Employee has an unclosed clock-in record."
            )

        return AttendanceRecord.record_clock_in(
            RecordAttendanceDto(
                tenant_id=dto.tenant_id,
                employee_id=dto.employee_id,
                branch_id=dto.branch_id,
                business_date=bdate,
                clock_in_utc=dto.clock_in_utc,
                clock_in_method=dto.clock_in_method,
            )
        )

    @classmethod
    @transaction.atomic
    def clock_out(cls, dto: ClockOutRequestDto) -> AttendanceRecord:
        """Closes open clock-in record with clock-out timestamp."""
        record = (
            AttendanceRecord.objects.select_for_update()
            .filter(
                tenant_id=dto.tenant_id,
                employee_id=dto.employee_id,
                clock_out_utc__isnull=True,
            )
            .first()
        )
        if not record:
            raise ValidationError("NoOpenClockInError: No open clock-in record found for employee.")

        if dto.clock_out_utc < record.clock_in_utc:
            raise ValidationError(
                "InvalidClockOutTimeError: Clock-out cannot be earlier than clock-in."
            )

        record.clock_out_utc = dto.clock_out_utc
        record.save(update_fields=["clock_out_utc", "updated_at"])
        return record

    @classmethod
    @transaction.atomic
    def apply_manager_correction(cls, dto: ManagerCorrectionDto) -> AttendanceRecord:
        """Applies manual supervisor correction requiring strict audit reason."""
        if not dto.reason.strip():
            raise ValidationError(
                "MissingAuditReasonError: Manager correction requires justification."
            )

        record = AttendanceRecord.objects.select_for_update().get(id=dto.record_id)
        if dto.clock_in_utc is not None:
            record.clock_in_utc = dto.clock_in_utc
        if dto.clock_out_utc is not None:
            record.clock_out_utc = dto.clock_out_utc

        record.is_manual_override = True
        record.correction_reason = f"Supervisor[{dto.manager_user_id}]: {dto.reason}"
        record.save(
            update_fields=[
                "clock_in_utc",
                "clock_out_utc",
                "is_manual_override",
                "correction_reason",
                "updated_at",
            ]
        )
        return record
