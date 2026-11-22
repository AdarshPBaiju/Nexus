"""
nexus.platform.authorization.pdp - Re-exports for Policy Decision Point primitives.
"""
from nexus.platform.authorization.pdp.fls import FieldSecurityProjector
from nexus.platform.authorization.pdp.policy_compiler import (
    CompiledActorPolicySnapshot,
    EffectivePolicyCompiler,
)
from nexus.platform.authorization.pdp.resolver import AuthorizationResolver, AuthzDecision
from nexus.platform.authorization.pdp.revocation import LiveRevocationManager

__all__ = [
    "AuthorizationResolver",
    "AuthzDecision",
    "CompiledActorPolicySnapshot",
    "EffectivePolicyCompiler",
    "FieldSecurityProjector",
    "LiveRevocationManager",
]
