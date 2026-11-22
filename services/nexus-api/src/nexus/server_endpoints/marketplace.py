"""
nexus.server_endpoints.marketplace - Features & Capability Marketplace endpoints.
Governs ModulePackage catalog, TenantPluginInstallation, and zero-restart feature toggling.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PluginPackageDTO:
    code: str
    name: str
    description: str
    tier: str
    execution_surface: str
    version: str
    status: str
    icon: str
    category: str
    dependencies: tuple[str, ...]
    installed_at: int | None


# Catalog of first-party capabilities and ecosystem plugins
_MARKETPLACE_CATALOG: dict[str, dict[str, Any]] = {
    "CAFE_QSR": {
        "code": "CAFE_QSR",
        "name": "Café & QSR Fast-Order Engine",
        "description": "Counter ordering, hot-key modifiers, seat tagging, barcode scanning, and fast split-tender.",
        "tier": "TIER_3_FIRST_PARTY",
        "execution_surface": "WEB_ALL",
        "version": "2.4.0",
        "status": "ACTIVE",
        "icon": "local_cafe",
        "category": "Food & Beverage",
        "dependencies": (),
        "installed_at": 1732272000,
    },
    "POS_COUNTER": {
        "code": "POS_COUNTER",
        "name": "Touch Counter POS & Folio",
        "description": "High-density touch canvas, multi-tender settlement, order holds, and receipt generation.",
        "tier": "TIER_3_FIRST_PARTY",
        "execution_surface": "WEB_ALL",
        "version": "2.4.0",
        "status": "ACTIVE",
        "icon": "point_of_sale",
        "category": "Commerce",
        "dependencies": (),
        "installed_at": 1732272000,
    },
    "KDS_KITCHEN": {
        "code": "KDS_KITCHEN",
        "name": "Kitchen Display & Bump Station",
        "description": "Real-time kitchen order ticket routing across Barista, Kitchen, and Pass with SLA countdowns.",
        "tier": "TIER_3_FIRST_PARTY",
        "execution_surface": "WEB_ALL",
        "version": "2.1.0",
        "status": "ACTIVE",
        "icon": "skillet",
        "category": "Kitchen Ops",
        "dependencies": ("POS_COUNTER",),
        "installed_at": 1732272000,
    },
    "INVENTORY_BOM": {
        "code": "INVENTORY_BOM",
        "name": "Recipe BOM & Stock Engine",
        "description": "Multi-warehouse batch tracking (FEFO/FIFO) with automatic ingredient decrement on KDS bump.",
        "tier": "TIER_2_SHARED",
        "execution_surface": "WEB_ALL",
        "version": "3.0.0",
        "status": "ACTIVE",
        "icon": "inventory_2",
        "category": "Supply Chain",
        "dependencies": (),
        "installed_at": 1732272000,
    },
    "FIN_CORE": {
        "code": "FIN_CORE",
        "name": "Protected Basic Finance & Cashiering",
        "description": "Shift opening float, blind count close, denomination counters, cash drop audits, and ledger.",
        "tier": "TIER_1_KERNEL",
        "execution_surface": "WEB_ALL",
        "version": "1.0.0",
        "status": "ACTIVE",
        "icon": "payments",
        "category": "Finance",
        "dependencies": (),
        "installed_at": 1732272000,
    },
    "HR_CORE": {
        "code": "HR_CORE",
        "name": "Staff Roster & Biometric Punch Clock",
        "description": "Cashier PIN security, biometric punch clock in/out, dynamic shift assignments, and ESS.",
        "tier": "TIER_1_KERNEL",
        "execution_surface": "WEB_ALL",
        "version": "1.0.0",
        "status": "ACTIVE",
        "icon": "badge",
        "category": "Workforce",
        "dependencies": (),
        "installed_at": 1732272000,
    },
    "HW_PERIPHERALS": {
        "code": "HW_PERIPHERALS",
        "name": "Hardware Peripherals & ESC/POS Driver",
        "description": "Native ESC/POS thermal printing, RJ11 cash drawer kick pulses, and serial EDC bridges.",
        "tier": "TIER_3_FIRST_PARTY",
        "execution_surface": "DESKTOP_ONLY",
        "version": "2.0.1",
        "status": "ACTIVE",
        "icon": "print",
        "category": "Hardware",
        "dependencies": (),
        "installed_at": 1732272000,
    },
    "GAME_CORE": {
        "code": "GAME_CORE",
        "name": "Gaming Lounge & 2D Floor Canvas",
        "description": "60fps interactive 2D venue canvas, compound station scheduling (PC/Console/VR), and 10-dim UTC timers.",
        "tier": "TIER_3_FIRST_PARTY",
        "execution_surface": "HYBRID_WEB_DESKTOP",
        "version": "1.0.0-rc1",
        "status": "ARCHIVED",
        "icon": "terminal",
        "category": "Gaming & Venue",
        "dependencies": ("POS_COUNTER",),
        "installed_at": None,
    },
    "LOYALTY_CRM": {
        "code": "LOYALTY_CRM",
        "name": "Customer Loyalty & WhatsApp Bot",
        "description": "Prepaid customer wallets, tiered loyalty points ledger, dynamic AST promotions, and WhatsApp bot.",
        "tier": "TIER_4_ECOSYSTEM",
        "execution_surface": "WEB_ALL",
        "version": "1.2.0",
        "status": "ARCHIVED",
        "icon": "verified",
        "category": "Growth",
        "dependencies": (),
        "installed_at": None,
    },
}


class MarketplaceEndpointHandler:
    """Coordinator for Plugin Module Marketplace and Feature Enablement."""

    @classmethod
    def list_plugins(cls) -> dict[str, Any]:
        """Return catalog of available capabilities and their installation states."""
        plugins = [
            PluginPackageDTO(
                code=p["code"],
                name=p["name"],
                description=p["description"],
                tier=p["tier"],
                execution_surface=p["execution_surface"],
                version=p["version"],
                status=p["status"],
                icon=p["icon"],
                category=p["category"],
                dependencies=tuple(p["dependencies"]),
                installed_at=p["installed_at"],
            )
            for p in _MARKETPLACE_CATALOG.values()
        ]
        installed = sum(1 for p in plugins if p.status == "ACTIVE")
        return {
            "plugins": [asdict(p) for p in plugins],
            "total_count": len(plugins),
            "installed_count": installed,
            "available_count": len(plugins) - installed,
        }

    @classmethod
    def toggle_plugin(cls, payload: dict[str, Any]) -> dict[str, Any]:
        """Install, enable, drain, or archive a plugin package."""
        code = str(payload.get("code", "")).upper()
        action = str(payload.get("action", "INSTALL")).upper()

        if code not in _MARKETPLACE_CATALOG:
            return {"success": False, "error": f"Unknown capability package: {code}"}

        pkg = _MARKETPLACE_CATALOG[code]
        # Validate dependencies if activating
        if action in {"INSTALL", "ENABLE"}:
            for dep in pkg["dependencies"]:
                if _MARKETPLACE_CATALOG.get(dep, {}).get("status") != "ACTIVE":
                    return {
                        "success": False,
                        "error": f"Dependency unmet: {code} requires {dep} to be active first.",
                    }
            pkg["status"] = "ACTIVE"
            pkg["installed_at"] = int(time.time())
        elif action == "DRAIN":
            pkg["status"] = "DRAINING"
        elif action == "ARCHIVE":
            pkg["status"] = "ARCHIVED"
            pkg["installed_at"] = None

        return {
            "success": True,
            "code": code,
            "status": pkg["status"],
            "installed_at": pkg["installed_at"],
            "execution_surface": pkg["execution_surface"],
            "message": f"Plugin {code} successfully transitioned to {pkg['status']}.",
        }
