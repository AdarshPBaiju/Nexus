#!/usr/bin/env python3
"""
verify_visual_rbac_studio_frontend_guards.py - Verification suite for Subphase 01.13.
Validates:
1. AuthzCliRunner commands: sync_catalog, sod_check, pdp_bench, explain.
2. AccessSimulator 5-layer explanation trace (RLS -> Cap Gate -> Scoped RBAC -> ABAC -> FLS/SoD).
3. Explicit Deny Always Wins in AccessSimulator.
4. Scope boundary validation in AccessSimulator.
5. Presence and structural integrity of ClientAuthorizationStore and UI components.
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "services" / "nexus-api" / "src"
sys.path.insert(0, str(API_SRC))
sys.path.insert(0, str(REPO_ROOT))

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
            "nexus.platform.authorization",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

call_command("migrate", run_syncdb=True, verbosity=0)

from nexus.platform.authorization.pdp.policy_compiler import CompiledActorPolicySnapshot
from nexus.platform.authorization.pdp.resolver import AuthzDecision
from nexus.platform.authorization.pdp.simulator import AccessSimulator
from ops.cli.authz_cli import AuthzCliRunner


def test_authz_cli_commands() -> None:
    assert AuthzCliRunner.sync_catalog() == 0, "sync_catalog command must return 0"
    assert AuthzCliRunner.sod_check() == 0, "sod_check command must return 0"
    assert AuthzCliRunner.pdp_bench(iterations=1000) == 0, "pdp_bench must pass"
    assert AuthzCliRunner.explain("pos.order.create") == 0, "explain command must return 0"
    print("[PASS] test_authz_cli_commands")


def _build_test_policy(tenant_id: uuid.UUID, branch_id: uuid.UUID) -> CompiledActorPolicySnapshot:
    return CompiledActorPolicySnapshot(
        tenant_id=tenant_id,
        membership_id=uuid.uuid4(),
        allowed_permissions=frozenset(["pos.order.create", "order.view"]),
        denied_permissions=frozenset(["pos.order.delete"]),
        scoped_grants={
            "pos.order.create": [("BRANCH", str(branch_id))],
            "order.view": [("TENANT", str(tenant_id))],
        },
        fls_rules={"pos_order:total_amount": "READ"},
        rbac_version=1,
    )


def test_access_simulator_allow() -> None:
    tenant_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    policy = _build_test_policy(tenant_id, branch_id)

    report = AccessSimulator.simulate(policy, "pos.order.create", target_scope_id=branch_id)
    assert report.decision == AuthzDecision.ALLOW
    assert len(report.trace_steps) == 5
    assert report.trace_steps[0].layer_name == "Hard RLS Isolation"
    assert report.trace_steps[1].layer_name == "Capability Gate"
    assert report.trace_steps[2].layer_name == "Multi-Dimensional Scoped RBAC"
    assert report.trace_steps[3].layer_name == "ABAC Guardrails"
    assert report.trace_steps[4].layer_name == "FLS & SoD Compliance"
    print("[PASS] test_access_simulator_allow")


def test_access_simulator_denials() -> None:
    tenant_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    policy = _build_test_policy(tenant_id, branch_id)

    # Explicit Deny
    report_deny = AccessSimulator.simulate(policy, "pos.order.delete")
    assert report_deny.decision == AuthzDecision.DENY
    assert "Explicit DENY" in report_deny.final_reason

    # Missing Permission
    report_missing = AccessSimulator.simulate(policy, "ledger.post")
    assert report_missing.decision == AuthzDecision.DENY
    assert "lacks granted permission" in report_missing.final_reason

    # Scope Mismatch
    mismatch_scope = uuid.uuid4()
    report_scope = AccessSimulator.simulate(
        policy, "pos.order.create", target_scope_id=mismatch_scope
    )
    assert report_scope.decision == AuthzDecision.DENY
    assert "Scope boundary mismatch" in report_scope.final_reason
    print("[PASS] test_access_simulator_denials")


def test_frontend_contracts_and_components() -> None:
    base_contracts = REPO_ROOT / "packages" / "contracts" / "src" / "authz"
    base_ui = REPO_ROOT / "packages" / "ui" / "src" / "authz"

    assert (base_contracts / "ClientAuthorizationStore.ts").exists()
    assert (base_ui / "PermissionGate.tsx").exists()
    assert (base_ui / "SensitiveFieldMask.tsx").exists()
    assert (base_ui / "index.ts").exists()
    print("[PASS] test_frontend_contracts_and_components")


if __name__ == "__main__":
    test_authz_cli_commands()
    test_access_simulator_allow()
    test_access_simulator_denials()
    test_frontend_contracts_and_components()
    print("ALL VISUAL RBAC STUDIO & FRONTEND GUARDS VERIFICATIONS PASSED")
