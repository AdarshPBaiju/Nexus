"""
nexus.engines.data_exchange.mapping.schema_mapper - Bidirectional dynamic schema mapper.
"""

from __future__ import annotations

from typing import Any, Mapping

from nexus.engines.data_exchange.mapping.ast_evaluator import SafeAstCaseEvaluator


class DataSchemaMapper:
    """Transforms raw input rows into target domain entity schemas."""

    @classmethod
    def transform_row(
        cls,
        raw_row: Mapping[str, Any],
        field_mappings: Mapping[str, str],
        ast_rules: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Transform single dictionary row using column renames and AST case rules."""
        result: dict[str, Any] = {}
        active_ast = ast_rules or {}

        for source_col, target_field in field_mappings.items():
            if source_col in raw_row:
                raw_val = raw_row[source_col]
                # Apply AST conditional rule if defined for this target field
                if target_field in active_ast:
                    rule_def = active_ast[target_field]
                    transformed_val = SafeAstCaseEvaluator.evaluate(
                        raw_val,
                        rules=rule_def.get("rules", []),
                        default_value=rule_def.get("default", raw_val),
                    )
                    result[target_field] = transformed_val
                else:
                    result[target_field] = raw_val

        return result
