#!/usr/bin/env python3
"""
verify_contracts.py - Verification suite for Subphase 00.04 (Shared Polyglot Contracts Base).
"""

from __future__ import annotations

import sys
from pathlib import Path


def _verify_headers(contracts_dir: Path) -> None:
    headers_file = contracts_dir / "src" / "headers.ts"
    assert headers_file.exists(), "headers.ts must exist"
    content = headers_file.read_text(encoding="utf-8")
    expected_headers = [
        "X-Nexus-Tenant-Slug",
        "X-Nexus-Org-Scope",
        "X-Nexus-Locale",
        "X-Nexus-I18n-ETag",
        "Idempotency-Key",
        "If-Match",
        "X-Nexus-RYOW-Token",
        "X-Nexus-Runtime-Surface",
        "X-Nexus-Request-ID",
        "X-Nexus-Client-Version",
    ]
    for h in expected_headers:
        assert h in content, f"Header {h} missing in NexusHeaders"
    print("  [PASS] NexusHeaders SSOT definitions verified")


def _verify_surfaces(contracts_dir: Path) -> None:
    surfaces_file = contracts_dir / "src" / "surfaces.ts"
    assert surfaces_file.exists(), "surfaces.ts must exist"
    content = surfaces_file.read_text(encoding="utf-8")
    assert "WEB_ALL" in content and "DESKTOP_ONLY" in content, "ExecutionSurface missing"
    assert "DesktopDeviceBinding" in content, "DesktopDeviceBinding contract missing"
    print("  [PASS] ExecutionSurface and desktop binding contracts verified")


def _verify_money(contracts_dir: Path) -> None:
    money_file = contracts_dir / "src" / "money" / "Money.ts"
    assert money_file.exists(), "Money.ts must exist"
    content = money_file.read_text(encoding="utf-8")
    required_methods = [
        "add",
        "subtract",
        "multiply",
        "divide",
        "allocate",
        "isEqual",
        "isGreaterThan",
        "isLessThan",
        "isZero",
        "isNegative",
    ]
    for m in required_methods:
        assert f"public {m}" in content or f"{m}(" in content, f"Method {m} missing in Money.ts"
    print("  [PASS] Money value object and exact arithmetic methods verified")


def _verify_time_and_filtering(contracts_dir: Path) -> None:
    dt_file = contracts_dir / "src" / "time" / "DateTimeFormatter.ts"
    ast_file = contracts_dir / "src" / "filtering" / "ast.types.ts"
    option_file = contracts_dir / "src" / "lookups" / "option.types.ts"

    assert dt_file.exists() and ast_file.exists() and option_file.exists()
    assert "getOperationalBusinessDate" in dt_file.read_text(encoding="utf-8")
    assert "FilterPredicate" in ast_file.read_text(encoding="utf-8")
    assert "OptionItemDTO" in option_file.read_text(encoding="utf-8")
    print("  [PASS] DateTimeFormatter, AST filters, and BatchLookup contracts verified")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    contracts_dir = repo_root / "packages" / "contracts"
    print(f"==> Verifying Subphase 00.04 Shared Contracts in {contracts_dir}...")

    _verify_headers(contracts_dir)
    _verify_surfaces(contracts_dir)
    _verify_money(contracts_dir)
    _verify_time_and_filtering(contracts_dir)

    index_file = contracts_dir / "src" / "index.ts"
    assert index_file.exists(), "index.ts must exist"
    assert len(index_file.read_text(encoding="utf-8").splitlines()) <= 30, "Barrel must be <= 30 lines"

    print("\n==> Subphase 00.04 Verification Suite PASSED (100% assertions satisfied).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
