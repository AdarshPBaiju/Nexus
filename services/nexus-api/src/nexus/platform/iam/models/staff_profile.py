"""
nexus.platform.iam.models.staff_profile - Tenant-specific staff profile and Cashier PIN model.
"""

from __future__ import annotations

import hashlib

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel
from nexus.platform.iam.models.user import User


class StaffProfile(TenantScopedModel):
    """
    Tenant-specific operational staff profile with Cashier PIN credentials.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="staff_profiles",
        help_text=_("Global identity associated with this staff profile."),
    )
    employee_code = models.CharField(
        max_length=32,
        help_text=_("Human-readable unique employee identifier (e.g. EMP-101)."),
    )
    pin_hash = models.CharField(
        max_length=128,
        help_text=_("Salted SHA-256 hash of the 4-6 digit numeric Cashier PIN."),
    )
    is_pin_locked = models.BooleanField(
        default=False,
        help_text=_("Designates whether workstation PIN access is currently locked."),
    )
    failed_pin_attempts = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Consecutive failed PIN unlock attempts (locks after 5)."),
    )

    class Meta:
        app_label = "iam"
        db_table = "iam_staff_profile"
        unique_together = [("tenant_id", "employee_code")]
        ordering = ["employee_code", "id"]

    @classmethod
    def hash_pin(cls, raw_pin: str, salt: str) -> str:
        """Compute salted SHA-256 hash of raw numeric PIN."""
        return hashlib.sha256(f"{salt}:{raw_pin}".encode("utf-8")).hexdigest()

    def set_pin(self, raw_pin: str) -> None:
        """Set a validated 4-6 digit numeric Cashier PIN."""
        if not raw_pin.isdigit() or not (4 <= len(raw_pin) <= 6):
            raise ValidationError({"pin": _("Cashier PIN must be strictly 4 to 6 numeric digits.")})
        self.pin_hash = self.hash_pin(raw_pin, str(self.tenant_id))
        self.failed_pin_attempts = 0
        self.is_pin_locked = False

    def verify_pin(self, candidate_pin: str) -> bool:
        """Verify candidate PIN and manage lock counter."""
        if self.is_pin_locked:
            return False

        expected_hash = self.hash_pin(candidate_pin, str(self.tenant_id))
        if self.pin_hash == expected_hash:
            self.failed_pin_attempts = 0
            return True

        self.failed_pin_attempts += 1
        if self.failed_pin_attempts >= 5:
            self.is_pin_locked = True
        return False

    def unlock_pin(self) -> None:
        """Administrative unlock of workstation PIN."""
        self.is_pin_locked = False
        self.failed_pin_attempts = 0

    def __str__(self) -> str:
        return f"StaffProfile({self.employee_code}, locked={self.is_pin_locked})"
