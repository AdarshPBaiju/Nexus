"""
Automated Verification Suite for Subphase 00.01: Monorepo Toolchain & Workspace Orchestration.
Validates polyglot configuration syntax, workspace member existence, and orchestrator commands.
"""

import os
import json
import subprocess
import sys

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # fallback

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_FILES = [
    "pnpm-workspace.yaml",
    "package.json",
    "turbo.json",
    "pyproject.toml",
    "go.work",
    "Cargo.toml",
    "Makefile",
    "nexus.ps1",
]


def test_required_files_exist():
    print("==> Checking required configuration files...")
    for rel_path in REQUIRED_FILES:
        full_path = os.path.join(REPO_ROOT, rel_path)
        assert os.path.exists(full_path), f"Missing required file: {rel_path}"
        print(f"  [OK] {rel_path}")


def test_json_configs():
    print("==> Validating JSON configuration schemas...")
    for json_file in ["package.json", "turbo.json"]:
        path = os.path.join(REPO_ROOT, json_file)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict), f"{json_file} must parse into a JSON object"
        print(f"  [OK] {json_file} syntax valid")


def test_toml_configs():
    print("==> Validating TOML workspace configs...")
    for toml_file in ["pyproject.toml", "Cargo.toml"]:
        path = os.path.join(REPO_ROOT, toml_file)
        with open(path, "rb") as f:
            data = tomllib.load(f)
        assert isinstance(data, dict), f"{toml_file} must parse into a TOML dictionary"
        print(f"  [OK] {toml_file} syntax valid")


def test_workspace_members():
    print("==> Validating workspace members...")
    expected_members = [
        "services/nexus-api/pyproject.toml",
        "services/nexus-worker-go/go.mod",
        "clients/desktop/src-tauri/Cargo.toml",
        "packages/rust-crypto/Cargo.toml",
        "packages/contracts/package.json",
        "packages/ui/package.json",
        "clients/web/package.json",
    ]
    for m in expected_members:
        full_path = os.path.join(REPO_ROOT, m)
        assert os.path.exists(full_path), f"Workspace member missing: {m}"
        print(f"  [OK] Member exists: {m}")


def test_nexus_ps1_orchestrator():
    print("==> Validating nexus.ps1 orchestrator execution...")
    ps1_path = os.path.join(REPO_ROOT, "nexus.ps1")
    res = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps1_path, "help"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"nexus.ps1 help failed with code {res.returncode}: {res.stderr}"
    assert "Project Nexus Windows Orchestrator" in res.stdout
    print("  [OK] nexus.ps1 help command exits 0 and renders help text")


def run_all():
    print("\n--- Running Subphase 00.01 Verification Suite ---")
    test_required_files_exist()
    test_json_configs()
    test_toml_configs()
    test_workspace_members()
    test_nexus_ps1_orchestrator()
    print("--- Subphase 00.01 Verification Suite PASSED (100% assertions) ---\n")


if __name__ == "__main__":
    try:
        run_all()
    except AssertionError as e:
        print(f"\n[FAIL] Assertion error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
