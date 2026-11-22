"""
nexus.engines.discounts.domain.condition_ast - Declarative condition AST evaluation engine.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any


class ConditionAstEvaluator:
    """
    Evaluates safe declarative condition trees without eval() or code injection.
    Supports comparison operators, set membership, and boolean combinators.
    """

    MAX_DEPTH = 8

    @classmethod
    def evaluate(cls, ast_node: dict[str, Any], context: dict[str, Any], depth: int = 0) -> bool:
        """Evaluates an AST node against the provided context dictionary."""
        if not ast_node or depth > cls.MAX_DEPTH:
            return True

        op = str(ast_node.get("op", "")).upper()
        if op == "AND":
            return cls._eval_and(ast_node.get("rules", []), context, depth + 1)
        if op == "OR":
            return cls._eval_or(ast_node.get("rules", []), context, depth + 1)
        if op == "NOT":
            return not cls.evaluate(ast_node.get("rule", {}), context, depth + 1)

        field = str(ast_node.get("field", ""))
        expected = ast_node.get("value")
        actual = context.get(field)
        return cls._eval_comparison(op, actual, expected)

    @classmethod
    def _eval_and(cls, rules: list[dict[str, Any]], context: dict[str, Any], depth: int) -> bool:
        return all(cls.evaluate(rule, context, depth) for rule in rules)

    @classmethod
    def _eval_or(cls, rules: list[dict[str, Any]], context: dict[str, Any], depth: int) -> bool:
        return any(cls.evaluate(rule, context, depth) for rule in rules)

    @classmethod
    def _eval_comparison(cls, op: str, actual: Any, expected: Any) -> bool:
        if actual is None:
            return False

        # Convert numerics to Decimal if applicable
        if isinstance(actual, (int, float, Decimal)) and isinstance(
            expected, (int, float, str, Decimal)
        ):
            try:
                actual = Decimal(str(actual))
                expected = Decimal(str(expected))
            except Exception:
                pass

        if op == "EQ":
            return actual == expected
        if op == "NEQ":
            return actual != expected
        if op == "GT":
            return actual > expected
        if op == "GTE":
            return actual >= expected
        if op == "LT":
            return actual < expected
        if op == "LTE":
            return actual <= expected
        if op == "IN":
            return actual in expected if isinstance(expected, (list, tuple, set)) else False
        if op == "CONTAINS":
            return expected in actual if isinstance(actual, (list, tuple, str)) else False
        return False
