"""
nexus.engines.templates.compilers.base - Base Target Compiler Protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from nexus.engines.templates.ast.nodes import ASTNode


class BaseTargetCompiler(ABC):
    """
    Abstract compiler compiling a evaluated AST into a specific output format.
    """

    @property
    @abstractmethod
    def target_name(self) -> str:
        """Target identifier (e.g. EMAIL_MJML, THERMAL_ESCPOS, A4_PDF)."""
        pass

    @abstractmethod
    def compile(self, root: ASTNode, metadata: dict[str, Any] | None = None) -> Any:
        """Compiles evaluated AST root node into the target artifact representation."""
        pass

    @classmethod
    def collect_text(cls, node: ASTNode) -> str:
        """Helper extracting recursive plain text from AST."""
        if node.content:
            return node.content
        return " ".join(
            [cls.collect_text(child) for child in node.children if cls.collect_text(child)]
        )
