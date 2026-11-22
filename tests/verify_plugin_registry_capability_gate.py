#!/usr/bin/env python3
"""
verify_plugin_registry_capability_gate.py - Verification suite for Subphase 01.03.
Validates:
1. ModulePackage and TenantPluginInstallation declarative feature enablement.
2. Non-destructive uninstall state machine (ACTIVE -> DRAINING -> ARCHIVED).
3. Cryptographic Ed25519 offline license certificates.
4. CapabilityGateMiddleware surface guarding and draining defense.
5. Polyglot TypeScript contracts parity.
"""

from __future__ import annotations

from typing import Any

import os
import sys
import time
from pathlib import Path

# Add nexus-api src to sys.path first
REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "services" / "nexus-api" / "src"
sys.path.insert(0, str(API_SRC))

# Setup Django minimal settings for standalone model checks
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexus_test_settings")
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "nexus.platform.tenancy",
            "nexus.platform.licensing",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command
from django.http import HttpRequest, HttpResponse

call_command("migrate", run_syncdb=True, verbosity=0)

from nexus.libs.http.actor import ActorContext, ActorType
from nexus.libs.http.middleware.capability_gate import CapabilityGateMiddleware
from nexus.libs.ids import new_uuid7
from nexus.platform.licensing.certs import (
    LicenseCertPayload,
    OfflineLicenseCertificateService,
)
from nexus.platform.licensing.models import (
    ModulePackage,
    ModulePricingOffer,
    TenantPluginInstallation,
)
from nexus.platform.tenancy.models import Tenant


def _verify_package_catalog_and_offers() -> None:
    pkg_pos = ModulePackage.objects.create(
        code="POS",
        name="Counter Point of Sale",
        tier=ModulePackage.Tier.FIRST_PARTY_CAPABILITY,
        execution_surface=ModulePackage.ExecutionSurface.WEB_ALL,
    )
    assert not pkg_pos.requires_desktop

    pkg_hw = ModulePackage.objects.create(
        code="HW_PRINTER_LOCAL",
        name="Silent ESC/POS Thermal Printing",
        tier=ModulePackage.Tier.FIRST_PARTY_CAPABILITY,
        execution_surface=ModulePackage.ExecutionSurface.DESKTOP_ONLY,
    )
    assert pkg_hw.requires_desktop

    offer = ModulePricingOffer.objects.create(
        package=pkg_pos,
        license_model=ModulePricingOffer.LicenseModel.FREE_INCLUDED,
    )
    assert offer.package_id == pkg_pos.id
    print("  [PASS] ModulePackage catalog and pricing offers verified")


def _verify_installation_state_machine() -> None:
    tenant = Tenant.objects.create(slug="cafe-one", legal_name="Café One")
    pkg = ModulePackage.objects.get(code="POS")

    install = TenantPluginInstallation.objects.create(
        tenant_id=tenant.id,
        package=pkg,
        status=TenantPluginInstallation.InstallationStatus.ACTIVE,
    )
    assert install.is_operational

    # Non-destructive draining transition
    install.transition_to_draining()
    assert not install.is_operational
    assert install.status == TenantPluginInstallation.InstallationStatus.DRAINING

    # Archive
    install.archive()
    assert install.status == TenantPluginInstallation.InstallationStatus.ARCHIVED

    # Reactivate
    install.reactivate()
    assert install.is_operational
    print("  [PASS] Non-destructive lifecycle state machine verified")


def _verify_offline_certificates() -> None:
    priv_key, pub_key = OfflineLicenseCertificateService.generate_key_pair()
    tenant_id = new_uuid7()
    exp = int(time.time()) + 86400

    payload_obj = LicenseCertPayload(
        tenant_id=tenant_id,
        package_code="POS",
        capacity_limit=5,
        expires_epoch=exp,
    )
    cert_b64 = OfflineLicenseCertificateService.sign_certificate(priv_key, payload_obj)
    assert isinstance(cert_b64, str) and len(cert_b64) > 30

    verified = OfflineLicenseCertificateService.verify_certificate(pub_key, cert_b64)
    assert verified is not None
    assert verified["package"] == "POS"
    assert verified["capacity"] == 5

    tampered_cert = cert_b64[:-8] + "xxxxxxxx"
    assert OfflineLicenseCertificateService.verify_certificate(pub_key, tampered_cert) is None
    print("  [PASS] Cryptographic Ed25519 offline license certificates verified")


def _verify_gate_install_and_surface(
    gate: CapabilityGateMiddleware, tenant: Tenant, make_req: Any
) -> None:
    # 1. Uninstalled module -> 403 FEATURE_NOT_ENABLED
    resp_uninstalled = gate(make_req("/api/v1/kds/orders/"))
    assert resp_uninstalled.status_code == 403
    assert b"FEATURE_NOT_ENABLED" in resp_uninstalled.content

    # 2. Installed WEB_ALL module (POS) -> 200 OK
    resp_pos = gate(make_req("/api/v1/pos/billing/"))
    assert resp_pos.status_code == 200

    # 3. Installed DESKTOP_ONLY module called from browser without desktop header -> 403 REQUIRES_DESKTOP_RUNTIME
    resp_desktop_blocked = gate(make_req("/api/v1/hw_printer_local/print/"))
    assert resp_desktop_blocked.status_code == 403
    assert b"REQUIRES_DESKTOP_RUNTIME" in resp_desktop_blocked.content

    # 4. Installed DESKTOP_ONLY module called with desktop header -> 200 OK
    resp_desktop_allowed = gate(make_req("/api/v1/hw_printer_local/print/", surface="desktop"))
    assert resp_desktop_allowed.status_code == 200


def _verify_gate_draining(
    gate: CapabilityGateMiddleware, tenant: Tenant, pkg_pos: ModulePackage, make_req: Any
) -> None:
    install_pos = TenantPluginInstallation.objects.get(tenant_id=tenant.id, package=pkg_pos)
    install_pos.transition_to_draining()
    install_pos.save()

    resp_drain_get = gate(make_req("/api/v1/pos/orders/"))
    assert resp_drain_get.status_code == 200

    resp_drain_post = gate(make_req("/api/v1/pos/orders/", method="POST"))
    assert resp_drain_post.status_code == 409
    assert b"PLUGIN_DRAINING" in resp_drain_post.content


def _verify_capability_gate_middleware() -> None:
    tenant = Tenant.objects.get(slug="cafe-one")
    pkg_pos = ModulePackage.objects.get(code="POS")
    pkg_hw = ModulePackage.objects.get(code="HW_PRINTER_LOCAL")

    TenantPluginInstallation.objects.create(
        tenant_id=tenant.id,
        package=pkg_hw,
        status=TenantPluginInstallation.InstallationStatus.ACTIVE,
    )

    def dummy_handler(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    gate = CapabilityGateMiddleware(dummy_handler)

    def _make_req(path: str, method: str = "GET", surface: str = "") -> HttpRequest:
        req = HttpRequest()
        req.path = path
        req.method = method
        req.headers = {"X-Nexus-Tenant-Id": str(tenant.id)}
        if surface:
            req.headers["X-Nexus-Runtime-Surface"] = surface
        req.actor = ActorContext(
            actor_type=ActorType.STAFF,
            actor_id=new_uuid7(),
            tenant_id=tenant.id,
        )
        return req

    _verify_gate_install_and_surface(gate, tenant, _make_req)
    _verify_gate_draining(gate, tenant, pkg_pos, _make_req)
    print("  [PASS] CapabilityGateMiddleware surface guard and draining defense verified")


def _verify_contracts_polyglot(repo_root: Path) -> None:
    plugins_ts = repo_root / "packages" / "contracts" / "src" / "licensing" / "plugins.ts"
    assert plugins_ts.exists(), "plugins.ts must exist"
    content = plugins_ts.read_text(encoding="utf-8")
    assert "ExecutionSurfaces" in content
    assert "buildDesktopHandoffUri" in content
    assert "nexus://open" in content
    print("  [PASS] Polyglot TypeScript licensing contracts parity verified")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    print(f"==> Verifying Subphase 01.03 Plugin Registry & Capability Gate in {repo_root}...")

    _verify_package_catalog_and_offers()
    _verify_installation_state_machine()
    _verify_offline_certificates()
    _verify_capability_gate_middleware()
    _verify_contracts_polyglot(repo_root)

    print("\n==> Subphase 01.03 Verification Suite PASSED (100% assertions satisfied).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
