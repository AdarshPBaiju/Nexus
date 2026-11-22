#!/usr/bin/env python3
"""
verify_multi_tenant_regional_rls.py - Verification suite for Subphase 01.01.
Validates:
1. Base Domain Models (TenantScopedModel, VersionedAggregateModel, SoftArchivableModel, EffectiveDatedModel).
2. Multi-tier Tenancy Hierarchy (Tenant, LegalEntity, Brand, Branch, PhysicalZone).
3. PostgreSQL 16 Forced RLS SQL Generator & Isolation Invariants.
4. Tenant Envelope Cipher (AES-256-GCM + AAD Binding) with tamper & transplant rejection.
5. Blind Index Hasher (HMAC-SHA256 + NFKC normalization).
6. Go Worker RLS context parity.
"""
from __future__ import annotations

import datetime
import os
import sys
import uuid
from pathlib import Path

# Add nexus-api src to sys.path first
REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "services" / "nexus-api" / "src"
sys.path.insert(0, str(API_SRC))

# Setup Django minimal settings for standalone model checks
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
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.exceptions import ValidationError

from nexus.libs.db.rls import generate_drop_rls_sql, generate_forced_rls_sql
from nexus.libs.ids import new_uuid7
from nexus.libs.models import (
    EffectiveDatedModel,
    SoftArchivableModel,
    TenantScopedModel,
    VersionedAggregateModel,
)
from nexus.libs.security import (
    BlindIndexHasher,
    CipherContext,
    CryptographicIntegrityError,
    TenantEnvelopeCipher,
    TenantKmsKeyService,
)
from nexus.platform.tenancy.models import (
    Branch,
    Brand,
    LegalEntity,
    PhysicalZone,
    Tenant,
)


def _verify_uuid7() -> None:
    u1 = new_uuid7()
    u2 = new_uuid7()
    assert u1.version == 7, f"UUID version must be 7, got {u1.version}"
    assert u2.version == 7, f"UUID version must be 7, got {u2.version}"
    assert u1 != u2, "Consecutive UUIDv7 tokens must be distinct"
    print("  [PASS] RFC 9562 UUIDv7 generator verified")


def _verify_tenant_and_versioned() -> None:
    tenant_id = new_uuid7()
    entity = LegalEntity(
        tenant_id=tenant_id,
        legal_name="Acme Corp",
        tax_id="TAX-01",
        jurisdiction_code="US-DE",
        functional_currency="USD",
    )
    entity.clean()

    # Reject null tenant_id
    invalid_entity = LegalEntity(tenant_id=None, legal_name="Bad Corp", tax_id="TAX-02")
    try:
        invalid_entity.clean()
        assert False, "Should reject null tenant_id"
    except ValidationError:
        pass

    class ConcreteVersioned(VersionedAggregateModel):
        class Meta:
            app_label = "test_app"

    v_instance = ConcreteVersioned()
    assert v_instance.version == 1
    v_instance.verify_version(1)
    new_v = v_instance.increment_version()
    assert new_v == 2
    try:
        v_instance.verify_version(1)
        assert False, "Should raise ValidationError on version mismatch"
    except ValidationError:
        pass


def _verify_archivable_and_effective() -> None:
    class ConcreteArchivable(SoftArchivableModel):
        class Meta:
            app_label = "test_app"

    a_instance = ConcreteArchivable()
    assert not a_instance.is_archived
    actor = new_uuid7()
    a_instance.archive(actor)
    assert a_instance.is_archived
    assert a_instance.archived_by_id == actor
    assert a_instance.archived_at is not None
    a_instance.restore()
    assert not a_instance.is_archived
    assert a_instance.archived_at is None

    class ConcreteEffective(EffectiveDatedModel):
        class Meta:
            app_label = "test_app"

    today = datetime.date.today()
    e_instance = ConcreteEffective(
        valid_from=today - datetime.timedelta(days=1),
        valid_until=today + datetime.timedelta(days=1),
    )
    assert e_instance.is_effective(today)
    assert not e_instance.is_effective(today - datetime.timedelta(days=2))
    assert not e_instance.is_effective(today + datetime.timedelta(days=2))


def _verify_base_models() -> None:
    _verify_tenant_and_versioned()
    _verify_archivable_and_effective()
    print("  [PASS] Base domain models (TenantScoped, Versioned, Archivable, EffectiveDated) verified")


def _verify_tenancy_hierarchy() -> None:
    t = Tenant(slug="acme-corp", legal_name="Acme Global Inc", status=Tenant.Status.ACTIVE, home_region="ap-south-1")
    t.clean()
    assert t.is_operational

    bad_t = Tenant(slug="Acme_Corp!", legal_name="Bad Slug")
    try:
        bad_t.clean()
        assert False, "Should reject invalid uppercase/special character slug"
    except ValidationError:
        pass

    t_id = new_uuid7()
    le = LegalEntity(tenant_id=t_id, legal_name="Acme Ltd", tax_id="GST-1234", jurisdiction_code="IN-KA", functional_currency="INR")
    le.clean()

    brand = Brand(tenant_id=t_id, name="Nexus Café", slug="nexus-cafe")
    brand.clean()

    other_t_id = new_uuid7()
    other_le = LegalEntity(tenant_id=other_t_id, legal_name="Other Corp", tax_id="TAX-99")
    branch_cross = Branch(tenant_id=t_id, legal_entity=other_le, brand=brand, name="Indiranagar Branch", code="BLR-01")
    try:
        branch_cross.clean()
        assert False, "Should reject branch with mismatched legal_entity tenant"
    except ValidationError:
        pass

    branch_valid = Branch(tenant_id=t_id, legal_entity=le, brand=brand, name="Indiranagar Branch", code="BLR-01")
    zone_cross = PhysicalZone(tenant_id=other_t_id, branch=branch_valid, name="Counter 1", zone_type=PhysicalZone.ZoneType.COUNTER)
    try:
        zone_cross.clean()
        assert False, "Should reject zone with mismatched branch tenant"
    except ValidationError:
        pass

    print("  [PASS] Tenancy hierarchy models and cross-tenant guardrails verified")


def _verify_forced_rls_sql() -> None:
    sql_stmts = generate_forced_rls_sql("tenancy_branch")
    joined = "\n".join(sql_stmts)

    assert "ALTER TABLE tenancy_branch ENABLE ROW LEVEL SECURITY;" in joined
    assert "ALTER TABLE tenancy_branch FORCE ROW LEVEL SECURITY;" in joined
    assert "CREATE POLICY tenancy_branch_tenant_isolation_policy" in joined
    assert "app.current_tenant_id" in joined

    drop_stmts = generate_drop_rls_sql("tenancy_branch")
    drop_joined = "\n".join(drop_stmts)
    assert "DISABLE ROW LEVEL SECURITY" in drop_joined
    print("  [PASS] PostgreSQL 16 Forced RLS SQL generators verified")


def _verify_cryptographic_cipher() -> None:
    kms = TenantKmsKeyService(ttl_seconds=60)
    cipher = TenantEnvelopeCipher(kms)

    ctx = CipherContext(
        tenant_id=new_uuid7(),
        entity_label="customer",
        row_id=new_uuid7(),
        field_name="phone_e164",
    )
    secret_phone = "+14155552671"

    # 1. Successful encryption and roundtrip
    envelope = cipher.encrypt(ctx, secret_phone)
    assert envelope.startswith("v1:"), f"Envelope must start with v1: {envelope}"
    decrypted = cipher.decrypt(ctx, envelope)
    assert decrypted == secret_phone, f"Decrypted {decrypted} != {secret_phone}"

    # 2. Tampered ciphertext rejection
    tampered_env = envelope[:-6] + "xxxx=="
    try:
        cipher.decrypt(ctx, tampered_env)
        assert False, "Must fail on tampered ciphertext"
    except CryptographicIntegrityError:
        pass

    # 3. Cross-Tenant transplant rejection
    other_ctx = CipherContext(
        tenant_id=new_uuid7(),
        entity_label=ctx.entity_label,
        row_id=ctx.row_id,
        field_name=ctx.field_name,
    )
    try:
        cipher.decrypt(other_ctx, envelope)
        assert False, "Must fail on cross-tenant transplant attack"
    except CryptographicIntegrityError:
        pass

    print("  [PASS] TenantEnvelopeCipher (AES-256-GCM + AAD) security invariants verified")


def _verify_blind_index() -> None:
    salt = b"test_salt_secret_123"
    v1 = "  John.DOE@example.COM  "
    v2 = "john.doe@example.com"

    h1 = BlindIndexHasher.compute_index(salt, v1)
    h2 = BlindIndexHasher.compute_index(salt, v2)
    assert len(h1) == 16, f"Blind index must be exactly 16 bytes, got {len(h1)}"
    assert h1 == h2, "NFKC-normalization must produce identical blind index for equivalent inputs"

    other_salt = b"different_tenant_salt"
    h3 = BlindIndexHasher.compute_index(other_salt, v1)
    assert h1 != h3, "Different tenant salts must yield different blind index hashes"

    hex_str = BlindIndexHasher.compute_index_hex(salt, v1)
    assert len(hex_str) == 32, "Hex string representation must be 32 characters"
    print("  [PASS] BlindIndexHasher (HMAC-SHA256 + NFKC) determinism and isolation verified")


def _verify_go_worker_parity(repo_root: Path) -> None:
    go_file = repo_root / "services" / "nexus-worker-go" / "pkg" / "db" / "rls.go"
    assert go_file.exists(), f"Go RLS helper missing: {go_file}"
    content = go_file.read_text(encoding="utf-8")
    assert "TenantTransaction" in content, "Go TenantTransaction function missing"
    assert "app.current_tenant_id" in content, "Go session variable app.current_tenant_id missing"
    print("  [PASS] Go worker rls.TenantTransaction parity verified")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    print(f"==> Verifying Subphase 01.01 Multi-Tenant Regional RLS in {repo_root}...")

    _verify_uuid7()
    _verify_base_models()
    _verify_tenancy_hierarchy()
    _verify_forced_rls_sql()
    _verify_cryptographic_cipher()
    _verify_blind_index()
    _verify_go_worker_parity(repo_root)

    print("\n==> Subphase 01.01 Verification Suite PASSED (100% assertions satisfied).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
