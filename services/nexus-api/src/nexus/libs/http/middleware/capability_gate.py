"""
nexus.libs.http.middleware.capability_gate - Capability Gate & Execution Surface Middleware.
Enforces:
1. Feature Enablement ("Install = Enable"): 403 Forbidden if package is not ACTIVE.
2. Surface Guard: 403 Forbidden if DESKTOP_ONLY route is called without X-Nexus-Runtime-Surface: desktop.
3. Non-Destructive Draining: 409 Conflict if mutation hits a DRAINING package.
"""

from __future__ import annotations

import uuid
from typing import Any, Callable

from django.apps import apps
from django.http import HttpRequest, HttpResponse, JsonResponse

STATUS_DRAINING = "DRAINING"
STATUS_ARCHIVED = "ARCHIVED"
SURFACE_DESKTOP_ONLY = "DESKTOP_ONLY"


class CapabilityGateMiddleware:
    """
    Guards module API endpoints against disabled plugins and mismatched execution surfaces.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        package_code = self._extract_package_code(request.path)
        if not package_code:
            return self.get_response(request)

        tenant_id = self._resolve_tenant_id(request)
        if not tenant_id:
            return self.get_response(request)

        installation = self._find_installation(tenant_id, package_code)
        if not installation or getattr(installation, "status", None) == STATUS_ARCHIVED:
            return self._build_not_enabled_response(package_code)

        drain_err = self._check_draining_violation(installation, request, package_code)
        if drain_err:
            return drain_err

        surface_err = self._check_surface_violation(installation, request, package_code)
        if surface_err:
            return surface_err

        return self.get_response(request)

    def _find_installation(self, tenant_id: uuid.UUID, package_code: str) -> Any:
        installation_model = apps.get_model("licensing", "TenantPluginInstallation")
        return (
            installation_model.objects.filter(
                tenant_id=tenant_id,
                package__code=package_code,
            )
            .select_related("package")
            .first()
        )

    def _build_not_enabled_response(self, package_code: str) -> JsonResponse:
        return JsonResponse(
            {
                "error": "Forbidden",
                "code": "FEATURE_NOT_ENABLED",
                "detail": f"Feature '{package_code}' is not installed or enabled for this workspace.",
            },
            status=403,
        )

    def _check_draining_violation(
        self,
        installation: Any,
        request: HttpRequest,
        package_code: str,
    ) -> JsonResponse | None:
        if getattr(installation, "status", None) == STATUS_DRAINING and request.method in {
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        }:
            return JsonResponse(
                {
                    "error": "Conflict",
                    "code": "PLUGIN_DRAINING",
                    "detail": f"Feature '{package_code}' is draining; new mutations are disallowed.",
                },
                status=409,
            )
        return None

    def _check_surface_violation(
        self,
        installation: Any,
        request: HttpRequest,
        package_code: str,
    ) -> JsonResponse | None:
        pkg = getattr(installation, "package", None)
        if getattr(pkg, "execution_surface", None) == SURFACE_DESKTOP_ONLY:
            runtime = request.headers.get("X-Nexus-Runtime-Surface", "").lower()
            if runtime != "desktop":
                return JsonResponse(
                    {
                        "error": "Forbidden",
                        "code": "REQUIRES_DESKTOP_RUNTIME",
                        "detail": f"Feature '{package_code}' strictly requires the Nexus Desktop native runtime.",
                    },
                    status=403,
                )
        return None

    def _extract_package_code(self, path: str) -> str | None:
        if not path.startswith("/api/v1/"):
            return None
        parts = path.strip("/").split("/")
        return parts[2].upper() if len(parts) >= 3 else None

    def _resolve_tenant_id(self, request: HttpRequest) -> uuid.UUID | None:
        if hasattr(request, "actor") and request.actor.tenant_id:
            return request.actor.tenant_id
        tid_hdr = request.headers.get("X-Nexus-Tenant-Slug") or request.headers.get(
            "X-Nexus-Tenant-Id"
        )
        if tid_hdr:
            try:
                return uuid.UUID(tid_hdr)
            except ValueError:
                return None
        return None
