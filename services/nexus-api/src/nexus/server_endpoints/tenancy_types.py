"""
nexus.server_endpoints.tenancy_types - DTOs and state for multi-tenant cloud SaaS operations.
Governs Cloud Tenant Profiles, Subscriptions, Regional Cell Topology, and Encryption metadata.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from nexus.libs.ids import new_uuid7


@dataclass(frozen=True)
class TenantSummaryDTO:
    tenant_id: str
    slug: str
    legal_name: str
    home_region: str
    status: str
    tier: str
    subdomain: str
    branch_name: str
    active_branches: int
    active_stations: int


@dataclass(frozen=True)
class TenantRegistrationDTO:
    tenant_id: str
    slug: str
    legal_name: str
    status: str
    home_region: str
    currency: str
    tax_identifier: str
    vertical: str
    branch_name: str
    admin_email: str
    created_at: int
    redirect_url: str
    access_token: str
    subdomain: str


@dataclass(frozen=True)
class TenantLifecycleStateDTO:
    tenant_id: str
    slug: str
    legal_name: str
    status: str
    home_region: str
    kms_key_version: str
    uptime_seconds: int
    active_branches: int
    active_stations: int
    compliance_mode: str
    pci_dss_level: str
    audit_events: list[dict[str, Any]]


@dataclass(frozen=True)
class TenantSubscriptionDTO:
    tenant_slug: str
    tier: str
    tier_name: str
    price_annual: str
    billing_status: str
    renewal_date: str
    isolation_model: str
    data_residency: str
    kms_status: str
    orders_today: int
    orders_quota_daily: int
    active_stations: int
    stations_quota: int
    active_kds: int
    kds_quota: int
    storage_mb: float
    storage_quota_mb: int
    uptime_sla: str


INITIAL_TENANTS_DATA: dict[str, dict[str, Any]] = {
    "artisan-coffee": {
        "tenant_id": str(new_uuid7()),
        "slug": "artisan-coffee",
        "legal_name": "Artisan Coffee Roasters",
        "home_region": "ap-south-1",
        "status": "ACTIVE",
        "tier": "ENTERPRISE",
        "subdomain": "artisan-coffee.nexus-qsr.io",
        "branch_name": "London SoHo Roastery",
        "currency": "GBP",
        "tax_identifier": "GB123456789",
        "kms_key_version": "kms-v4-envelope-aes256gcm",
        "created_at": int(time.time()) - (86400 * 30),
        "active_branches": 2,
        "active_stations": 4,
        "compliance_mode": "WORM_8YR_IMMUTABLE",
        "pci_dss_level": "PCI-DSS-4.0-SAQ-A",
        "audit_events": [
            {
                "id": "evt-art-1",
                "timestamp": int(time.time()) - (86400 * 10),
                "action": "TENANT_PROVISIONED",
                "actor": "system.cloud-init",
                "detail": "Cloud tenant cell provisioned in ap-south-1.",
            },
            {
                "id": "evt-art-2",
                "timestamp": int(time.time()) - 3600,
                "action": "KMS_ENVELOPE_VERIFIED",
                "actor": "security.envelope",
                "detail": "AES-256-GCM envelope cipher validated with AAD tenant binding.",
            },
        ],
    },
    "nexus-flagship-cafe": {
        "tenant_id": str(new_uuid7()),
        "slug": "nexus-flagship-cafe",
        "legal_name": "Nexus Flagship Roastery & Café",
        "home_region": "ap-south-1",
        "status": "ACTIVE",
        "tier": "ENTERPRISE",
        "subdomain": "nexus-flagship-cafe.nexus-qsr.io",
        "branch_name": "Flagship Café - Indiranagar",
        "currency": "INR",
        "tax_identifier": "29AAAAA0000A1Z5",
        "kms_key_version": "kms-v3-envelope-aes256gcm",
        "created_at": int(time.time()) - (86400 * 15),
        "active_branches": 3,
        "active_stations": 8,
        "compliance_mode": "WORM_8YR_IMMUTABLE",
        "pci_dss_level": "PCI-DSS-4.0-SAQ-A",
        "audit_events": [
            {
                "id": "evt-101",
                "timestamp": int(time.time()) - (86400 * 5),
                "action": "TENANT_PROVISIONED",
                "actor": "system.init",
                "detail": "Tenant root cell provisioned in ap-south-1.",
            },
        ],
    },
    "blue-mountain-espresso": {
        "tenant_id": str(new_uuid7()),
        "slug": "blue-mountain-espresso",
        "legal_name": "Blue Mountain Espresso Bar",
        "home_region": "ap-northeast-1",
        "status": "ACTIVE",
        "tier": "PRO",
        "subdomain": "blue-mountain.nexus-qsr.io",
        "branch_name": "Tokyo Shibuya Specialty Bar",
        "currency": "JPY",
        "tax_identifier": "JP987654321",
        "kms_key_version": "kms-v2-envelope-aes256gcm",
        "created_at": int(time.time()) - (86400 * 7),
        "active_branches": 1,
        "active_stations": 2,
        "compliance_mode": "WORM_8YR_IMMUTABLE",
        "pci_dss_level": "PCI-DSS-4.0-SAQ-A",
        "audit_events": [],
    },
}
