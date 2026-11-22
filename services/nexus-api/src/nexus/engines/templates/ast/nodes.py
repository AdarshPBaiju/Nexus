"""
nexus.engines.templates.ast.nodes - Sandboxed Template AST Node Specifications.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ASTNodeType:
    """Canonical AST Node Types."""

    DOCUMENT = "document"
    SECTION = "section"
    PARAGRAPH = "paragraph"
    TEXT = "text"
    TABLE = "table"
    LOOP = "loop"
    CONDITION = "condition"
    BARCODE = "barcode"
    QR_CODE = "qr_code"
    SIGNATURE = "signature"


@dataclass(frozen=True)
class ASTNode:
    """Immutable Sandboxed AST Node."""

    node_type: str
    content: str = ""
    binding: str = ""
    children: list[ASTNode] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
