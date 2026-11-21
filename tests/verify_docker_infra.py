"""
Automated Verification Suite for Subphase 00.02: Docker Multi-Stage Builds & PgBouncer Infrastructure.
Validates immutable image digest pinning, non-root user execution, Forced RLS database roles, and transaction pooling configs.
"""

import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_INFRA_FILES = [
    "infra/docker/base-pins.env",
    "infra/docker/api.Dockerfile",
    "infra/docker/worker-go.Dockerfile",
    "infra/docker/web.Dockerfile",
    "infra/docker/docker-compose.dev.yml",
    "infra/postgres/01_init_regional_cell.sql",
    "infra/pgbouncer/pgbouncer.ini",
    "infra/pgbouncer/userlist.txt",
]

def test_infra_files_exist():
    print("==> Checking required infrastructure files...")
    for rel_path in REQUIRED_INFRA_FILES:
        full_path = os.path.join(REPO_ROOT, rel_path)
        assert os.path.exists(full_path), f"Missing infrastructure file: {rel_path}"
        print(f"  [OK] {rel_path}")

def test_immutable_digest_pins():
    print("==> Validating immutable sha256 base image pins...")
    pins_file = os.path.join(REPO_ROOT, "infra/docker/base-pins.env")
    with open(pins_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pins = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
    assert len(pins) >= 5, "base-pins.env must define at least 5 base images"

    for pin in pins:
        key, val = pin.split("=", 1)
        assert "@sha256:" in val, f"Floating tag detected in {key}: {val}. Mandatory @sha256: pin missing!"
        print(f"  [OK] {key} securely pinned with digest")

def test_dockerfile_security_invariants():
    print("==> Validating Dockerfile security invariants (non-root, multi-stage)...")
    dockerfiles = {
        "infra/docker/api.Dockerfile": {"expected_user": "USER 10001:10001", "stages": ["builder", "runner"]},
        "infra/docker/worker-go.Dockerfile": {"expected_user": "USER 65532:65532", "stages": ["builder", "runner"]},
        "infra/docker/web.Dockerfile": {"expected_user": "USER 10001:10001", "stages": ["builder", "runner"]},
    }

    for df_path, rules in dockerfiles.items():
        full_path = os.path.join(REPO_ROOT, df_path)
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check multi-stage
        for stage in rules["stages"]:
            pattern = rf"FROM\s+.*?\s+AS\s+{stage}"
            assert re.search(pattern, content, re.IGNORECASE), f"{df_path} missing multi-stage '{stage}'"

        # Check non-root
        assert rules["expected_user"] in content, f"{df_path} missing non-root directive {rules['expected_user']}"
        print(f"  [OK] {df_path} passes non-root & multi-stage assertions")

def test_pgbouncer_configuration():
    print("==> Validating PgBouncer transaction pooling & parameter passthrough...")
    ini_path = os.path.join(REPO_ROOT, "infra/pgbouncer/pgbouncer.ini")
    with open(ini_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "pool_mode = transaction" in content, "PgBouncer MUST use pool_mode = transaction"
    assert "server_reset_query = DISCARD ALL" in content, "PgBouncer MUST reset queries with DISCARD ALL"
    assert "app.current_tenant_id" in content, "PgBouncer MUST pass track_extra_parameters for app.current_tenant_id"
    print("  [OK] PgBouncer transaction pooling & RLS parameters verified")

def test_postgres_init_sql():
    print("==> Validating PostgreSQL 16 regional init scripts...")
    sql_path = os.path.join(REPO_ROOT, "infra/postgres/01_init_regional_cell.sql")
    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()

    for ext in ["uuid-ossp", "btree_gist", "pgcrypto"]:
        assert ext in sql, f"PostgreSQL init missing mandatory extension: {ext}"

    assert "nexus_app_rw" in sql, "PostgreSQL init missing nexus_app_rw role"
    assert "NOBYPASSRLS" in sql, "nexus_app_rw role MUST strictly enforce NOBYPASSRLS"
    print("  [OK] PostgreSQL 16 extensions and NOBYPASSRLS role verified")

def run_all():
    print("\n--- Running Subphase 00.02 Verification Suite ---")
    test_infra_files_exist()
    test_immutable_digest_pins()
    test_dockerfile_security_invariants()
    test_pgbouncer_configuration()
    test_postgres_init_sql()
    print("--- Subphase 00.02 Verification Suite PASSED (100% assertions) ---\n")

if __name__ == "__main__":
    try:
        run_all()
    except AssertionError as e:
        print(f"\n[FAIL] Assertion error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
