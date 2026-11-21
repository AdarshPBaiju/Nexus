#!/usr/bin/env python3
"""
verify_ci_governance.py - Verification suite for Subphase 00.03.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _verify_linters(repo_root: Path) -> None:
    linter_cfg = repo_root / "services" / "nexus-api" / ".importlinter"
    assert linter_cfg.exists(), ".importlinter must exist"
    content = linter_cfg.read_text(encoding="utf-8")
    assert "Layered Architecture Contract" in content, "Layer contract missing"
    assert "Extension Independence Contract" in content, "Independence contract missing"

    pyproject = repo_root / "services" / "nexus-api" / "pyproject.toml"
    assert pyproject.exists(), "pyproject.toml must exist"
    pyproject_text = pyproject.read_text(encoding="utf-8")
    assert "[tool.ruff]" in pyproject_text, "Ruff configuration missing"
    assert "max-complexity = 10" in pyproject_text, "McCabe complexity missing"
    print("  [PASS] .importlinter and Ruff configs verified")


def _verify_audits(repo_root: Path) -> None:
    budget_audit = repo_root / "ops" / "audits" / "audit_code_budget.py"
    res = subprocess.run([sys.executable, str(budget_audit)], capture_output=True, text=True)
    assert res.returncode == 0, f"audit_code_budget.py failed: {res.stdout}\n{res.stderr}"

    rls_audit = repo_root / "ops" / "audits" / "audit_rls_coverage.py"
    res = subprocess.run([sys.executable, str(rls_audit)], capture_output=True, text=True)
    assert res.returncode == 0, f"audit_rls_coverage.py failed: {res.stdout}\n{res.stderr}"
    print("  [PASS] Code budget and RLS coverage audits passed")


def _verify_branches(repo_root: Path) -> None:
    branch_check = repo_root / "ops" / "ci" / "branch_check.py"
    valid = ["development", "feat/ci-governance-linters", "test/ci-linters"]
    for b in valid:
        r = subprocess.run([sys.executable, str(branch_check), b], capture_output=True, text=True)
        assert r.returncode == 0, f"Branch '{b}' should pass: {r.stderr}"

    invalid = ["phase-0", "FEAT/UPPER", "feat_underscore", "temp"]
    for b in invalid:
        r = subprocess.run([sys.executable, str(branch_check), b], capture_output=True, text=True)
        assert r.returncode != 0, f"Branch '{b}' should fail"
    print("  [PASS] Branch naming taxonomy assertions passed")


def _verify_workflows(repo_root: Path) -> None:
    expected = [
        "ci-api-rls-and-boundaries.yml",
        "ci-worker-go.yml",
        "ci-web-and-contracts.yml",
        "ci-desktop-release.yml",
        "ci-branch-governance.yml",
    ]
    wf_dir = repo_root / ".github" / "workflows"
    for wf in expected:
        assert (wf_dir / wf).exists(), f"Workflow {wf} must exist"

    root_eslint = repo_root / ".eslintrc.js"
    assert root_eslint.exists(), "Root eslint config must exist"
    golangci_cfg = repo_root / "services" / "nexus-worker-go" / ".golangci.yml"
    assert golangci_cfg.exists(), ".golangci.yml must exist"
    print(f"  [PASS] All {len(expected)} workflows and linters verified")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    print(f"==> Verifying Subphase 00.03 CI Governance in {repo_root}...")
    _verify_linters(repo_root)
    _verify_audits(repo_root)
    _verify_branches(repo_root)
    _verify_workflows(repo_root)
    print("\n==> Subphase 00.03 Verification Suite PASSED (100% assertions satisfied).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
