"""
nexus.libs.field_control.contract - Declarative ViewFieldContract for ask-only projection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class ViewFieldContract:
    """Defines field dependencies, relational join paths, and allowed projection keys."""

    model_label: str
    allowed_fields: tuple[str, ...]
    field_dependencies: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    relation_paths: Mapping[str, str] = field(default_factory=dict)
    mandatory_columns: tuple[str, ...] = ("id", "tenant_id")

    def resolve_sql_columns(self, requested_fields: Sequence[str]) -> set[str]:
        """Expand requested fields into actual physical SQL columns via dependencies."""
        resolved: set[str] = set(self.mandatory_columns)
        for req in requested_fields:
            if req not in self.allowed_fields:
                continue
            deps = self.field_dependencies.get(req)
            if deps:
                resolved.update(deps)
            else:
                resolved.add(req)
        return resolved

    def resolve_relations(self, requested_fields: Sequence[str]) -> set[str]:
        """Dynamically identify strictly necessary relational joins."""
        needed_joins: set[str] = set()
        for req in requested_fields:
            rel_path = self.relation_paths.get(req)
            if rel_path:
                needed_joins.add(rel_path)
        return needed_joins

    def apply_to_queryset(self, queryset: Any, requested_fields: Sequence[str]) -> Any:
        """Apply .only() column projection and .select_related() strictly for asked fields."""
        sql_cols = self.resolve_sql_columns(requested_fields)
        relations = self.resolve_relations(requested_fields)

        qs = queryset
        if relations:
            qs = qs.select_related(*relations)
        return qs.only(*sql_cols)
