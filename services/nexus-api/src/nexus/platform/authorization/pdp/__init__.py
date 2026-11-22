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
from nexus.platform.authorization.pdp.simulator import (
    AccessSimulationReport,
    AccessSimulator,
    SimulationTraceStep,
)

__all__ = [
    "AccessSimulationReport",
    "AccessSimulator",
    "AuthorizationResolver",
    "AuthzDecision",
    "CompiledActorPolicySnapshot",
    "EffectivePolicyCompiler",
    "FieldSecurityProjector",
    "LiveRevocationManager",
    "SimulationTraceStep",
]
