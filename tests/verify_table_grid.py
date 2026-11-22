#!/usr/bin/env python3
"""
verify_table_grid.py - Verification suite for Subphase 00.08 (Advanced Data Table & Virtualization Grid).
"""

from __future__ import annotations

import sys
from pathlib import Path


def _verify_controllers(table_dir: Path) -> None:
    base_ctrl = table_dir / "BaseListingController.ts"
    vis_ctrl = table_dir / "ColumnVisibilityController.ts"
    pag_ctrl = table_dir / "TablePaginationController.ts"

    assert base_ctrl.exists() and vis_ctrl.exists() and pag_ctrl.exists()
    content = base_ctrl.read_text(encoding="utf-8")
    assert "class BaseListingController" in content
    assert "DEFAULT_PAGE_SIZE" in content
    assert "visibilityController" in content
    print("  [PASS] BaseListingController, ColumnVisibility, and Pagination controllers verified")


def _verify_components(table_dir: Path) -> None:
    table_comp = table_dir / "NexusAdvancedDataTable.tsx"
    pag_comp = table_dir / "NexusPaginationBar.tsx"

    assert table_comp.exists() and pag_comp.exists()
    table_content = table_comp.read_text(encoding="utf-8")
    assert "function NexusAdvancedDataTable" in table_content
    assert 'role="grid"' in table_content
    print("  [PASS] NexusAdvancedDataTable and NexusPaginationBar components verified")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    table_dir = repo_root / "packages" / "ui" / "src" / "table"
    print(f"==> Verifying Subphase 00.08 Advanced Table Grid in {table_dir}...")

    _verify_controllers(table_dir)
    _verify_components(table_dir)

    index_file = table_dir / "index.ts"
    assert index_file.exists(), "index.ts must exist"
    assert len(index_file.read_text(encoding="utf-8").splitlines()) <= 30, (
        "Barrel must be <= 30 lines"
    )

    print("\n==> Subphase 00.08 Verification Suite PASSED (100% assertions satisfied).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
