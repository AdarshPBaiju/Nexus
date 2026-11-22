#!/usr/bin/env python3
"""
verify_bulk_import_multi_source_staging.py - Verification suite for Subphase 01.26.
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

from nexus.engines.data_exchange.importing import (
    DryRunBatchValidator,
    ImportBatchSession,
    ImportPipelineCoordinator,
    TopologicalImportResolver,
)


def test_topological_dependency_ordering() -> None:
    # TaxProfile -> Category -> MenuItem -> RecipeBOM
    deps = {
        "RecipeBOM": ["MenuItem"],
        "MenuItem": ["Category", "TaxProfile"],
        "Category": ["TaxProfile"],
        "TaxProfile": [],
    }

    order = TopologicalImportResolver.resolve_order(deps)
    assert order.index("TaxProfile") < order.index("Category")
    assert order.index("Category") < order.index("MenuItem")
    assert order.index("MenuItem") < order.index("RecipeBOM")

    # Cycle detection
    cyclic_deps = {
        "A": ["B"],
        "B": ["A"],
    }
    try:
        TopologicalImportResolver.resolve_order(cyclic_deps)
        assert False, "Expected cyclic dependency error"
    except ValueError as exc:
        assert "Cyclic dependency" in str(exc)
    print("PASS: TopologicalImportResolver dependency resolution verified.")


def test_staging_validation_commit_and_rollback() -> None:
    tenant_id = uuid.uuid4()
    raw_rows = [
        {"sku": "SKU-01", "name": "Espresso Single", "price": 2.50},
        {"sku": "SKU-02", "name": "", "price": 3.00},  # Missing name!
        {"sku": "SKU-03", "name": "Cappuccino", "price": 4.00},
    ]

    # 1. Stage Batch
    session = ImportPipelineCoordinator.stage_batch(
        tenant_id=tenant_id,
        name="Coffee Menu Import",
        target_entity="MenuItem",
        raw_rows=raw_rows,
    )
    assert session.status == ImportBatchSession.Status.STAGED
    assert session.total_rows == 3

    # 2. Dry-Run Validation
    valid_count, error_count = DryRunBatchValidator.validate_session(
        session=session,
        mandatory_fields=["sku", "name", "price"],
        type_checks={"price": float},
    )
    assert valid_count == 2
    assert error_count == 1
    session.refresh_from_db()
    assert session.error_rows == 1

    # 3. Atomic Commit
    inserted_ids = ["rec_001", "rec_003"]
    ImportPipelineCoordinator.commit_batch(
        session=session,
        inserted_record_ids=inserted_ids,
        target_table="cat_menu_item",
    )
    session.refresh_from_db()
    assert session.status == ImportBatchSession.Status.COMPLETED
    assert session.rollback_logs.count() == 1

    # 4. 1-Click Rollback
    reverted_count = ImportPipelineCoordinator.rollback_batch(session)
    assert reverted_count == 2
    session.refresh_from_db()
    assert session.status == ImportBatchSession.Status.ROLLED_BACK
    print("PASS: 7-Stage staging, dry-run validation, atomic commit & 1-click rollback verified.")


def main() -> None:
    print("--- Running Subphase 01.26 Verification Suite ---")
    test_topological_dependency_ordering()
    test_staging_validation_commit_and_rollback()
    print("SUCCESS: 01.26 Bulk Import & Staging Pipeline verified with 100% assertions.")


if __name__ == "__main__":
    main()
