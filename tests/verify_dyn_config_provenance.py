#!/usr/bin/env python3
"""
verify_dyn_config_provenance.py - Verification suite for Subphase 01.04.
Validates:
1. 6-level inheritance hierarchy resolution (Platform -> Tenant -> Brand -> Branch -> Zone -> Workstation).
2. 9-field provenance metadata attached to all resolved keys.
3. RFC 7396 merge patch behavior (null deletes, dict merges, primitive overrides).
4. Pre-publish simulation conflict detection (parent locks & statutory guardrails).
5. DynamicConfigNode, DynamicConfigRevision, and ConfigSimulationRun persistence.
6. Weak ETag generation for cache invalidation.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
import uuid

# Add nexus-api src to sys.path
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
            "nexus.platform.config",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

call_command("migrate", run_syncdb=True, verbosity=0)

from nexus.libs.ids import new_uuid7
from nexus.platform.config.engine import (
    ConfigResolutionEngine,
    LockStatus,
)
from nexus.platform.config.models import (
    ConfigSchemaRegistry,
    ConfigSimulationRun,
    DynamicConfigNode,
    DynamicConfigRevision,
)


def test_rfc7396_merge_patch() -> None:
    """Test RFC 7396 JSON Merge Patch operations."""
    target = {
        "title": "Default Venue",
        "tax_rate": 5.0,
        "features": {"dine_in": True, "kds_enabled": False},
        "to_delete": "temp_value",
    }
    patch = {
        "title": "Flagship Café",
        "features": {"kds_enabled": True},
        "to_delete": None,
        "new_key": 42,
    }
    res = ConfigResolutionEngine.apply_merge_patch(target, patch)
    assert res["title"] == "Flagship Café"
    assert res["tax_rate"] == 5.0
    assert res["features"]["dine_in"] is True
    assert res["features"]["kds_enabled"] is True
    assert "to_delete" not in res
    assert res["new_key"] == 42
    print("[PASS] test_rfc7396_merge_patch")


def _build_test_inheritance_chain() -> list[dict[str, Any]]:
    """Build mock 6-level inheritance hierarchy nodes."""
    return [
        {
            "scope_level": "PLATFORM",
            "revision_id": "rev_plat",
            "config": {"currency": "USD", "vat_rate": 0.20, "theme": "dark"},
            "locks": {"vat_rate": LockStatus.STATUTORY_GUARDRAIL.value},
        },
        {
            "scope_level": "TENANT",
            "revision_id": "rev_ten",
            "config": {"theme": "light", "brand_color": "#0055ff"},
            "locks": {},
        },
        {
            "scope_level": "BRAND",
            "revision_id": "rev_brand",
            "config": {"brand_color": "#11aa22"},
            "locks": {},
        },
        {
            "scope_level": "BRANCH",
            "revision_id": "rev_branch",
            "config": {"receipt_footer": "Thank you for visiting!"},
            "locks": {},
        },
        {
            "scope_level": "ZONE",
            "revision_id": "rev_zone",
            "config": {"audio_volume": 75},
            "locks": {},
        },
        {
            "scope_level": "WORKSTATION",
            "revision_id": "rev_station",
            "config": {"kds_bump_sound": True, "theme": "high-contrast-pos"},
            "locks": {},
        },
    ]


def _assert_provenance_record(rec: Any) -> None:
    """Assert all 9 provenance metadata fields exist and are valid."""
    assert rec.effective_value is not None
    assert rec.source_level is not None
    assert rec.source_revision_id is not None
    assert isinstance(rec.inheritance_chain, list)
    assert rec.override_history_ref.startswith("hist_")
    assert rec.lock_status == LockStatus.UNLOCKED
    assert rec.validation_status == "VALID"
    assert rec.resolved_at is not None
    assert rec.applicable_plugin_version == "v1.0.0"


def test_6_level_inheritance_and_provenance() -> None:
    """Test resolution across all 6 levels with 9-field provenance."""
    chain = _build_test_inheritance_chain()
    prov = ConfigResolutionEngine.resolve_effective_config(chain)

    assert prov["currency"].effective_value == "USD"
    assert prov["currency"].source_level == "PLATFORM"
    assert prov["vat_rate"].lock_status == LockStatus.STATUTORY_GUARDRAIL

    # Theme was overridden by workstation
    assert prov["theme"].effective_value == "high-contrast-pos"
    assert prov["theme"].source_level == "WORKSTATION"
    assert prov["theme"].inheritance_chain == ["PLATFORM", "TENANT", "WORKSTATION"]

    _assert_provenance_record(prov["theme"])
    print("[PASS] test_6_level_inheritance_and_provenance")


def test_simulation_conflict_detection() -> None:
    """Test pre-publish dry-run simulation detecting lock conflicts."""
    base_config = {"vat_rate": 0.20, "store_name": "Main Café"}
    locks = {"vat_rate": LockStatus.STATUTORY_GUARDRAIL.value}

    # Attempting to override locked vat_rate
    patch = {"vat_rate": 0.05, "store_name": "Downtown Café"}
    forecast = ConfigResolutionEngine.simulate_revision(base_config, patch, locks)

    assert not forecast.is_safe
    assert len(forecast.conflicts) == 1
    assert "Cannot override locked key 'vat_rate'" in forecast.conflicts[0]
    assert "store_name" in forecast.diff
    assert forecast.diff["store_name"] == ("Main Café", "Downtown Café")
    print("[PASS] test_simulation_conflict_detection")


def test_config_models_persistence() -> None:
    """Test ORM models for schema, nodes, revisions, and simulations."""
    schema = ConfigSchemaRegistry.objects.create(
        module_code="CAFE_QSR",
        schema_json={"type": "object", "properties": {"auto_print": {"type": "boolean"}}},
    )
    assert schema.module_code == "CAFE_QSR"

    tenant_id = new_uuid7()
    node = DynamicConfigNode.objects.create(
        tenant_id=tenant_id,
        scope_level=DynamicConfigNode.ScopeLevel.TENANT,
        scope_id=tenant_id,
        config_json={"auto_print": True},
    )
    assert node.scope_level == "TENANT"

    rev = DynamicConfigRevision.objects.create(
        node=node,
        author_id=new_uuid7(),
        change_summary="Enable auto print for barista station",
        patch_json={"auto_print": False},
    )
    assert rev.status == DynamicConfigRevision.RevisionStatus.DRAFT
    assert len(rev.etag) == 16

    sim = ConfigSimulationRun.objects.create(
        revision=rev,
        result_status=ConfigSimulationRun.ResultStatus.PASSED,
        impact_forecast_json={"affected_terminals": 2},
    )
    assert sim.is_safe_to_publish
    print("[PASS] test_config_models_persistence")


def main() -> None:
    test_rfc7396_merge_patch()
    test_6_level_inheritance_and_provenance()
    test_simulation_conflict_detection()
    test_config_models_persistence()
    print("\n>>> All 4 Subphase 01.04 verification suites passed successfully! <<<")


if __name__ == "__main__":
    main()
