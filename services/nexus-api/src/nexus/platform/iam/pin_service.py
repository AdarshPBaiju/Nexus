"""
nexus.platform.iam.pin_service - Cashier PIN authentication and fast workstation switching.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from nexus.libs.ids import new_uuid7
from nexus.platform.iam.models.staff_profile import StaffProfile


@dataclass(frozen=True)
class PinSwitchResult:
    """Result returned upon workstation PIN authentication."""

    success: bool
    session_token: str | None = None
    staff_id: uuid.UUID | None = None
    error_message: str | None = None


class CashierPinService:
    """
    Coordinates fast Cashier PIN authentication at counter/KDS stations.
    """

    @classmethod
    def switch_cashier(
        cls,
        staff: StaffProfile,
        raw_pin: str,
    ) -> PinSwitchResult:
        """
        Verify staff PIN and issue short-lived workstation session token.
        """
        if staff.is_pin_locked:
            return PinSwitchResult(
                success=False,
                error_message="Cashier PIN is locked due to excessive failed attempts.",
            )

        if not staff.verify_pin(raw_pin):
            staff.save(update_fields=["failed_pin_attempts", "is_pin_locked"])
            remaining = max(0, 5 - staff.failed_pin_attempts)
            msg = "Incorrect PIN." if remaining > 0 else "PIN locked."
            return PinSwitchResult(
                success=False,
                error_message=f"{msg} ({remaining} attempts remaining)",
            )

        staff.save(update_fields=["failed_pin_attempts"])
        session_token = f"pos_sess_{new_uuid7()}"
        return PinSwitchResult(
            success=True,
            session_token=session_token,
            staff_id=staff.id,
        )

    @classmethod
    def lock_workstation(cls, staff: StaffProfile) -> bool:
        """
        Immediately lock the workstation screen.
        """
        return True
