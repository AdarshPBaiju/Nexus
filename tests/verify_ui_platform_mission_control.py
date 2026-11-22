"""
Verification test suite for UI Platform Mission Control, Clean Navbar, and Next.js App Router.
Governed by PNX-NAV-ARCH-001 v2.1, Rule 3 (Custom In-House UI Controls), and GEMINI.md code limits.
"""

import re
import sys
import urllib.request
from pathlib import Path


def _verify_route_status(route: str, expected_code: int = 200) -> None:
    """Verifies that an active Next.js App Router route returns expected HTTP status."""
    url = f"http://localhost:3000{route}"
    req = urllib.request.Request(url, headers={"User-Agent": "NexusTestRunner/1.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        assert response.status == expected_code, f"Route {route} returned {response.status}"


def test_nextjs_routes_accessible() -> None:
    """Asserts that all 10 dynamic enterprise SaaS routes compile and serve HTTP 200."""
    routes = [
        "/",
        "/inputs",
        "/pos",
        "/kitchen",
        "/finance",
        "/hr",
        "/inventory",
        "/gateways",
        "/billing",
        "/onboarding",
    ]
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
    navbar_dir = Path(__file__).parent.parent / "clients" / "web" / "src" / "app" / "components"
    navbar_path = navbar_dir / "NexusMainTopNavbar.tsx"
    search_path = navbar_dir / "navbar" / "TopNavSearch.tsx"
    content = navbar_path.read_text(encoding="utf-8")
    search_content = search_path.read_text(encoding="utf-8")
    assert "NexusMainTopNavbar" in content
    assert "⌘K" in search_content, "Missing command palette shortcut"
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
    assert "Mission Control" in content
    assert "Commerce & POS" in content
    assert "Inventory & Recipes" in content
    assert "Finance & Treasury" in content
    assert "Workforce & HRMS" in content
    assert "SaaS Lifecycle" in content


def test_zero_raw_inputs_and_alerts() -> None:
    """Asserts that zero raw input/select/textarea and zero alert() exist in feature views."""
    src_dir = Path(__file__).parent.parent / "clients" / "web" / "src"
    raw_input_pattern = re.compile(r"<(?:input|select|textarea)[\s>]")
    alert_pattern = re.compile(r"\balert\s*\(")

    for tsx_file in src_dir.rglob("*.tsx"):
        text = tsx_file.read_text(encoding="utf-8")
        assert not raw_input_pattern.search(text), (
            f"Found forbidden raw input/select/textarea in {tsx_file.name}"
        )
        assert not alert_pattern.search(text), f"Found forbidden alert() call in {tsx_file.name}"


def test_code_budget_ceilings() -> None:
    """Asserts that all .tsx components strictly adhere to <= 250 line ceilings."""
    src_dir = Path(__file__).parent.parent / "clients" / "web" / "src"
    for tsx_file in src_dir.rglob("*.tsx"):
        lines = len(tsx_file.read_text(encoding="utf-8").splitlines())
        assert lines <= 250, (
            f"Component {tsx_file.name} has {lines} lines, exceeding the 250-line hard ceiling!"
        )


def run_all_checks() -> None:
    """Runs all verification assertions."""
    test_zero_hardcoded_domains_in_http_client()
    test_navbar_clean_law_adherence()
    test_sidebar_navigation_groups()
    test_zero_raw_inputs_and_alerts()
    test_code_budget_ceilings()
    test_nextjs_routes_accessible()


if __name__ == "__main__":
    try:
        run_all_checks()
        print(
            "ALL CAFE SAAS PRODUCTION UI ASSERTIONS PASSED (10/10 ROUTES, ZERO RAW INPUTS, STRICT BUDGETS)"
        )
        sys.exit(0)
    except Exception as exc:
        print(f"VERIFICATION FAILURE: {exc}")
        sys.exit(1)
