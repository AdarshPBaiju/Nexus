#!/usr/bin/env python3
"""
verify_make_bake_infra.py - Verification suite for Subphase 00.10 (Modular Makefile, PS1 & BuildKit Bake).
"""

from __future__ import annotations

import sys
from pathlib import Path


def _verify_modular_mk(repo_root: Path) -> None:
    mk_dir = repo_root / "mk"
    expected = [
        "00-config.mk",
        "10-docker.mk",
        "20-database.mk",
        "40-workers.mk",
        "50-dev.mk",
        "60-quality.mk",
        "70-test.mk",
    ]
    for mk in expected:
        f = mk_dir / mk
        assert f.exists(), f"Modular makefile {mk} must exist in mk/"

    root_makefile = repo_root / "Makefile"
    assert root_makefile.exists(), "Root Makefile must exist"
    content = root_makefile.read_text(encoding="utf-8")
    for mk in expected:
        assert f"include mk/{mk}" in content, f"Makefile must include mk/{mk}"
    print(f"  [PASS] All {len(expected)} modular makefiles and inclusions verified")


def _verify_docker_bake(repo_root: Path) -> None:
    bake_file = repo_root / "infra" / "docker" / "docker-bake.hcl"
    assert bake_file.exists(), "docker-bake.hcl must exist"
    content = bake_file.read_text(encoding="utf-8")
    assert 'targets = ["api", "worker-go", "web"]' in content
    assert 'target "api"' in content
    assert 'target "worker-go"' in content
    assert 'target "web"' in content
    print("  [PASS] Docker Buildx Bake targets and group verified")


def _verify_windows_ps1(repo_root: Path) -> None:
    ps1_file = repo_root / "nexus.ps1"
    assert ps1_file.exists(), "nexus.ps1 must exist"
    content = ps1_file.read_text(encoding="utf-8")
    assert "audit-rls" in content
    assert "audit-budget" in content
    assert "branch-check" in content
    print("  [PASS] Windows PowerShell orchestrator verified")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    print(f"==> Verifying Subphase 00.10 Make, PS1 & Bake Infrastructure in {repo_root}...")

    _verify_modular_mk(repo_root)
    _verify_docker_bake(repo_root)
    _verify_windows_ps1(repo_root)

    print("\n==> Subphase 00.10 Verification Suite PASSED (100% assertions satisfied).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
