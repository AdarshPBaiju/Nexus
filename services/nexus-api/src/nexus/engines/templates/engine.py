"""
nexus.engines.templates.engine - Universal SSTI-Proof Template Engine.
"""
from __future__ import annotations

from typing import Any

from nexus.engines.templates.ast.evaluator import SandboxedContextEvaluator
from nexus.engines.templates.ast.nodes import ASTNode
from nexus.engines.templates.compilers.registry import TemplateCompilerRegistry


class UniversalTemplateEngine:
    """
    Single unified template compilation engine across all 13 physical and digital targets.
    Guarantees zero SSTI, zero eval(), and strict resource boundaries.
    """

    @classmethod
    def render(
        cls,
        ast_root: ASTNode,
        target: str,
        context: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """
        Evaluates template AST against context and compiles to specified target artifact.
        """
        evaluated_nodes = SandboxedContextEvaluator.evaluate_node(ast_root, context)
        evaluated_root = evaluated_nodes[0] if evaluated_nodes else ast_root

        compiler = TemplateCompilerRegistry.get(target)
        if not compiler:
            raise ValueError(f"Unsupported template target: {target}")

        return compiler.compile(evaluated_root, metadata)
