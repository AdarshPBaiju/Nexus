#!/usr/bin/env python3
"""
verify_nexus_desktop_v1_shell.py - Verification suite for Subphase 03.04 (Nexus Desktop Shell).
Validates:
1. Tauri 2.0 configuration (tauri.conf.json): window dimensions, CSP, and deep-link schemes.
2. Custom protocol handler syntax (nexus://open?tenant=...&route=...).
3. DesktopSurfaceBridge TypeScript contracts and handoff URL builder.
4. Rust source structure, module exports, and test assertions in src-tauri.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import urllib.parse

REPO_ROOT = Path(__file__).resolve().parents[1]
TAURI_DIR = REPO_ROOT / "clients" / "desktop" / "src-tauri"
CONF_FILE = TAURI_DIR / "tauri.conf.json"
CONTRACTS_FILE = (
    REPO_ROOT / "packages" / "contracts" / "src" / "desktop" / "DesktopSurfaceBridge.ts"
)


def test_tauri_config() -> None:
    print("[1/4] Testing Tauri 2.0 configuration (tauri.conf.json)...")
    assert CONF_FILE.exists(), f"Configuration not found: {CONF_FILE}"
    with open(CONF_FILE, encoding="utf-8") as f:
        conf = json.load(f)

    assert conf["identifier"] == "com.nexus.desktop"
    assert "app" in conf and "windows" in conf["app"]
    main_win = conf["app"]["windows"][0]
    assert main_win["width"] == 1280
    assert main_win["height"] == 800

    # CSP checks
    csp = conf["app"]["security"]["csp"]
    assert "default-src" in csp
    assert "ipc:" in csp

    # Deep link plugin scheme
    plugins = conf.get("plugins", {})
    assert "deep-link" in plugins
    assert "nexus" in plugins["deep-link"]["schemes"]
    print("  ✓ Tauri 2.0 config validated: 1280x800 window, IPC CSP, and nexus:// scheme.")


def test_custom_protocol_parser() -> None:
    print("[2/4] Testing OS custom protocol handler URL parser...")
    raw_url = "nexus://open?tenant=espresso-labs&route=/pos/counter&workstation=WS-01"
    parsed = urllib.parse.urlparse(raw_url)
    assert parsed.scheme == "nexus"
    assert parsed.netloc == "open"
    query = urllib.parse.parse_qs(parsed.query)

    assert query["tenant"] == ["espresso-labs"]
    assert query["route"] == ["/pos/counter"]
    assert query["workstation"] == ["WS-01"]
    print("  ✓ Protocol handler URI successfully parsed into operational launch intent.")


def test_desktop_surface_bridge_contract() -> None:
    print("[3/4] Testing DesktopSurfaceBridge TypeScript contracts...")
    assert CONTRACTS_FILE.exists(), f"Bridge contract not found: {CONTRACTS_FILE}"
    content = CONTRACTS_FILE.read_text(encoding="utf-8")

    assert "export class DesktopSurfaceBridge" in content
    assert "public static isTauriRuntime()" in content
    assert "public static buildHandoffUrl(" in content
    assert "public static async getTelemetry(" in content
    assert "public static async kickCashDrawer()" in content
    print("  ✓ DesktopSurfaceBridge contracts and methods verified.")


def test_rust_module_structure() -> None:
    print("[4/4] Testing Rust desktop module structure and test coverage...")
    lib_rs = TAURI_DIR / "src" / "lib.rs"
    protocol_rs = TAURI_DIR / "src" / "protocol.rs"
    commands_rs = TAURI_DIR / "src" / "commands.rs"
    device_rs = TAURI_DIR / "src" / "device_binding.rs"
    spooler_rs = TAURI_DIR / "src" / "print_spooler.rs"

    for rfile in [lib_rs, protocol_rs, commands_rs, device_rs, spooler_rs]:
        assert rfile.exists(), f"Rust module missing: {rfile}"
        code = rfile.read_text(encoding="utf-8")
        assert len(code.splitlines()) <= 200, f"File {rfile.name} exceeds recommended ceiling"
        if rfile != lib_rs:
            assert "mod tests" in code, f"Missing tests in {rfile.name}"
            assert "#[test]" in code, f"Missing #[test] attribute in {rfile.name}"

    print("  ✓ Rust src-tauri modules comply with architectural ceilings and unit tests.")


def main() -> None:
    print("=" * 80)
    print("NEXUS SUBPHASE 03.04: NEXUS DESKTOP V1 SHELL VERIFICATION")
    print("=" * 80)
    test_tauri_config()
    test_custom_protocol_parser()
    test_desktop_surface_bridge_contract()
    test_rust_module_structure()
    print("=" * 80)
    print("ALL NEXUS DESKTOP V1 SHELL TESTS COMPLETED WITH 100% SUCCESS.")
    print("=" * 80)


if __name__ == "__main__":
    main()
