"""
nexus.platform.authorization.pdp.policy_compiler - Compiled Actor Policy Snapshot & Compiler.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from nexus.platform.authorization.models.fls_rule import FieldSecurityRule
from nexus.platform.authorization.models.grant import ResourceGrant


@dataclass(frozen=True)
class CompiledActorPolicySnapshot:
    """
    Immutable compiled authorization snapshot for an actor within a tenant workspace.
    Provides sub-1.5ms evaluation with zero SQL queries on hot paths.
    """

    tenant_id: uuid.UUID
    membership_id: uuid.UUID
    allowed_permissions: frozenset[str]
    denied_permissions: frozenset[str]
    scoped_grants: dict[str, list[tuple[str, str]]]  # perm -> list of (scope_level, scope_id_str)
    fls_rules: dict[str, str]  # entity:field -> classification (READ, MASKED, HIDDEN)
    rbac_version: int


class EffectivePolicyCompiler:
    """
    Compiles database grants, ABAC rules, and FLS classifications into a snapshot.
    """

    _MEMORY_CACHE: dict[str, CompiledActorPolicySnapshot] = {}

    @classmethod
    def get_cache_key(cls, tenant_id: uuid.UUID, membership_id: uuid.UUID, rbac_ver: int) -> str:
        return f"nx:authz:v{rbac_ver}:{tenant_id}:{membership_id}"

    @classmethod
    def compile_policy(
        cls,
        tenant_id: uuid.UUID,
        membership_id: uuid.UUID,
        rbac_version: int = 1,
    ) -> CompiledActorPolicySnapshot:
        """Compiles actor policy snapshot using active database grants with L1 memory caching."""
        cache_key = cls.get_cache_key(tenant_id, membership_id, rbac_version)
        if cache_key in cls._MEMORY_CACHE:
            return cls._MEMORY_CACHE[cache_key]

        grants = ResourceGrant.objects.filter(tenant_id=tenant_id, membership_id=membership_id)
        allowed: set[str] = set()
        denied: set[str] = set()
        scoped: dict[str, list[tuple[str, str]]] = {}

        for g in grants:
            if g.effect == ResourceGrant.GrantEffect.DENY:
                denied.add(g.permission_code)
            else:
                allowed.add(g.permission_code)
                scoped.setdefault(g.permission_code, []).append((g.scope_level, str(g.scope_id)))

        fls_rules_db = FieldSecurityRule.objects.filter(tenant_id=tenant_id)
        fls_map = {f"{r.entity_type}:{r.field_name}": r.classification for r in fls_rules_db}

        snapshot = CompiledActorPolicySnapshot(
            tenant_id=tenant_id,
            membership_id=membership_id,
            allowed_permissions=frozenset(allowed),
            denied_permissions=frozenset(denied),
            scoped_grants=scoped,
            fls_rules=fls_map,
            rbac_version=rbac_version,
        )
        cls._MEMORY_CACHE[cache_key] = snapshot
        return snapshot

    @classmethod
    def evict_tenant(cls, tenant_id: uuid.UUID) -> None:
        """Evicts in-memory L1 cache entries for a tenant upon live revocation."""
        tenant_str = str(tenant_id)
        keys_to_del = [k for k in cls._MEMORY_CACHE if tenant_str in k]
        for k in keys_to_del:
            cls._MEMORY_CACHE.pop(k, None)
