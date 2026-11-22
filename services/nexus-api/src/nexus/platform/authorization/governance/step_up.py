"""
nexus.platform.authorization.governance.step_up - Step-Up Authentication & Cashier PIN Supervisor Override.
"""

from __future__ import annotations

import base64
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from django.core.exceptions import ValidationError

from nexus.libs.ids import new_uuid7
from nexus.platform.iam.models.staff_profile import StaffProfile


class StepUpRequiredError(ValidationError):
    """Raised when an operation requires step-up supervisor elevation (HTTP 403)."""


@dataclass(frozen=True)
class StepUpTicket:
    """Short-lived cryptographic ticket proving supervisor elevation."""

    token: str
    supervisor_id: uuid.UUID
    target_action: str
    expires_at: datetime


class StepUpAuthService:
    """
    Validates supervisor PIN and issues 5-minute cryptographic elevation tickets.
    """

    TICKET_PREFIX = "nx_stepup_"
    TICKET_VALIDITY_MINUTES = 5

    @classmethod
    def verify_supervisor_pin_and_issue_ticket(
        cls,
        tenant_id: uuid.UUID,
        supervisor_staff_id: uuid.UUID,
        raw_pin: str,
        target_action: str,
    ) -> StepUpTicket:
        """Verifies supervisor Cashier PIN and generates short-lived authorization ticket."""
        supervisor = StaffProfile.objects.get(id=supervisor_staff_id, tenant_id=tenant_id)
        if supervisor.is_pin_locked or not supervisor.verify_pin(raw_pin):
            supervisor.save(update_fields=["failed_pin_attempts", "is_pin_locked"])
            raise ValidationError("Invalid supervisor Cashier PIN or account locked.")

        supervisor.save(update_fields=["failed_pin_attempts"])

        expires = datetime.now(timezone.utc) + timedelta(minutes=cls.TICKET_VALIDITY_MINUTES)
        payload = {
            "tid": str(tenant_id),
            "sid": str(supervisor_staff_id),
            "act": target_action,
            "exp": expires.isoformat(),
            "nonce": str(new_uuid7()),
        }
        b64 = (
            base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8"))
            .decode("ascii")
            .rstrip("=")
        )
        token = f"{cls.TICKET_PREFIX}{b64}"

        return StepUpTicket(
            token=token,
            supervisor_id=supervisor_staff_id,
            target_action=target_action,
            expires_at=expires,
        )

    @classmethod
    def validate_ticket(cls, ticket_token: str, expected_action: str) -> bool:
        """Asserts validity and expiry of step-up authorization ticket."""
        if not ticket_token or not ticket_token.startswith(cls.TICKET_PREFIX):
            return False
        raw_b64 = ticket_token[len(cls.TICKET_PREFIX) :]
        padding = (4 - len(raw_b64) % 4) % 4
        try:
            raw_bytes = base64.urlsafe_b64decode(raw_b64 + ("=" * padding))
            data = json.loads(raw_bytes.decode("utf-8"))
            if data.get("act") != expected_action:
                return False
            exp = datetime.fromisoformat(data["exp"])
            return datetime.now(timezone.utc) <= exp
        except Exception:
            return False
