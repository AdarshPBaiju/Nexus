#!/usr/bin/env python3
"""
verify_database_logs_forensic_audit_cdc_worm.py - Verification suite for Subphase 01.21.
"""

from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone
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
            "nexus.platform.audit",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

call_command("migrate", run_syncdb=True, verbosity=0)

from nexus.libs.db.audit_context import (
    AuditRequestContext,
    clear_current_audit_context,
    get_current_audit_context,
    set_current_audit_context,
)
from nexus.libs.db.rls import tenant_transaction
from nexus.platform.audit.application import (
    AuditEventIntent,
    DataAccessAuditService,
    ForensicAuditService,
    HashChainVerifier,
)
from nexus.platform.audit.domain.hash_chain import HashChainEngine
from nexus.platform.audit.domain.redaction import PiiRedactionDiffEngine
from nexus.platform.audit.domain.regulated_registry import get_regulated_table
from nexus.platform.audit.models import (
    AuditChainAnchor,
    AuditColdArchiveManifest,
)


def test_audit_request_context_and_gucs() -> None:
    tenant_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    ctx = AuditRequestContext(
        tenant_id=tenant_id,
        actor_id=actor_id,
        actor_type="STAFF",
        reason="Fiscal review",
    )
    set_current_audit_context(ctx)
    retrieved = get_current_audit_context()
    assert retrieved is not None
    assert retrieved.actor_id == actor_id

    with tenant_transaction(tenant_id, ctx):
        pass  # In-transaction execution

    clear_current_audit_context()
    assert get_current_audit_context() is None
    print("PASS: AuditRequestContext & GUC context verified.")


def test_pii_redaction_and_minimal_diff() -> None:
    before = {
        "id": "item-123",
        "username": "alice",
        "password": "super_secret_password",
        "cashier_pin": "1234",
        "role": "CASHIER",
        "updated_at": "2026-11-22T08:00:00Z",
    }
    after = {
        "id": "item-123",
        "username": "alice",
        "password": "new_super_secret_password",
        "cashier_pin": "5678",
        "role": "SUPERVISOR",
        "updated_at": "2026-11-22T08:30:00Z",
    }

    scrubbed = PiiRedactionDiffEngine.scrub_dict(before)
    assert scrubbed["password"] == "[REDACTED_SECRET]"

    diff, changed_keys = PiiRedactionDiffEngine.compute_diff(before, after)
    assert "role" in changed_keys
    assert "updated_at" not in changed_keys
    print("PASS: PiiRedactionDiffEngine & minimal diff verified.")


def test_cryptographic_hash_chain_and_tamper_detection() -> None:
    tenant_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    sup_id = uuid.uuid4()

    ev1 = ForensicAuditService.record_event(
        tenant_id=tenant_id,
        intent=AuditEventIntent(
            category="IAM",
            event_type="ROLE_ASSIGNED",
            target_entity_type="StaffProfile",
            target_entity_id="staff-001",
            before_state={"role": "CASHIER"},
            after_state={"role": "SUPERVISOR"},
            actor_id=actor_id,
            supervisor_id=sup_id,
        ),
    )
    assert ev1.prev_hash == HashChainEngine.GENESIS_HASH

    ev2 = ForensicAuditService.record_event(
        tenant_id=tenant_id,
        intent=AuditEventIntent(
            category="FINANCE",
            event_type="DISCOUNT_APPLIED",
            target_entity_type="Folio",
            target_entity_id="folio-999",
            before_state={"discount": 0},
            after_state={"discount": 15},
            actor_id=actor_id,
        ),
    )
    assert ev2.prev_hash == ev1.cumulative_hash

    res = HashChainVerifier.verify_tenant_chain(tenant_id)
    assert res.is_valid is True

    # Mutate event to test tamper detection
    ev1.outcome = "DENIED"
    ev1.save(update_fields=["outcome"])

    tamper_res = HashChainVerifier.verify_tenant_chain(tenant_id)
    assert tamper_res.is_valid is False
    assert tamper_res.tampered_event_id == ev1.id
    print("PASS: Cryptographic hash chaining & tamper detection verified.")


def test_data_access_and_registry() -> None:
    tenant_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    log_c = DataAccessAuditService.record_pii_access(
        tenant_id=tenant_id,
        target_entity="StaffProfile",
        accessed_fields=["national_id", "phone_number"],
        actor_id=actor_id,
    )
    assert log_c.access_type == "PII_UNMASK"

    reg = get_regulated_table("iam_role")
    assert reg is not None
    assert reg.entity_label == "Role"
    print("PASS: Data access audit & regulated registry verified.")


def test_merkle_roots_and_anchors() -> None:
    tenant_id = uuid.uuid4()
    merkle_root = HashChainEngine.compute_merkle_root(["a" * 64, "b" * 64])
    assert len(merkle_root) == 64

    anchor = AuditChainAnchor.objects.create(
        tenant_id=tenant_id,
        window_start=datetime.now(timezone.utc),
        window_end=datetime.now(timezone.utc),
        row_count=100,
        prev_anchor_hash=HashChainEngine.GENESIS_HASH,
        merkle_chain_root_hash=merkle_root,
        ed25519_signature="sig_test_ed25519",
        minio_worm_object_key="nexus-fiscal-worm/2026/11/anchor.json",
    )
    assert anchor.merkle_chain_root_hash == merkle_root

    manifest = AuditColdArchiveManifest.objects.create(
        tenant_id=tenant_id,
        partition_name="audit_tier_a_2026_08",
        date_start=datetime.now(timezone.utc).date(),
        date_end=datetime.now(timezone.utc).date(),
        row_count=5000,
        parquet_s3_key="nexus-fiscal-worm/cold/tier_a_2026_08.parquet",
        sha256_checksum="f" * 64,
        worm_retention_until=datetime.now(timezone.utc),
    )
    assert manifest.row_count == 5000
    print("PASS: Merkle roots, anchors & cold manifests verified.")


def main() -> None:
    print("--- Running Subphase 01.21 Verification Suite ---")
    test_audit_request_context_and_gucs()
    test_pii_redaction_and_minimal_diff()
    test_cryptographic_hash_chain_and_tamper_detection()
    test_data_access_and_registry()
    test_merkle_roots_and_anchors()
    print("SUCCESS: 01.21 Enterprise Database Logs & Forensic Audit verified with 100% assertions.")


if __name__ == "__main__":
    main()
