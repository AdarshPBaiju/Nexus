"""
nexus.extensions.base.docs_basic.services.receipt_ast_compiler - Normalized receipt compiler.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class ReceiptVenueDto:
    name: str
    tax_id: str
    address: str
    phone: str


@dataclass(frozen=True)
class ReceiptMetadataDto:
    document_number: str
    order_token: str
    cashier_name: str
    issued_at: str


@dataclass(frozen=True)
class ReceiptLineItemDto:
    name: str
    quantity: Decimal
    unit_price: Decimal
    modifiers: list[str]
    line_total: Decimal


@dataclass(frozen=True)
class ReceiptTaxLineDto:
    rate_percent: Decimal
    taxable_amount: Decimal
    tax_amount: Decimal
    label: str


@dataclass(frozen=True)
class ReceiptTenderDto:
    tender_type: str
    tendered_amount: Decimal
    change_returned: Decimal


@dataclass(frozen=True)
class ReceiptTotalsDto:
    subtotal: Decimal
    discount: Decimal
    taxes: list[ReceiptTaxLineDto]
    grand_total: Decimal
    tenders: list[ReceiptTenderDto]


@dataclass(frozen=True)
class ReceiptCompilerInputDto:
    venue: ReceiptVenueDto
    metadata: ReceiptMetadataDto
    items: list[ReceiptLineItemDto]
    totals: ReceiptTotalsDto
    footer_text: dict[str, str]


@dataclass(frozen=True)
class CompiledReceiptAstDto:
    ast_payload: dict[str, Any]
    canonical_json: str
    sha256_hash: str
    qr_verification_url: str


class ReceiptAstCompiler:
    """
    Authoritative compiler transforming business orders into normalized JSON AST for thermal slips.
    """

    VERIFY_BASE_URL = "https://verify.nexus.internal/receipt"

    @classmethod
    def compile_ast(cls, payload: ReceiptCompilerInputDto) -> CompiledReceiptAstDto:
        ast_dict: dict[str, Any] = {
            "version": "1.0",
            "type": "RECEIPT_THERMAL",
            "header": cls._build_header(payload.venue),
            "metadata": cls._build_metadata(payload.metadata),
            "line_items": cls._build_line_items(payload.items),
            "totals": cls._build_totals(payload.totals),
            "footer": cls._build_footer(payload.footer_text),
        }
        canonical_str = json.dumps(ast_dict, sort_keys=True, separators=(",", ":"))
        sha256_digest = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
        qr_url = (
            f"{cls.VERIFY_BASE_URL}/{payload.metadata.document_number}/?sig={sha256_digest[:16]}"
        )
        ast_dict["footer"]["qr_payload"] = qr_url
        ast_dict["digest"] = sha256_digest
        return CompiledReceiptAstDto(
            ast_payload=ast_dict,
            canonical_json=canonical_str,
            sha256_hash=sha256_digest,
            qr_verification_url=qr_url,
        )

    @classmethod
    def _build_header(cls, venue: ReceiptVenueDto) -> dict[str, str]:
        return {
            "name": venue.name,
            "tax_id": venue.tax_id,
            "address": venue.address,
            "phone": venue.phone,
        }

    @classmethod
    def _build_metadata(cls, meta: ReceiptMetadataDto) -> dict[str, str]:
        return {
            "document_number": meta.document_number,
            "order_token": meta.order_token,
            "cashier_name": meta.cashier_name,
            "issued_at": meta.issued_at,
        }

    @classmethod
    def _build_line_items(cls, items: list[ReceiptLineItemDto]) -> list[dict[str, Any]]:
        return [
            {
                "name": item.name,
                "quantity": str(item.quantity),
                "unit_price": str(item.unit_price),
                "modifiers": item.modifiers,
                "line_total": str(item.line_total),
            }
            for item in items
        ]

    @classmethod
    def _build_totals(cls, totals: ReceiptTotalsDto) -> dict[str, Any]:
        return {
            "subtotal": str(totals.subtotal),
            "discount": str(totals.discount),
            "taxes": [
                {
                    "rate_percent": str(t.rate_percent),
                    "taxable_amount": str(t.taxable_amount),
                    "tax_amount": str(t.tax_amount),
                    "label": t.label,
                }
                for t in totals.taxes
            ],
            "grand_total": str(totals.grand_total),
            "tenders": [
                {
                    "type": td.tender_type,
                    "tendered": str(td.tendered_amount),
                    "change": str(td.change_returned),
                }
                for td in totals.tenders
            ],
        }

    @classmethod
    def _build_footer(cls, footer: dict[str, str]) -> dict[str, str]:
        return {
            "wifi": footer.get("wifi", ""),
            "notice": footer.get("notice", "Thank you for your visit!"),
            "qr_payload": "",
        }
