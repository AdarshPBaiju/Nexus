"""
nexus.extensions.base.hr_basic.models.leave - Basic employee leave request model.
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
class SubmitLeaveDto:
    """Parameter object for leave request submission."""

    tenant_id: uuid.UUID
    employee_id: uuid.UUID
    leave_type: str
    start_date: datetime.date
    end_date: datetime.date
    reason: str = ""


class BasicLeaveRequest(TenantScopedModel):
    """
    Standard staff leave request with manager approval workflow.
    """

    class LeaveType(models.TextChoices):
        ANNUAL = "ANNUAL", _("Annual Vacation Leave")
        SICK = "SICK", _("Medical / Sick Leave")
        UNPAID = "UNPAID", _("Authorized Unpaid Leave")

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Awaiting Manager Approval")
        APPROVED = "APPROVED", _("Approved by Manager")
        REJECTED = "REJECTED", _("Rejected")

    employee_id = models.UUIDField(
        db_index=True,
        help_text=_("Associated EmployeeProfile."),
    )
    leave_type = models.CharField(
        max_length=32,
        choices=LeaveType.choices,
        default=LeaveType.ANNUAL,
        db_index=True,
    )
    start_date = models.DateField(
        db_index=True,
        help_text=_("First day of leave."),
    )
    end_date = models.DateField(
        db_index=True,
        help_text=_("Last day of leave (inclusive)."),
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    approver_user_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Manager Identity user ID who approved/rejected."),
    )
    reason = models.TextField(
        blank=True,
        help_text=_("Employee submission explanation."),
    )

    class Meta:
        app_label = "nexus_hr_basic"
        db_table = "hr_basic_leave_request"
        ordering = ["-start_date", "id"]

    @classmethod
    def submit_request(cls, dto: SubmitLeaveDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            employee_id=dto.employee_id,
            leave_type=dto.leave_type,
            start_date=dto.start_date,
            end_date=dto.end_date,
            reason=dto.reason,
            status=cls.Status.PENDING,
        )

    def approve(self, approver_id: uuid.UUID) -> None:
        self.status = self.Status.APPROVED
        self.approver_user_id = approver_id
        self.save(update_fields=["status", "approver_user_id", "updated_at"])

    def __str__(self) -> str:
        return f"LeaveRequest({self.employee_id} - {self.leave_type}: {self.status})"
