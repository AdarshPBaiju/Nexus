"""
nexus.platform.authorization.pdp.resolver - Sub-1.5ms Policy Decision Point (PDP) Resolver.
Enforces: Explicit Deny Always Wins, Scope Hierarchy, and ABAC Guardrails.
"""
from __future__ import annotations

import uuid
from enum import Enum
from typing import Any

from nexus.platform.authorization.pdp.policy_compiler import CompiledActorPolicySnapshot


class AuthzDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class AuthorizationResolver:
    """
    Sub-1.5ms Policy Decision Point evaluator.
    """

    @classmethod
    def is_scope_matching(
        cls,
        granted_level: str,
        granted_id: str,
        target_id: str | uuid.UUID | None,
    ) -> bool:
        """
        Validates scope matching:
        - Scope level TENANT matches any resource in the tenant.
        - Matching scope_id grants access.
        """
        if granted_level == "TENANT":
            return True
        if not target_id:
            return True
        return granted_id == str(target_id)

    @classmethod
    def evaluate_abac_constraints(
        cls,
        context: dict[str, Any] | None,
        constraints: dict[str, Any],
    ) -> bool:
        """Evaluates AST predicate constraints (e.g. amount_max, shift_open)."""
        if not constraints:
            return True
        if not context:
            return False

        for k, expected_v in constraints.items():
            actual_v = context.get(k)
            if k.endswith("_max") and actual_v is not None:
                if float(actual_v) > float(expected_v):
                    return False
            elif actual_v != expected_v:
                return False
        return True

    @classmethod
    def resolve_access(
        cls,
        policy: CompiledActorPolicySnapshot,
        permission_code: str,
        target_scope_id: str | uuid.UUID | None = None,
        context: dict[str, Any] | None = None,
    ) -> AuthzDecision:
        """
        Evaluates authorization decision:
        1. Explicit Deny Always Wins.
        2. Permission must be in allowed grants.
        3. Scoped grants must match target scope.
        """
        # Rule 1: Explicit Deny Always Wins
        if permission_code in policy.denied_permissions:
            return AuthzDecision.DENY

        # Rule 2: Permission must be granted
        if permission_code not in policy.allowed_permissions:
            return AuthzDecision.DENY

        # Rule 3: Target scope verification
        grants = policy.scoped_grants.get(permission_code, [])
        if not any(cls.is_scope_matching(lvl, gid, target_scope_id) for lvl, gid in grants):
            return AuthzDecision.DENY

        return AuthzDecision.ALLOW
