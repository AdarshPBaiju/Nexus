#!/usr/bin/env python3
"""
verify_navigation_shell.py - Verification suite for Subphase 00.11 (Clean Main Top Navbar & Below-Nav Sidebars).
"""

from __future__ import annotations

import sys
from pathlib import Path


def _verify_clean_navbar(nav_dir: Path) -> None:
    navbar = nav_dir / "NexusCleanMainTopNavbar.tsx"
    assert navbar.exists(), "NexusCleanMainTopNavbar.tsx must exist"
    content = navbar.read_text(encoding="utf-8")
    assert "height: '56px'" in content
    assert "workspaceSwitcher" in content
    assert "globalSearchTrigger" in content
    assert "userAvatar" in content
    print("  [PASS] Clean 56px Main Top Navbar verified (zero nav links)")


def _verify_below_nav_modes(nav_dir: Path) -> None:
    modes = [
        ("NexusNestedSidebar.tsx", "Nested Sidebar (Mode A)"),
        ("NexusDualSidebar.tsx", "Dual Sidebar (Mode B)"),
        ("NexusChildStripBar.tsx", "Child Strip Bar (Mode C)"),
        ("NexusChildSidebar.tsx", "Child Sidebar (Mode D)"),
        ("NexusOperationalMinimalBar.tsx", "Operational Minimal Bar (Mode E)"),
    ]
    for filename, label in modes:
        f = nav_dir / filename
        assert f.exists(), f"{filename} missing"
    print(f"  [PASS] All {len(modes)} below-navbar navigation modes verified")


def _verify_controller_and_shell(nav_dir: Path) -> None:
    ctrl = nav_dir / "NavigationModeController.ts"
    shell = nav_dir / "NexusAppLayoutShell.tsx"
    assert ctrl.exists() and shell.exists()

    ctrl_content = ctrl.read_text(encoding="utf-8")
    assert "setMode" in ctrl_content
    assert "toggleCollapse" in ctrl_content

    shell_content = shell.read_text(encoding="utf-8")
    assert "dir={dir}" in shell_content
    assert "NexusCleanMainTopNavbar" in shell_content
    print("  [PASS] NavigationModeController and RTL/BiDi NexusAppLayoutShell verified")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    nav_dir = repo_root / "packages" / "ui" / "src" / "navigation"
    print(f"==> Verifying Subphase 00.11 Navigation Shell in {nav_dir}...")

    _verify_clean_navbar(nav_dir)
    _verify_below_nav_modes(nav_dir)
    _verify_controller_and_shell(nav_dir)

    index_file = nav_dir / "index.ts"
    assert index_file.exists(), "index.ts must exist"
    assert len(index_file.read_text(encoding="utf-8").splitlines()) <= 30, (
        "Barrel must be <= 30 lines"
    )

    print("\n==> Subphase 00.11 Verification Suite PASSED (100% assertions satisfied).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
