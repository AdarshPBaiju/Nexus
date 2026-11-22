"""
nexus.engines.templates.ast.evaluator - Sandboxed Zero-Eval Context Evaluator.
"""
from __future__ import annotations

import re
from typing import Any

from nexus.engines.templates.ast.nodes import ASTNode, ASTNodeType


class TemplateSecurityError(ValueError):
    """Raised when AST evaluation violates sandboxing or complexity bounds."""


class SandboxedContextEvaluator:
    """
    Evaluates variable bindings and loops securely without eval() or Jinja2.
    """

    MAX_RECURSION_DEPTH = 8
    MAX_LOOP_ITERATIONS = 5000
    FORBIDDEN_IDENTIFIERS = frozenset([
        "__", "eval", "exec", "globals", "locals", "import", "builtins",
        "mro", "subclasses", "class", "base",
    ])

    @classmethod
    def resolve_binding(cls, binding: str, context: dict[str, Any]) -> Any:
        """Navigates dot-notated paths safely against dictionary contexts."""
        if not binding:
            return ""
        cls._validate_binding_security(binding)

        parts = binding.split(".")
        current: Any = context
        for part in parts:
            if current is None or not isinstance(current, dict):
                return ""
            current = current.get(part)
        return current if current is not None else ""

    @classmethod
    def _validate_binding_security(cls, binding: str) -> None:
        binding_lower = binding.lower()
        for forbidden in cls.FORBIDDEN_IDENTIFIERS:
            if forbidden in binding_lower:
                raise TemplateSecurityError(f"Security violation: forbidden token '{forbidden}'")

    @classmethod
    def evaluate_text(cls, text: str, context: dict[str, Any]) -> str:
        """Replaces {{ variable.path }} placeholders using safe dot navigation."""
        pattern = re.compile(r"\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}")

        def replace(match: re.Match[str]) -> str:
            val = cls.resolve_binding(match.group(1), context)
            return str(val)

        return pattern.sub(replace, text)

    @classmethod
    def evaluate_node(
        cls,
        node: ASTNode,
        context: dict[str, Any],
        depth: int = 0,
    ) -> list[ASTNode]:
        """Evaluates ASTNode recursively respecting depth and iteration bounds."""
        if depth > cls.MAX_RECURSION_DEPTH:
            raise TemplateSecurityError("Recursion depth limit exceeded (max 8 levels)")

        if node.node_type == ASTNodeType.TEXT:
            resolved_content = cls.evaluate_text(node.content, context)
            return [ASTNode(node.node_type, resolved_content, node.binding, [], node.attributes)]

        if node.node_type == ASTNodeType.CONDITION:
            return cls._evaluate_condition(node, context, depth)

        if node.node_type == ASTNodeType.LOOP:
            return cls._evaluate_loop(node, context, depth)

        evaluated_children: list[ASTNode] = []
        for child in node.children:
            evaluated_children.extend(cls.evaluate_node(child, context, depth + 1))

        return [ASTNode(node.node_type, node.content, node.binding, evaluated_children, node.attributes)]

    @classmethod
    def _evaluate_condition(
        cls,
        node: ASTNode,
        context: dict[str, Any],
        depth: int,
    ) -> list[ASTNode]:
        cond_val = cls.resolve_binding(node.binding, context)
        if not cond_val:
            return []
        res: list[ASTNode] = []
        for child in node.children:
            res.extend(cls.evaluate_node(child, context, depth + 1))
        return res

    @classmethod
    def _evaluate_loop(
        cls,
        node: ASTNode,
        context: dict[str, Any],
        depth: int,
    ) -> list[ASTNode]:
        items = cls.resolve_binding(node.binding, context)
        if not isinstance(items, list):
            return []

        if len(items) > cls.MAX_LOOP_ITERATIONS:
            raise TemplateSecurityError("Loop iteration ceiling exceeded (max 5000)")

        var_name = node.attributes.get("as", "item")
        res: list[ASTNode] = []
        for item in items:
            scoped_ctx = {**context, var_name: item}
            for child in node.children:
                res.extend(cls.evaluate_node(child, scoped_ctx, depth + 1))
        return res
