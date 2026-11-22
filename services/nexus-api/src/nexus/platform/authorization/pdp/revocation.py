"""
nexus.platform.authorization.pdp.revocation - Sub-Second Live Authorization Revocation.
"""

from __future__ import annotations

import uuid
from typing import Any

from nexus.libs.ids import new_uuid7
from nexus.platform.authorization.pdp.policy_compiler import EffectivePolicyCompiler


class LiveRevocationManager:
    """
    Coordinates atomic bumping of RBAC version and event broadcasts.
    """

    @classmethod
    def bump_tenant_rbac_version(
        cls,
        tenant_id: uuid.UUID,
        new_version: int,
    ) -> dict[str, Any]:
        """
        Evicts process memory cache and creates CloudEvent rbac.version.bumped.v1.
        """
        EffectivePolicyCompiler.evict_tenant(tenant_id)
        return {
            "specversion": "1.0",
            "id": str(new_uuid7()),
            "type": "rbac.version.bumped.v1",
            "source": f"/tenants/{tenant_id}/authz",
            "datacontenttype": "application/json",
            "data": {
                "tenant_id": str(tenant_id),
                "new_version": new_version,
            },
        }
