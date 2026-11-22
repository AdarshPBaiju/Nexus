"""
nexus.extensions.base.hr_basic.models.shift_assignment - Weekly recurring shift assignment model.
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
class AssignShiftDto:
    """Parameter object for shift assignment."""

    tenant_id: uuid.UUID
    employee_id: uuid.UUID
    branch_id: uuid.UUID
    day_of_week: int
    start_time: datetime.time
    end_time: datetime.time


class BasicShiftAssignment(TenantScopedModel):
    """
    Weekly recurring shift assignment mapping employee to branch day and working hours.
    """

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, _("Monday")
        TUESDAY = 1, _("Tuesday")
        WEDNESDAY = 2, _("Wednesday")
        THURSDAY = 3, _("Thursday")
        FRIDAY = 4, _("Friday")
        SATURDAY = 5, _("Saturday")
        SUNDAY = 6, _("Sunday")

    employee_id = models.UUIDField(
        db_index=True,
        help_text=_("Associated EmployeeProfile."),
    )
    branch_id = models.UUIDField(
        db_index=True,
        help_text=_("Target venue branch location."),
    )
    day_of_week = models.IntegerField(
        choices=DayOfWeek.choices,
        db_index=True,
        help_text=_("Day of week (0=Monday, 6=Sunday)."),
    )
    start_time = models.TimeField(
        help_text=_("Scheduled shift start time."),
    )
    end_time = models.TimeField(
        help_text=_("Scheduled shift end time."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Designates whether assignment is currently active in roster."),
    )

    class Meta:
        app_label = "nexus_hr_basic"
        db_table = "hr_basic_shift_assignment"
        ordering = ["day_of_week", "start_time", "id"]

    @classmethod
    def assign_shift(cls, dto: AssignShiftDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            employee_id=dto.employee_id,
            branch_id=dto.branch_id,
            day_of_week=dto.day_of_week,
            start_time=dto.start_time,
            end_time=dto.end_time,
            is_active=True,
        )

    def __str__(self) -> str:
        return (
            f"Shift({self.employee_id} - Day {self.day_of_week}: {self.start_time}-{self.end_time})"
        )
