#!/usr/bin/env python3
"""
verify_export_advanced_dynamic_data_mapping.py - Verification suite for Subphase 01.25.
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

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
            "nexus.engines.data_exchange",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

call_command("migrate", run_syncdb=True, verbosity=0)

from nexus.engines.data_exchange import (
    CsvFormulaSanitizer,
    DataSchemaMapper,
    DualLaneExportCoordinator,
    SafeAstCaseEvaluator,
)
from nexus.engines.data_exchange.models import DataMappingProfile


def test_data_mapping_profile_model() -> None:
    tenant_id = uuid.uuid4()
    profile = DataMappingProfile.objects.create(
        tenant_id=tenant_id,
        name="Legacy POS Menu Importer",
        source_format="CSV",
        target_entity="MenuItem",
        field_mappings={"old_sku": "sku", "old_title": "name", "old_cat": "category"},
        ast_rules={
            "category": {
                "rules": [
                    {"operator": "eq", "operand": "HOT_COFFEE", "target": "Hot Beverages"},
                    {"operator": "eq", "operand": "COLD_BREW", "target": "Cold Beverages"},
                ],
                "default": "General",
            }
        },
    )
    assert profile.name == "Legacy POS Menu Importer"
    assert profile.target_entity == "MenuItem"
    print("PASS: DataMappingProfile model and schema definition verified.")


def test_safe_ast_case_evaluator() -> None:
    rules = [
        {"operator": "eq", "operand": "BEV", "target": "Beverage"},
        {"operator": "eq", "operand": "SNK", "target": "Snacks"},
    ]
    assert SafeAstCaseEvaluator.evaluate("BEV", rules, default_value="Other") == "Beverage"
    assert SafeAstCaseEvaluator.evaluate("UNKNOWN", rules, default_value="Other") == "Other"
    print("PASS: SafeAstCaseEvaluator sandboxed evaluation verified.")


def test_schema_mapper_transformation() -> None:
    raw_row = {
        "old_sku": "SKU-9901",
        "old_title": "Caramel Macchiato",
        "old_cat": "HOT_COFFEE",
        "unmapped_extra": "discard",
    }
    mappings = {"old_sku": "sku", "old_title": "name", "old_cat": "category"}
    ast_rules = {
        "category": {
            "rules": [
                {"operator": "eq", "operand": "HOT_COFFEE", "target": "Hot Beverages"},
            ],
            "default": "Food",
        }
    }

    transformed = DataSchemaMapper.transform_row(raw_row, mappings, ast_rules)
    assert transformed["sku"] == "SKU-9901"
    assert transformed["name"] == "Caramel Macchiato"
    assert transformed["category"] == "Hot Beverages"
    assert "unmapped_extra" not in transformed
    print("PASS: DataSchemaMapper dynamic transformation verified.")


def test_csv_formula_sanitizer() -> None:
    dangerous_payloads = [
        "=cmd|' /C calc'!A0",
        "+12345",
        "-67890",
        "@SUM(A1:A10)",
        "|dangerous_pipe",
        "%exploit",
    ]
    for payload in dangerous_payloads:
        sanitized = CsvFormulaSanitizer.sanitize_value(payload)
        assert sanitized.startswith("'"), f"Failed to escape {payload}"

    safe_val = "Regular Item Name"
    assert CsvFormulaSanitizer.sanitize_value(safe_val) == "Regular Item Name"
    print("PASS: CsvFormulaSanitizer injection prevention verified.")


def test_dual_lane_export_coordinator() -> None:
    # 1. Sync lane (<= 1,000 rows)
    small_batch = [{"id": i, "name": f"Item {i}"} for i in range(10)]
    res_sync = DualLaneExportCoordinator.dispatch_export(small_batch, columns=["id", "name"])
    assert res_sync.lane == "SYNC"
    assert "Item 0" in res_sync.payload_or_job_id

    # 2. Heavy async lane (> 1,000 rows)
    large_batch = [{"id": i, "name": f"Item {i}"} for i in range(1001)]
    res_async = DualLaneExportCoordinator.dispatch_export(large_batch, columns=["id", "name"])
    assert res_async.lane == "ASYNC_GO"
    assert str(res_async.payload_or_job_id).startswith("job_export_go_")
    print("PASS: DualLaneExportCoordinator routing verified.")


def main() -> None:
    print("--- Running Subphase 01.25 Verification Suite ---")
    test_data_mapping_profile_model()
    test_safe_ast_case_evaluator()
    test_schema_mapper_transformation()
    test_csv_formula_sanitizer()
    test_dual_lane_export_coordinator()
    print("SUCCESS: 01.25 Export & Dynamic Data Mapping verified with 100% assertions.")


if __name__ == "__main__":
    main()
