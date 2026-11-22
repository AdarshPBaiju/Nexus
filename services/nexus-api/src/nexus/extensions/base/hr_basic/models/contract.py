"""
nexus.extensions.base.hr_basic.models.contract - Employment contract with confidential PII encryption.
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
class CreateContractDto:
    """Parameter object for employment contract creation."""

    tenant_id: uuid.UUID
    employee_id: uuid.UUID
    contract_type: str
    salary_ciphertext: str
    salary_blind_index: str
    valid_from: datetime.date
    currency: str = "USD"
    valid_until: datetime.date | None = None


class EmploymentContract(TenantScopedModel):
    """
    Effective-dated employment contract with envelope-encrypted confidential compensation.
    """

    class ContractType(models.TextChoices):
        FULL_TIME = "FULL_TIME", _("Full-Time Permanent Contract")
        PART_TIME = "PART_TIME", _("Part-Time Contract")
        CASUAL = "CASUAL", _("Casual / Hourly Contract")
        SEASONAL = "SEASONAL", _("Seasonal / Fixed-Term Contract")

    employee_id = models.UUIDField(
        db_index=True,
        help_text=_("Associated EmployeeProfile."),
    )
    contract_type = models.CharField(
        max_length=32,
        choices=ContractType.choices,
        default=ContractType.FULL_TIME,
        db_index=True,
    )
    salary_ciphertext = models.TextField(
        help_text=_("AES-256-GCM envelope-encrypted compensation figure."),
    )
    salary_blind_index = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Searchable HMAC-SHA256 blind index hash of compensation."),
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        help_text=_("ISO 4217 contract compensation currency."),
    )
    valid_from = models.DateField(
        db_index=True,
        help_text=_("Start date when contract terms become effective."),
    )
    valid_until = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("End date of contract validity (null for permanent)."),
    )
    is_current = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Designates currently active contract version."),
    )

    class Meta:
        app_label = "nexus_hr_basic"
        db_table = "hr_employment_contract"
        ordering = ["-valid_from", "id"]

    @classmethod
    def create_contract(cls, dto: CreateContractDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            employee_id=dto.employee_id,
            contract_type=dto.contract_type,
            salary_ciphertext=dto.salary_ciphertext,
            salary_blind_index=dto.salary_blind_index,
            currency=dto.currency,
            valid_from=dto.valid_from,
            valid_until=dto.valid_until,
            is_current=True,
        )

    def __str__(self) -> str:
        return f"Contract({self.employee_id} - {self.contract_type} [{self.currency}])"
