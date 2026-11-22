"""
nexus.extensions.base.docs_basic.models.generated_document - Generated document record model.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from typing import Any, Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from nexus.libs.models.tenant_scoped import TenantScopedModel


@dataclass(frozen=True)
class RecordDocumentDto:
    """Parameter object for registering a generated document record."""

    tenant_id: uuid.UUID
    folio_id: uuid.UUID
    document_number: str
    document_type: str
    sha256_hash: str
    qr_verification_url: str
    ast_payload_json: dict[str, Any]
    storage_url: str = ""


class GeneratedDocumentRecord(TenantScopedModel):
    """
    Tamper-evident audit record of rendered fiscal receipts and invoices.
    """

    folio_id = models.UUIDField(
        db_index=True,
        help_text=_("Associated commercial folio or order identifier."),
    )
    document_number = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Fiscal sequential numbering series document code."),
    )
    document_type = models.CharField(
        max_length=32,
        db_index=True,
        help_text=_("Document format type (e.g. RECEIPT_THERMAL, INVOICE_TAX_A4)."),
    )
    sha256_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Cryptographic SHA-256 digest of normalized AST payload."),
    )
    qr_verification_url = models.CharField(
        max_length=255,
        help_text=_("Dynamic verification URL encoded into receipt QR code."),
    )
    ast_payload_json = models.JSONField(
        help_text=_("Full canonical structured AST representation of document."),
    )
    storage_url = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_("Object storage URI for archived PDF/A-3 or ESC/POS stream."),
    )

    class Meta:
        db_table = "docs_generated_document"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "folio_id"]),
            models.Index(fields=["tenant_id", "sha256_hash"]),
        ]
        unique_together = ("tenant_id", "document_number")

    @classmethod
    def record_document(cls, dto: RecordDocumentDto) -> Self:
        return cls.objects.create(
            tenant_id=dto.tenant_id,
            folio_id=dto.folio_id,
            document_number=dto.document_number,
            document_type=dto.document_type,
            sha256_hash=dto.sha256_hash,
            qr_verification_url=dto.qr_verification_url,
            ast_payload_json=dto.ast_payload_json,
            storage_url=dto.storage_url,
        )

    def verify_payload_integrity(self, canonical_bytes: bytes) -> bool:
        computed = hashlib.sha256(canonical_bytes).hexdigest()
        return computed == self.sha256_hash

    def __str__(self) -> str:
        return f"GeneratedDocumentRecord({self.document_number}, hash={self.sha256_hash[:8]})"
