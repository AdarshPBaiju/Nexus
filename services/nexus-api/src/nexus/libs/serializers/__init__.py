"""
nexus.libs.serializers - Strict split input/output serializer architecture.
"""

from nexus.libs.serializers.base_input import BaseNexusInputSerializer
from nexus.libs.serializers.base_output import BaseNexusOutputSerializer
from nexus.libs.serializers.errors import (
    InvalidParameterDetail,
    RFC9457ProblemDetail,
)
from nexus.libs.serializers.renderers import OrjsonResponseRenderer
from nexus.libs.serializers.sentinels import UNSET, is_set

__all__ = [
    "UNSET",
    "BaseNexusInputSerializer",
    "BaseNexusOutputSerializer",
    "InvalidParameterDetail",
    "OrjsonResponseRenderer",
    "RFC9457ProblemDetail",
    "is_set",
]
