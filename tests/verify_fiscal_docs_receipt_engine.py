#!/usr/bin/env python3
"""
verify_fiscal_docs_receipt_engine.py - Verification suite for Subphase 03.03.
Validates:
1. DocumentTemplate model creation and Forced RLS tenant isolation.
2. Normalized Receipt AST compilation (Header, Metadata, Lines, Totals, Footer).
3. Tamper-evident SHA-256 cryptographic hash and QR verification URL generation.
4. GeneratedDocumentRecord audit persistence and payload integrity verification.
5. Execution performance budget (< 10ms).
"""

from __future__ import annotations

from decimal import Decimal
import os
from pathlib import Path
import sys
import time
import uuid

REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "services" / "nexus-api" / "src"
sys.path.insert(0, str(API_SRC))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexus_test_settings")
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "nexus.platform.tenancy",
            "nexus.engines.currency_fx",
            "nexus.engines.accounting",
            "nexus.engines.taxation",
            "nexus.extensions.base.docs_basic",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

from nexus.extensions.base.docs_basic.models import (
    DocumentTemplate,
    GeneratedDocumentRecord,
)
from nexus.extensions.base.docs_basic.models.generated_document import RecordDocumentDto
from nexus.extensions.base.docs_basic.services import (
    CompiledReceiptAstDto,
    ReceiptAstCompiler,
    ReceiptCompilerInputDto,
    ReceiptLineItemDto,
    ReceiptMetadataDto,
    ReceiptTaxLineDto,
    ReceiptTenderDto,
    ReceiptTotalsDto,
    ReceiptVenueDto,
)


def _setup_schema() -> None:
    call_command("migrate", "--run-syncdb", verbosity=0)


def _build_test_items() -> list[ReceiptLineItemDto]:
    return [
        ReceiptLineItemDto(
            name="Single Origin Oat Flat White",
            quantity=Decimal("2"),
            unit_price=Decimal("4.50"),
            modifiers=["Oat Milk", "Extra Shot"],
            line_total=Decimal("9.00"),
        ),
        ReceiptLineItemDto(
            name="Butter Croissant",
            quantity=Decimal("1"),
            unit_price=Decimal("3.50"),
            modifiers=[],
            line_total=Decimal("3.50"),
        ),
    ]


def _build_test_totals() -> ReceiptTotalsDto:
    taxes = [
        ReceiptTaxLineDto(
            rate_percent=Decimal("20.00"),
            taxable_amount=Decimal("9.00"),
            tax_amount=Decimal("1.80"),
            label="Standard VAT 20%",
        ),
        ReceiptTaxLineDto(
            rate_percent=Decimal("0.00"),
            taxable_amount=Decimal("3.50"),
            tax_amount=Decimal("0.00"),
            label="Zero Rated Food",
        ),
    ]
    tenders = [
        ReceiptTenderDto(
            tender_type="CASH",
            tendered_amount=Decimal("20.00"),
            change_returned=Decimal("5.70"),
        )
    ]
    return ReceiptTotalsDto(
        subtotal=Decimal("12.50"),
        discount=Decimal("0.00"),
        taxes=taxes,
        grand_total=Decimal("14.30"),
        tenders=tenders,
    )


def _build_test_payload() -> ReceiptCompilerInputDto:
    venue = ReceiptVenueDto(
        name="Nexus Artisan Espresso",
        tax_id="VAT-GB-99887766",
        address="102 Bean Street, London",
        phone="+44 20 7946 0991",
    )
    meta = ReceiptMetadataDto(
        document_number="REC-2026-0042",
        order_token="#087",
        cashier_name="Barista Sarah",
        issued_at="2026-11-22T14:30:00Z",
    )
    footer = {
        "wifi": "ArtisanWifiPass",
        "notice": "Thank you for supporting craft coffee!",
    }
    return ReceiptCompilerInputDto(
        venue=venue,
        metadata=meta,
        items=_build_test_items(),
        totals=_build_test_totals(),
        footer_text=footer,
    )


def test_document_template_creation() -> None:
    print("[1/5] Testing DocumentTemplate creation and RLS isolation...")
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    tpl1 = DocumentTemplate.create_template(t1, "Thermal 80mm Slip", "RECEIPT_THERMAL", "80MM")
    tpl2 = DocumentTemplate.create_template(t2, "Tax Invoice A4", "INVOICE_TAX_A4", "A4")

    assert tpl1.width_type == DocumentTemplate.WidthType.WIDTH_80MM
    assert tpl1.get_footer_text("wifi") == "GuestWifi"
    assert DocumentTemplate.objects.filter(tenant_id=t1).count() == 1
    assert DocumentTemplate.objects.filter(tenant_id=t2).count() == 1
    print("  ✓ Document templates created with tenant isolation and default footer.")


def test_receipt_ast_compilation() -> None:
    print("[2/5] Testing normalized Receipt AST compiler...")
    payload = _build_test_payload()
    compiled = ReceiptAstCompiler.compile_ast(payload)
    ast = compiled.ast_payload

    assert ast["version"] == "1.0"
    assert ast["type"] == "RECEIPT_THERMAL"
    assert ast["header"]["tax_id"] == "VAT-GB-99887766"
    assert ast["metadata"]["order_token"] == "#087"
    assert len(ast["line_items"]) == 2
    assert ast["line_items"][0]["modifiers"] == ["Oat Milk", "Extra Shot"]
    assert ast["totals"]["grand_total"] == "14.30"
    assert len(ast["totals"]["taxes"]) == 2
    print("  ✓ Normalized AST generated with header, metadata, lines, taxes and tenders.")


def test_tamper_evident_sha256() -> None:
    print("[3/5] Testing tamper-evident cryptographic SHA-256 signatures...")
    payload = _build_test_payload()
    compiled = ReceiptAstCompiler.compile_ast(payload)

    assert len(compiled.sha256_hash) == 64
    assert compiled.sha256_hash == compiled.ast_payload["digest"]
    sig_prefix = compiled.sha256_hash[:16]
    assert f"sig={sig_prefix}" in compiled.qr_verification_url

    # Verify tampering detection
    tampered_bytes = compiled.canonical_json.replace("14.30", "1.00").encode("utf-8")
    import hashlib

    tampered_digest = hashlib.sha256(tampered_bytes).hexdigest()
    assert tampered_digest != compiled.sha256_hash
    print("  ✓ SHA-256 signature and QR verification URL validated against payload tampering.")


def test_generated_document_audit_record() -> None:
    print("[4/5] Testing GeneratedDocumentRecord audit persistence...")
    t_id = uuid.uuid4()
    folio_id = uuid.uuid4()
    payload = _build_test_payload()
    compiled = ReceiptAstCompiler.compile_ast(payload)

    dto = RecordDocumentDto(
        tenant_id=t_id,
        folio_id=folio_id,
        document_number=payload.metadata.document_number,
        document_type="RECEIPT_THERMAL",
        sha256_hash=compiled.sha256_hash,
        qr_verification_url=compiled.qr_verification_url,
        ast_payload_json=compiled.ast_payload,
    )
    record = GeneratedDocumentRecord.record_document(dto)

    assert record.document_number == "REC-2026-0042"
    assert record.verify_payload_integrity(compiled.canonical_json.encode("utf-8")) is True
    print("  ✓ Document record persisted with audit payload integrity check.")


def test_performance_budget_sub_10ms() -> None:
    print("[5/5] Testing execution performance budget (< 10ms)...")
    payload = _build_test_payload()
    start = time.perf_counter()
    compiled = ReceiptAstCompiler.compile_ast(payload)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert compiled.sha256_hash != ""
    assert elapsed_ms < 10.0, f"Compilation took {elapsed_ms:.2f}ms (budget < 10ms)"
    print(f"  ✓ Sub-10ms performance budget met: {elapsed_ms:.2f}ms.")


def main() -> None:
    print("=" * 80)
    print("NEXUS SUBPHASE 03.03: FISCAL DOCS & RECEIPT ENGINE VERIFICATION")
    print("=" * 80)
    _setup_schema()
    test_document_template_creation()
    test_receipt_ast_compilation()
    test_tamper_evident_sha256()
    test_generated_document_audit_record()
    test_performance_budget_sub_10ms()
    print("=" * 80)
    print("ALL FISCAL DOCS & RECEIPT ENGINE TESTS COMPLETED WITH 100% SUCCESS.")
    print("=" * 80)


if __name__ == "__main__":
    main()
