"""
nexus.platform.authorization.governance.sod_validator - Segregation of Duties (SoD) Validator.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from django.core.exceptions import ValidationError

from nexus.platform.authorization.governance.models.sod_rule import SodConflictRule


class SodViolationError(ValidationError):
    """Raised when an action or grant violates statutory Segregation of Duties rules."""


class SodConflictValidator:
    """
    Validates static role incompatibility and dynamic Maker-Checker separation.
    """

    @classmethod
    def assert_no_static_conflict(
        cls,
        tenant_id: uuid.UUID,
        assigned_permissions: Sequence[str],
        new_permission: str,
    ) -> None:
        """
        Ensures new permission does not conflict with already assigned permissions.
        """
        rules = SodConflictRule.objects.filter(tenant_id=tenant_id, is_active=True)
        assigned_set = set(assigned_permissions)

        for rule in rules:
            if (
                rule.first_permission == new_permission
                and rule.conflicting_permission in assigned_set
            ):
                raise SodViolationError(
                    f"SoD Conflict: Cannot grant '{new_permission}' because user already holds conflicting '{rule.conflicting_permission}' ({rule.rule_code})."
                )
            if (
                rule.conflicting_permission == new_permission
                and rule.first_permission in assigned_set
            ):
                raise SodViolationError(
                    f"SoD Conflict: Cannot grant '{new_permission}' because user already holds conflicting '{rule.first_permission}' ({rule.rule_code})."
                )

    @classmethod
    def assert_maker_checker_separation(
        cls,
        creator_id: uuid.UUID,
        approver_id: uuid.UUID,
        action_name: str,
    ) -> None:
        """
        Enforces dynamic Maker-Checker separation: creator cannot approve their own document.
        """
        if creator_id == approver_id:
            raise SodViolationError(
                f"Maker-Checker Violation: Initiator {creator_id} cannot independently approve {action_name}. Dual control required."
            )
