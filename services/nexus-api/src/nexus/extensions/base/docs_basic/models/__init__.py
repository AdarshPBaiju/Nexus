"""
nexus.extensions.base.docs_basic.models - Domain models barrel export.
"""

from __future__ import annotations

from nexus.extensions.base.docs_basic.models.document_template import (
    DocumentTemplate,
)
from nexus.extensions.base.docs_basic.models.generated_document import (
    GeneratedDocumentRecord,
)

__all__ = [
    "DocumentTemplate",
    "GeneratedDocumentRecord",
]
