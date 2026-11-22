#!/usr/bin/env python3
"""
verify_view_field_control_strict_projection.py - Verification suite for Subphase 01.24.
"""
from __future__ import annotations

import os
import sys
import time
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
        ],
        USE_TZ=True,
    )
    django.setup()

from nexus.libs.field_control import (
    FieldPlanCompiler,
    FlsProjectionBridge,
    ViewFieldContract,
)


def test_view_field_contract_and_joins() -> None:
    contract = ViewFieldContract(
        model_label="OrderFolio",
        allowed_fields=("folio_number", "total_amount", "customer_name", "status"),
        field_dependencies={
            "total_amount": ("subtotal", "tax_amount", "discount_amount"),
        },
        relation_paths={
            "customer_name": "customer",
        },
    )

    # 1. Ask for folio_number and status (no relations, no dependencies)
    cols1 = contract.resolve_sql_columns(["folio_number", "status"])
    joins1 = contract.resolve_relations(["folio_number", "status"])
    assert "folio_number" in cols1
    assert "status" in cols1
    assert "id" in cols1 and "tenant_id" in cols1
    assert len(joins1) == 0  # Zero unused JOINs!

    # 2. Ask for customer_name and total_amount
    cols2 = contract.resolve_sql_columns(["customer_name", "total_amount"])
    joins2 = contract.resolve_relations(["customer_name", "total_amount"])
    assert "subtotal" in cols2 and "tax_amount" in cols2 and "discount_amount" in cols2
    assert "customer" in joins2  # Only asked relation joined!
    print("PASS: ViewFieldContract dependencies and zero unused joins verified.")


def test_plan_compiler_and_latency() -> None:
    contract = ViewFieldContract(
        model_label="Branch",
        allowed_fields=("name", "code", "city", "phone"),
        relation_paths={"city": "address__city"},
    )
    compiler = FieldPlanCompiler(contract)

    # Warm compile
    plan1 = compiler.compile(["name", "code"])
    assert "name" in plan1.sql_columns
    assert "code" in plan1.sql_columns
    assert len(plan1.relations) == 0

    # Cached compile latency benchmark
    start = time.perf_counter()
    for _ in range(1000):
        _ = compiler.compile(["name", "code"])
    elapsed_ms = (time.perf_counter() - start) * 1000 / 1000
    assert elapsed_ms < 0.15  # Sub-0.15ms resolution SLA
    print(f"PASS: FieldPlanCompiler cached resolution latency {elapsed_ms:.4f} ms verified.")


def test_fls_projection_bridge() -> None:
    requested = ["code", "account_number", "salary_rate", "secret_key"]
    fls_rules = {
        "code": "READ",
        "account_number": "MASKED",
        "secret_key": "HIDDEN",
    }

    eval_result = FlsProjectionBridge.evaluate_permissions(requested, fls_rules)
    assert "code" in eval_result.visible_fields
    assert "salary_rate" in eval_result.visible_fields  # Default READ
    assert "account_number" in eval_result.masked_fields
    assert "secret_key" not in eval_result.visible_fields
    assert "secret_key" not in eval_result.masked_fields  # Completely pruned!

    # Masking
    masked_dict = FlsProjectionBridge.mask_representation(
        {"code": "BR-01", "account_number": "123456789012"},
        eval_result.masked_fields,
    )
    assert masked_dict["account_number"] == "**** 9012"
    assert masked_dict["code"] == "BR-01"
    print("PASS: FlsProjectionBridge FLS intersection & masking verified.")


def main() -> None:
    print("--- Running Subphase 01.24 Verification Suite ---")
    test_view_field_contract_and_joins()
    test_plan_compiler_and_latency()
    test_fls_projection_bridge()
    print("SUCCESS: 01.24 View Field Control & Strict Projection verified with 100% assertions.")


if __name__ == "__main__":
    main()
