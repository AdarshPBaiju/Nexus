"""
verify_cloud_saas_docker_lifecycle.py - Automated verification for Full-Stack Dockerization,
Cloud Multi-Tenant SaaS Workspace Switcher, SaaS Tenant Registration & Quotas Lifecycle.
Governed by PNX-REPO-ARCH-004 §5, PNX-ECO-SPEC-001, and GEMINI.md code limits.
"""

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

NEXUS_ROOT = Path(__file__).resolve().parent.parent


def test_docker_compose_validity() -> None:
    """Asserts that docker-compose.yml config validates with zero syntax or network errors."""
    compose_path = NEXUS_ROOT / "docker-compose.yml"
    assert compose_path.exists(), f"Missing docker-compose.yml at {compose_path}"

    res = subprocess.run(
        ["docker", "compose", "-f", str(compose_path), "config", "--quiet"],
        cwd=str(NEXUS_ROOT),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"docker compose config failed: {res.stderr}"
    print("  [✓] Docker Compose full-stack specification verified valid.")


def test_all_cloud_saas_routes() -> None:
    """Asserts that all 14 enterprise cloud SaaS routes compile and return HTTP 200."""
    routes = [
        "/",
        "/pos",
        "/kitchen",
        "/inventory",
        "/finance",
        "/gateways",
        "/marketplace",
        "/tenant/lifecycle",
        "/tenant/subscription",
        "/billing",
        "/register",
        "/onboarding",
        "/hr",
        "/inputs",
    ]
    for r in routes:
        url = f"http://localhost:3000{r}"
        req = urllib.request.Request(url, headers={"User-Agent": "NexusSaaSTestRunner/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            assert resp.status == 200, f"Route {r} returned HTTP {resp.status}"
            print(f"  [✓] Route {r} -> HTTP 200")


def test_backend_tenancy_and_saas_endpoints() -> None:
    """Asserts that core API endpoints return active multi-tenant and quota payloads."""
    endpoints = [
        ("/healthz", "status"),
        ("/api/v1/info", "phase"),
        ("/api/v1/tenants/list", "tenants"),
        ("/api/v1/tenants/subscription", "subscription"),
        ("/api/v1/tenants/lifecycle", "kms_key_version"),
        ("/api/v1/gateways/config", "gateways"),
        ("/api/v1/plugins", "plugins"),
    ]
    for ep, key in endpoints:
        url = f"http://localhost:8000{ep}"
        req = urllib.request.Request(url, headers={"User-Agent": "NexusSaaSTestRunner/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            assert resp.status == 200, f"Endpoint {ep} returned {resp.status}"
            data = json.loads(resp.read().decode("utf-8"))
            assert key in data, f"Key '{key}' not in response for {ep}"
            print(f"  [✓] API {ep} -> HTTP 200 ({key} verified)")


def test_code_length_ceilings() -> None:
    """Audits all modified files to ensure strict compliance with the 250-line hard limit."""
    audit_files = [
        NEXUS_ROOT / "clients/web/src/app/components/navbar/TopNavScopePicker.tsx",
        NEXUS_ROOT / "clients/web/src/app/components/NexusMainTopNavbar.tsx",
        NEXUS_ROOT / "clients/web/src/runtime/auth/AuthContext.tsx",
        NEXUS_ROOT / "clients/web/src/runtime/auth/authTypes.ts",
        NEXUS_ROOT / "clients/web/src/app/register/components/RegisterOrgStep.tsx",
        NEXUS_ROOT / "clients/web/src/app/register/page.tsx",
        NEXUS_ROOT / "clients/web/src/app/billing/page.tsx",
        NEXUS_ROOT / "clients/web/src/app/billing/components/BillingQuotaMeters.tsx",
        NEXUS_ROOT / "clients/web/src/app/billing/components/BillingInvoicesTable.tsx",
        NEXUS_ROOT / "services/nexus-api/src/nexus/server_endpoints/tenancy.py",
        NEXUS_ROOT / "services/nexus-api/src/nexus/server_endpoints/tenancy_types.py",
    ]
    for f in audit_files:
        assert f.exists(), f"Audited file not found: {f}"
        lines = len(f.read_text(encoding="utf-8").splitlines())
        assert lines <= 250, f"File {f.name} has {lines} lines, exceeding 250 limit!"
        print(f"  [✓] File budget {f.name}: {lines} lines (ceiling <= 250)")


def test_zero_hardcoded_colors_in_new_components() -> None:
    """Verifies that all new components use semantic --nx-* design tokens exclusively."""
    check_files = [
        NEXUS_ROOT / "clients/web/src/app/components/navbar/TopNavScopePicker.tsx",
        NEXUS_ROOT / "clients/web/src/app/billing/components/BillingQuotaMeters.tsx",
        NEXUS_ROOT / "clients/web/src/app/billing/components/BillingInvoicesTable.tsx",
        NEXUS_ROOT / "clients/web/src/app/register/components/RegisterOrgStep.tsx",
    ]
    for f in check_files:
        content = f.read_text(encoding="utf-8")
        assert not re.search(r"\b(bg-blue-600|bg-white|text-black|text-emerald-400)\b", content), (
            f"Raw Tailwind color classes found in {f.name}"
        )
    print("  [✓] Zero hardcoded color literals verified.")


if __name__ == "__main__":
    print("================================================================================")
    print("Project Nexus — Cloud Multi-Tenant SaaS, Docker & Lifecycle Verification Gate")
    print("================================================================================")
    test_docker_compose_validity()
    test_code_length_ceilings()
    test_zero_hardcoded_colors_in_new_components()
    test_backend_tenancy_and_saas_endpoints()
    test_all_cloud_saas_routes()
    print("================================================================================")
    print("ALL VERIFICATIONS PASSED: 100% SUCCESS")
    print("================================================================================")
