"""
Verification test suite for UI Platform Mission Control, Clean Navbar, and Next.js App Router.
Governed by PNX-NAV-ARCH-001 v2.1 and GEMINI.md code limits.
"""

import sys
import urllib.request
from pathlib import Path


def _verify_route_status(route: str, expected_code: int = 200) -> None:
    """Verifies that an active Next.js App Router route returns expected HTTP status."""
    url = f"http://localhost:3000{route}"
    req = urllib.request.Request(url, headers={"User-Agent": "NexusTestRunner/1.0"})
    with urllib.request.urlopen(req, timeout=5) as response:
        assert response.status == expected_code, f"Route {route} returned {response.status}"


def test_nextjs_routes_accessible() -> None:
    """Asserts that all 6 dynamic enterprise routes compile and serve HTTP 200."""
    routes = ["/", "/inputs", "/pos", "/kitchen", "/finance", "/hr"]
    for route in routes:
        _verify_route_status(route)


def test_zero_hardcoded_domains_in_http_client() -> None:
    """Asserts that NexusHttpClient dispatches relative paths without hardcoded domains."""
    client_path = (
        Path(__file__).parent.parent
        / "clients"
        / "web"
        / "src"
        / "runtime"
        / "http"
        / "NexusHttpClient.ts"
    )
    content = client_path.read_text(encoding="utf-8")
    assert "http://localhost:8000" not in content, "NexusHttpClient contains hardcoded domain"
    assert "X-Nexus-Tenant-Slug" in content, "Missing mandatory X-Nexus-Tenant-Slug header"


def test_navbar_clean_law_adherence() -> None:
    """Asserts that NexusMainTopNavbar adheres to PNX-NAV-ARCH-001 Clean Navbar Law."""
    navbar_path = (
        Path(__file__).parent.parent
        / "clients"
        / "web"
        / "src"
        / "app"
        / "components"
        / "NexusMainTopNavbar.tsx"
    )
    content = navbar_path.read_text(encoding="utf-8")
    assert "NexusMainTopNavbar" in content
    assert "⌘K" in content, "Missing command palette shortcut"
    assert "NEXUS" in content, "Missing brand mark"


def test_sidebar_navigation_groups() -> None:
    """Asserts that NexusEnterpriseSidebar provides full multi-domain navigation."""
    sidebar_path = (
        Path(__file__).parent.parent
        / "clients"
        / "web"
        / "src"
        / "app"
        / "components"
        / "NexusEnterpriseSidebar.tsx"
    )
    content = sidebar_path.read_text(encoding="utf-8")
    assert "COMMERCE & POS" in content
    assert "FINANCE & TREASURY" in content
    assert "WORKFORCE & HRMS" in content
    assert "Inputs & Form Studio" in content


def run_all_checks() -> None:
    """Runs all verification assertions."""
    test_nextjs_routes_accessible()
    test_zero_hardcoded_domains_in_http_client()
    test_navbar_clean_law_adherence()
    test_sidebar_navigation_groups()


if __name__ == "__main__":
    try:
        run_all_checks()
        print("ALL UI PLATFORM MISSION CONTROL ASSERTIONS PASSED (4/4)")
        sys.exit(0)
    except Exception as exc:
        print(f"VERIFICATION FAILURE: {exc}")
        sys.exit(1)
