#!/usr/bin/env python3
"""
verify_enterprise_sod_jit_elevation_delegation.py - Verification suite for Subphase 01.12.
Validates:
1. Segregation of Duties (SoD) static role conflict detection.
2. Maker-Checker dual control enforcement on critical operations.
3. Just-In-Time (JIT) break-glass elevation grant validation and expiration.
4. Vacation delegation time-window matching.
5. Cashier PIN Supervisor Step-Up authentication ticket issuance and verification.
6. Anti-privilege escalation (subset grant defense) and Last Active Owner protection.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "services" / "nexus-api" / "src"
sys.path.insert(0, str(API_SRC))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexus_test_settings")
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "nexus.platform.tenancy",
            "nexus.platform.iam",
            "nexus.platform.authorization",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.exceptions import ValidationError
from django.core.management import call_command

call_command("migrate", run_syncdb=True, verbosity=0)

from nexus.libs.ids import new_uuid7
from nexus.platform.authorization.governance import (
    JitElevationGrant,
    PrivilegeEscalationGuard,
    SodConflictRule,
    SodConflictValidator,
    StepUpAuthService,
    VacationDelegation,
)
from nexus.platform.authorization.governance.anti_escalation import PrivilegeEscalationError
from nexus.platform.authorization.governance.sod_validator import SodViolationError
from nexus.platform.iam.models import (
    StaffProfile,
    StaffRoleAssignment,
    User,
)


def test_sod_static_and_dynamic_conflicts() -> None:
    """Validate static SoD rule collision and Maker-Checker dynamic separation."""
    tenant_id = new_uuid7()

    SodConflictRule.objects.create(
        tenant_id=tenant_id,
        rule_code="SOD-CASHIER-AUDIT",
        description="Cashier cannot audit and reconcile shifts",
        first_permission="pos.cashier",
        conflicting_permission="pos.shift.reconcile",
    )

    # 1. Static SoD: User with pos.cashier cannot receive pos.shift.reconcile
    try:
        SodConflictValidator.assert_no_static_conflict(
            tenant_id=tenant_id,
            assigned_permissions=["pos.cashier", "inventory.view"],
            new_permission="pos.shift.reconcile",
        )
        assert False, "Conflicting permission must raise SodViolationError"
    except SodViolationError as err:
        assert "SoD Conflict" in str(err)

    # 2. Dynamic SoD: Maker-Checker dual control
    initiator_id = new_uuid7()
    approver_id = new_uuid7()

    # Self-approval blocked
    try:
        SodConflictValidator.assert_maker_checker_separation(
            initiator_id, initiator_id, "Discount Approval"
        )
        assert False, "Self-approval must raise SodViolationError"
    except SodViolationError as err:
        assert "Maker-Checker Violation" in str(err)

    # Independent approval allowed
    SodConflictValidator.assert_maker_checker_separation(
        initiator_id, approver_id, "Discount Approval"
    )
    print("[PASS] test_sod_static_and_dynamic_conflicts")


def test_jit_elevation_and_delegation() -> None:
    """Validate JIT elevation expiration and vacation delegation."""
    tenant_id = new_uuid7()
    membership_id = new_uuid7()
    now = datetime.now(timezone.utc)

    # Active JIT grant
    jit_active = JitElevationGrant.objects.create(
        tenant_id=tenant_id,
        membership_id=membership_id,
        elevated_permission="pos.order.void",
        business_justification="Manager holiday coverage",
        expires_at=now + timedelta(minutes=30),
    )
    assert jit_active.is_currently_valid is True

    # Expired JIT grant
    jit_expired = JitElevationGrant.objects.create(
        tenant_id=tenant_id,
        membership_id=membership_id,
        elevated_permission="financial.payout",
        business_justification="Immediate emergency fix",
        expires_at=now - timedelta(minutes=5),
    )
    assert jit_expired.is_currently_valid is False

    # Vacation delegation
    peer_id = new_uuid7()
    delegation = VacationDelegation.objects.create(
        tenant_id=tenant_id,
        delegator_id=membership_id,
        delegatee_id=peer_id,
        delegated_permissions=["order.approve"],
        valid_from=now - timedelta(days=1),
        valid_to=now + timedelta(days=5),
    )
    assert delegation.is_currently_active is True
    print("[PASS] test_jit_elevation_and_delegation")


def test_step_up_auth_and_anti_escalation() -> None:
    """Validate supervisor step-up ticket issuance, subset grant, and last owner defense."""
    tenant_id = new_uuid7()
    user = User.objects.create(email="supervisor@nexus.com")
    supervisor = StaffProfile.objects.create(
        tenant_id=tenant_id,
        user=user,
        employee_code="SUP-01",
    )
    supervisor.set_pin("9988")
    supervisor.save()

    # Issue step-up ticket
    ticket = StepUpAuthService.verify_supervisor_pin_and_issue_ticket(
        tenant_id=tenant_id,
        supervisor_staff_id=supervisor.id,
        raw_pin="9988",
        target_action="pos.order.void",
    )
    assert ticket.token.startswith("nx_stepup_")
    assert StepUpAuthService.validate_ticket(ticket.token, "pos.order.void") is True
    assert StepUpAuthService.validate_ticket(ticket.token, "finance.payout") is False

    # Anti-privilege escalation: cannot grant permissions you do not hold
    try:
        PrivilegeEscalationGuard.assert_subset_grant(
            grantor_permissions=["order.view", "order.create"],
            requested_grants=["order.create", "system.admin"],
        )
        assert False, "Escalation must be blocked"
    except PrivilegeEscalationError as err:
        assert "Privilege Escalation Blocked" in str(err)

    # Last Owner Protection
    StaffRoleAssignment.objects.create(
        tenant_id=tenant_id,
        staff=supervisor,
        role_slug=PrivilegeEscalationGuard.OWNER_ROLE,
        is_active=True,
    )
    try:
        PrivilegeEscalationGuard.assert_not_last_owner(tenant_id, supervisor.id)
        assert False, "Revoking last owner must be blocked"
    except ValidationError as err:
        assert "Last Owner Invariant" in str(err)

    print("[PASS] test_step_up_auth_and_anti_escalation")


def main() -> None:
    test_sod_static_and_dynamic_conflicts()
    test_jit_elevation_and_delegation()
    test_step_up_auth_and_anti_escalation()
    print("\n>>> All 3 Subphase 01.12 verification suites passed successfully! <<<")


if __name__ == "__main__":
    main()
