"""
nexus.extensions.base.hr_basic.models.employee - Employee master directory model.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


@dataclass(frozen=True)
class CreateEmployeeDto:
    """Parameter object for registering a new employee profile."""

    tenant_id: uuid.UUID
    employee_code: str
    first_name: str
    last_name: str
    department: str = "Operations"
    designation: str = "Staff"
    reporting_manager_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None


class EmployeeProfile(TenantScopedModel):
    """
    Central employee directory profile tracking organizational hierarchy and roles.
    """

    employee_code = models.CharField(
        max_length=32,
        db_index=True,
        help_text=_("Unique employee identification code (e.g. EMP-1001)."),
    )
    user_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Associated Identity platform user account."),
    )
    first_name = models.CharField(
        max_length=64,
        help_text=_("Legal given name."),
    )
    last_name = models.CharField(
        max_length=64,
        help_text=_("Legal family name."),
    )
    department = models.CharField(
        max_length=64,
        default="Operations",
        db_index=True,
        help_text=_("Primary operational department."),
    )
    designation = models.CharField(
        max_length=64,
        default="Staff",
        db_index=True,
        help_text=_("Job title / role designation."),
    )
    reporting_manager_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Foreign key to direct reporting manager EmployeeProfile."),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Designates whether employee is currently active."),
    )

    class Meta:
        app_label = "nexus_hr_basic"
        db_table = "hr_employee_profile"
        unique_together = [("tenant_id", "employee_code")]
        ordering = ["employee_code", "id"]

    @classmethod
    def register_employee(cls, dto: CreateEmployeeDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            employee_code=dto.employee_code,
            first_name=dto.first_name,
            last_name=dto.last_name,
            department=dto.department,
            designation=dto.designation,
            reporting_manager_id=dto.reporting_manager_id,
            user_id=dto.user_id,
        )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return f"Employee({self.employee_code} - {self.full_name})"
