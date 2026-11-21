#!/usr/bin/env python3
"""
verify_form_kernel.py - Verification suite for Subphase 00.09 (Advanced Forms & Controller Kernel).
"""

from __future__ import annotations

import sys
from pathlib import Path


def _verify_controllers(forms_dir: Path) -> None:
    base_ctrl = forms_dir / "BaseFormController.ts"
    batch_coord = forms_dir / "BatchLookupCoordinator.ts"
    val_ctrl = forms_dir / "FormValidationController.ts"

    assert base_ctrl.exists() and batch_coord.exists() and val_ctrl.exists()
    content = base_ctrl.read_text(encoding="utf-8")
    assert "class BaseFormController" in content
    assert "isDirty" in content
    assert "validationController" in content
    assert "lookupCoordinator" in content
    print("  [PASS] BaseFormController, BatchLookupCoordinator, and FormValidationController verified")


def _verify_components(forms_dir: Path) -> None:
    form_comp = forms_dir / "NexusForm.tsx"
    assert form_comp.exists(), "NexusForm.tsx must exist"
    content = form_comp.read_text(encoding="utf-8")
    assert "function NexusForm" in content
    assert "controller" in content
    print("  [PASS] NexusForm component verified")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    forms_dir = repo_root / "packages" / "ui" / "src" / "forms"
    print(f"==> Verifying Subphase 00.09 Advanced Form Kernel in {forms_dir}...")

    _verify_controllers(forms_dir)
    _verify_components(forms_dir)

    index_file = forms_dir / "index.ts"
    assert index_file.exists(), "index.ts must exist"
    assert len(index_file.read_text(encoding="utf-8").splitlines()) <= 30, "Barrel must be <= 30 lines"

    print("\n==> Subphase 00.09 Verification Suite PASSED (100% assertions satisfied).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
