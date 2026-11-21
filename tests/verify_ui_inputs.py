#!/usr/bin/env python3
"""
verify_ui_inputs.py - Verification suite for Subphase 00.06 (19 In-House Enterprise Custom Inputs).
"""

from __future__ import annotations

import sys
from pathlib import Path

EXPECTED_INPUTS = [
    "NexusTextInput",
    "NexusNumberInput",
    "NexusSelect",
    "NexusMultiSelect",
    "NexusDateInput",
    "NexusDateRangeInput",
    "NexusTimeInput",
    "NexusCheckbox",
    "NexusCheckboxGroup",
    "NexusRadioGroup",
    "NexusSwitch",
    "NexusTextarea",
    "NexusMoneyInput",
    "NexusSearchInput",
    "NexusColorPicker",
    "NexusFileInput",
    "NexusSlider",
    "NexusPinInput",
    "NexusLocalizedTextInput",
]


def _verify_input_files(inputs_dir: Path) -> None:
    types_file = inputs_dir / "types.ts"
    assert types_file.exists(), "types.ts must exist"
    assert "NexusControlProps" in types_file.read_text(encoding="utf-8")

    for input_name in EXPECTED_INPUTS:
        component_file = inputs_dir / f"{input_name}.tsx"
        assert component_file.exists(), f"Input component {input_name}.tsx must exist"
        content = component_file.read_text(encoding="utf-8")
        assert f"export function {input_name}" in content, f"Function {input_name} missing"
    print(f"  [PASS] All {len(EXPECTED_INPUTS)} custom input primitives verified")


def _verify_barrel_exports(inputs_dir: Path) -> None:
    index_file = inputs_dir / "index.ts"
    assert index_file.exists(), "index.ts must exist in inputs/"
    content = index_file.read_text(encoding="utf-8")
    for input_name in EXPECTED_INPUTS:
        assert f"export * from './{input_name}';" in content, f"Export for {input_name} missing"
    print("  [PASS] Custom inputs barrel re-exports verified")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    inputs_dir = repo_root / "packages" / "ui" / "src" / "inputs"
    print(f"==> Verifying Subphase 00.06 19 Custom Inputs in {inputs_dir}...")

    _verify_input_files(inputs_dir)
    _verify_barrel_exports(inputs_dir)

    print("\n==> Subphase 00.06 Verification Suite PASSED (100% assertions satisfied).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
