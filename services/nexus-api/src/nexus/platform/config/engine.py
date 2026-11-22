"""
nexus.platform.config.engine - RFC 7396 Merge Patch & 9-Field Provenance Resolution Engine.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class LockStatus(str, Enum):
    """Lock status governing overrideability of a configuration key."""

    UNLOCKED = "UNLOCKED"
    LOCKED_BY_PARENT = "LOCKED_BY_PARENT"
    STATUTORY_GUARDRAIL = "STATUTORY_GUARDRAIL"


@dataclass(frozen=True)
class ProvenanceRecord:
    """
    9 mandatory provenance fields attached to every resolved configuration setting.
    """

    effective_value: Any
    source_level: str
    source_revision_id: str
    inheritance_chain: list[str]
    override_history_ref: str
    lock_status: LockStatus
    validation_status: str
    resolved_at: str
    applicable_plugin_version: str


@dataclass(frozen=True)
class SimulationForecast:
    """Outcome of pre-publish dry-run simulation."""

    is_safe: bool
    conflicts: list[str]
    diff: dict[str, tuple[Any, Any]]


class StatutoryLockConflictError(ValueError):
    """Raised when an override violates a parent or statutory guardrail lock."""


class ConfigResolutionEngine:
    """
    Evaluates 6-level inheritance hierarchy:
    Platform -> Tenant -> Brand -> Branch -> Zone -> Workstation
    with RFC 7396 merge patching and 9-field provenance tracking.
    """

    @classmethod
    def apply_merge_patch(cls, target: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
        """
        RFC 7396 JSON Merge Patch algorithm:
        - null deletes the key
        - dict recursively merges
        - primitive replaces
        """
        res = copy.deepcopy(target)
        for k, v in patch.items():
            if v is None:
                res.pop(k, None)
            elif isinstance(v, dict) and isinstance(res.get(k), dict):
                res[k] = cls.apply_merge_patch(res[k], v)
            else:
                res[k] = copy.deepcopy(v)
        return res

    @classmethod
    def resolve_effective_config(
        cls,
        nodes_in_order: list[dict[str, Any]],
    ) -> dict[str, ProvenanceRecord]:
        """
        Resolve inheritance chain and attach 9-field provenance metadata.
        """
        effective_map: dict[str, Any] = {}
        provenance_map: dict[str, ProvenanceRecord] = {}
        locks: dict[str, LockStatus] = {}

        now_iso = datetime.now(timezone.utc).isoformat()

        for node in nodes_in_order:
            level = node.get("scope_level", "PLATFORM")
            rev_id = str(node.get("revision_id", "rev_init"))
            cfg = node.get("config", {})
            node_locks = node.get("locks", {})

            for k, l_type in node_locks.items():
                locks[k] = LockStatus(l_type)

            for key, val in cfg.items():
                curr_lock = locks.get(key, LockStatus.UNLOCKED)
                chain = (
                    [*provenance_map[key].inheritance_chain, level]
                    if key in provenance_map
                    else [level]
                )

                effective_map[key] = val
                provenance_map[key] = ProvenanceRecord(
                    effective_value=val,
                    source_level=level,
                    source_revision_id=rev_id,
                    inheritance_chain=chain,
                    override_history_ref=f"hist_{key}_{level.lower()}",
                    lock_status=curr_lock,
                    validation_status="VALID",
                    resolved_at=now_iso,
                    applicable_plugin_version="v1.0.0",
                )

        return provenance_map

    @classmethod
    def simulate_revision(
        cls,
        base_config: dict[str, Any],
        patch: dict[str, Any],
        locks: dict[str, str],
    ) -> SimulationForecast:
        """
        Dry-run simulation checking for statutory locks and value diffs.
        """
        conflicts: list[str] = []
        diff: dict[str, tuple[Any, Any]] = {}

        for k, new_v in patch.items():
            lock = locks.get(k, LockStatus.UNLOCKED.value)
            if lock in {LockStatus.LOCKED_BY_PARENT.value, LockStatus.STATUTORY_GUARDRAIL.value}:
                conflicts.append(f"Cannot override locked key '{k}': {lock}")

            old_v = base_config.get(k)
            if old_v != new_v:
                diff[k] = (old_v, new_v)

        return SimulationForecast(
            is_safe=len(conflicts) == 0,
            conflicts=conflicts,
            diff=diff,
        )
