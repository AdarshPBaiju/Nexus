"""
nexus.platform.authorization.pdp.fls - Field-Level Security (FLS) Projector.
Applies column-level classifications (READ, MASKED, WRITE, HIDDEN).
"""
from __future__ import annotations

import copy
from typing import Any

from nexus.platform.authorization.pdp.policy_compiler import CompiledActorPolicySnapshot


class FieldSecurityProjector:
    """
    Projector applying column-level security classifications to record payloads.
    """

    @classmethod
    def mask_value(cls, val: Any) -> str:
        """Applies masking pattern to sensitive value (e.g. ****1234 or ***)."""
        s = str(val)
        if len(s) <= 4:
            return "****"
        return f"{'*' * (len(s) - 4)}{s[-4:]}"

    @classmethod
    def project_payload(
        cls,
        entity_type: str,
        data: dict[str, Any],
        policy: CompiledActorPolicySnapshot,
    ) -> dict[str, Any]:
        """
        Redacts HIDDEN fields and masks MASKED fields according to policy FLS rules.
        """
        result = copy.deepcopy(data)
        for field_name in list(result.keys()):
            rule_key = f"{entity_type}:{field_name}"
            classification = policy.fls_rules.get(rule_key, "READ")

            if classification == "HIDDEN":
                result.pop(field_name, None)
            elif classification == "MASKED" and result[field_name] is not None:
                result[field_name] = cls.mask_value(result[field_name])

        return result
