"""
nexus.engines.data_exchange.mapping.ast_evaluator - Sandboxed AST conditional evaluator.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence


class SafeAstCaseEvaluator:
    """Evaluates conditional value mappings safely without eval()."""

    @classmethod
    def evaluate(
        cls,
        value: Any,
        rules: Sequence[Mapping[str, Any]],
        default_value: Any = None,
    ) -> Any:
        """
        Evaluate value against sequential conditional rules:
        Each rule has:
          {"operator": "eq" | "neq" | "in" | "gt" | "lt", "operand": ..., "target": ...}
        """
        for rule in rules:
            op = rule.get("operator", "eq")
            operand = rule.get("operand")
            target = rule.get("target")

            if cls._matches(value, op, operand):
                return target

        return default_value

    @staticmethod
    def _matches(value: Any, op: str, operand: Any) -> bool:
        if op == "eq":
            return value == operand
        if op == "neq":
            return value != operand
        if op == "in" and isinstance(operand, (list, tuple, set)):
            return value in operand
        if op == "gt" and value is not None and operand is not None:
            return float(value) > float(operand)
        if op == "lt" and value is not None and operand is not None:
            return float(value) < float(operand)
        return False
