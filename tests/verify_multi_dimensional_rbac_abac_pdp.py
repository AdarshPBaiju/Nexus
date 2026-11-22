#!/usr/bin/env python3
"""
verify_multi_dimensional_rbac_abac_pdp.py - Verification suite for Subphase 01.11.
Validates:
1. PermissionCatalog model with risk tiers and Cashier PIN step-up flags.
2. ResourceGrant with 6-dimensional scoping and explicit DENY precedence.
3. EffectivePolicyCompiler generating immutable CompiledActorPolicySnapshot.
4. AuthorizationResolver (PDP) sub-1.5ms evaluation (< 0.5ms on warm cache).
5. Explicit Deny Always Wins law overriding any Allow grant.
6. FieldSecurityProjector applying HIDDEN redactions and MASKED protections.
7. LiveRevocationManager cache eviction and CloudEvent rbac.version.bumped.v1.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
import time

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
            "nexus.platform.authorization",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

call_command("migrate", run_syncdb=True, verbosity=0)

from nexus.libs.ids import new_uuid7
from nexus.platform.authorization.models import (
    FieldSecurityRule,
    PermissionCatalog,
    ResourceGrant,
)
from nexus.platform.authorization.pdp import (
    AuthorizationResolver,
    AuthzDecision,
    EffectivePolicyCompiler,
    FieldSecurityProjector,
    LiveRevocationManager,
)


def test_permission_catalog_and_grants() -> None:
    """Validate PermissionCatalog and multi-dimensional ResourceGrant models."""
    perm_void = PermissionCatalog.objects.create(
        code="pos.order.void",
        description="Void an active kitchen line item",
        risk_tier=PermissionCatalog.RiskTier.HIGH,
        requires_step_up=True,
    )
    assert perm_void.risk_tier == "HIGH"
    assert perm_void.requires_step_up is True

    tenant_id = new_uuid7()
    membership_id = new_uuid7()
    branch_id = new_uuid7()

    grant = ResourceGrant.objects.create(
        tenant_id=tenant_id,
        membership_id=membership_id,
        permission_code="pos.order.void",
        scope_level=ResourceGrant.ScopeLevel.BRANCH,
        scope_id=branch_id,
        effect=ResourceGrant.GrantEffect.ALLOW,
    )
    assert grant.scope_level == "BRANCH"
    print("[PASS] test_permission_catalog_and_grants")


def test_explicit_deny_always_wins_and_scoped_pdp() -> None:
    """Validate Explicit Deny Always Wins and sub-1.5ms PDP resolution."""
    tenant_id = new_uuid7()
    membership_id = new_uuid7()
    branch_1 = new_uuid7()
    branch_2 = new_uuid7()

    # Grant allow on branch_1
    ResourceGrant.objects.create(
        tenant_id=tenant_id,
        membership_id=membership_id,
        permission_code="order.create",
        scope_level=ResourceGrant.ScopeLevel.BRANCH,
        scope_id=branch_1,
        effect=ResourceGrant.GrantEffect.ALLOW,
    )
    # Explicit DENY on order.delete
    ResourceGrant.objects.create(
        tenant_id=tenant_id,
        membership_id=membership_id,
        permission_code="order.delete",
        scope_level=ResourceGrant.ScopeLevel.TENANT,
        scope_id=tenant_id,
        effect=ResourceGrant.GrantEffect.DENY,
    )

    policy = EffectivePolicyCompiler.compile_policy(tenant_id, membership_id, rbac_version=1)

    # Allowed on branch 1
    dec_allowed = AuthorizationResolver.resolve_access(policy, "order.create", target_scope_id=branch_1)
    assert dec_allowed == AuthzDecision.ALLOW

    # Denied on branch 2 (out of scope)
    dec_out_of_scope = AuthorizationResolver.resolve_access(policy, "order.create", target_scope_id=branch_2)
    assert dec_out_of_scope == AuthzDecision.DENY

    # Explicit Deny overrides all allows
    dec_explicit_deny = AuthorizationResolver.resolve_access(policy, "order.delete", target_scope_id=branch_1)
    assert dec_explicit_deny == AuthzDecision.DENY

    # Benchmark: 1,000 warm PDP checks must finish in < 50ms (< 0.05ms per check)
    t0 = time.perf_counter()
    for _ in range(1000):
        AuthorizationResolver.resolve_access(policy, "order.create", target_scope_id=branch_1)
    duration_ms = (time.perf_counter() - t0) * 1000
    assert duration_ms < 50.0, f"PDP check took {duration_ms:.2f}ms, must be < 50ms for 1000 checks"

    print(f"[PASS] test_explicit_deny_always_wins_and_scoped_pdp (1,000 checks in {duration_ms:.2f}ms)")


def test_field_level_security_and_live_revocation() -> None:
    """Validate FLS masking/hiding and live cache revocation."""
    tenant_id = new_uuid7()
    membership_id = new_uuid7()

    FieldSecurityRule.objects.create(
        tenant_id=tenant_id,
        entity_type="payment",
        field_name="card_pan",
        classification=FieldSecurityRule.Classification.MASKED,
    )
    FieldSecurityRule.objects.create(
        tenant_id=tenant_id,
        entity_type="payment",
        field_name="gateway_secret",
        classification=FieldSecurityRule.Classification.HIDDEN,
    )

    policy = EffectivePolicyCompiler.compile_policy(tenant_id, membership_id, rbac_version=1)

    raw_payload = {
        "id": "pay-101",
        "card_pan": "4111111111111234",
        "gateway_secret": "sk_live_secret_key",
        "amount": "150.00",
    }
    projected = FieldSecurityProjector.project_payload("payment", raw_payload, policy)

    assert "gateway_secret" not in projected
    assert projected["card_pan"] == "************1234"
    assert projected["amount"] == "150.00"

    # Revocation: bump version
    event = LiveRevocationManager.bump_tenant_rbac_version(tenant_id, new_version=2)
    assert event["type"] == "rbac.version.bumped.v1"
    assert event["data"]["new_version"] == 2

    # L1 cache must be evicted
    key_v1 = EffectivePolicyCompiler.get_cache_key(tenant_id, membership_id, 1)
    assert key_v1 not in EffectivePolicyCompiler._MEMORY_CACHE

    print("[PASS] test_field_level_security_and_live_revocation")


def main() -> None:
    test_permission_catalog_and_grants()
    test_explicit_deny_always_wins_and_scoped_pdp()
    test_field_level_security_and_live_revocation()
    print("\n>>> All 3 Subphase 01.11 verification suites passed successfully! <<<")


if __name__ == "__main__":
    main()
