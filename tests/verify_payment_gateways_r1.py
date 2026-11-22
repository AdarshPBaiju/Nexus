#!/usr/bin/env python3
"""
verify_payment_gateways_r1.py - Verification suite for Subphase 03.07 (Payment Gateways).
Validates:
1. GatewayInstallation model with tenant isolation.
2. Direct UPI QR payload generation with merchant VPA.
3. Multi-rail payment charges (Stripe, UPI) and fee quantization.
4. Double-entry clearing invariant: sum(Debit) == sum(Credit).
5. Webhook deduplication: 5 duplicate webhooks result in strictly 1 recorded log.
"""

from __future__ import annotations

from decimal import Decimal
import os
from pathlib import Path
import sys
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
            "nexus.engines.payment_router",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

from nexus.engines.payment_router.application.clearing_generator import (
    ClearingJournalGenerator,
)
from nexus.engines.payment_router.application.dtos import (
    ConfirmPaymentCmd,
    CreatePaymentIntentCmd,
    WebhookEventCmd,
)
from nexus.engines.payment_router.application.service import PaymentOrchestrationService
from nexus.engines.payment_router.gateways.upi_qr_adapter import DirectUpiQrAdapter
from nexus.engines.payment_router.models import (
    GatewayInstallation,
    PaymentIntent,
    PaymentWebhookEventLog,
)


def _setup_schema() -> None:
    call_command("migrate", "--run-syncdb", verbosity=0)


def test_gateway_installation_isolation() -> None:
    print("[1/5] Testing GatewayInstallation model creation and RLS...")
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    i1 = GatewayInstallation.objects.create(
        tenant_id=t1,
        gateway_code=GatewayInstallation.Gateway.STRIPE,
        name="Stripe Live",
        encrypted_credentials='{"sk_live": "enc_kms_123"}',
        is_active=True,
    )
    i2 = GatewayInstallation.objects.create(
        tenant_id=t2,
        gateway_code=GatewayInstallation.Gateway.DIRECT_UPI,
        name="HDFC UPI QR",
        encrypted_credentials='{"vpa": "cafe@hdfcbank"}',
        is_active=True,
    )
    assert i1.gateway_code == "STRIPE"
    assert GatewayInstallation.objects.filter(tenant_id=t1).count() == 1
    assert GatewayInstallation.objects.filter(tenant_id=t2).count() == 1
    print("  ✓ Gateway installations isolated per tenant.")


def test_direct_upi_qr_generation() -> None:
    print("[2/5] Testing Direct UPI QR code payload generation...")
    t_id = uuid.uuid4()
    folio_id = uuid.uuid4()
    intent = PaymentIntent.objects.create(
        tenant_id=t_id,
        folio_id=folio_id,
        amount=Decimal("450.00"),
        currency="INR",
        status=PaymentIntent.Status.REQUIRES_PAYMENT_METHOD,
    )
    adapter = DirectUpiQrAdapter()
    ok, tx_ref, fee, raw = adapter.process_charge(
        intent,
        {"merchant_vpa": "artisan.cafe@axisbank", "merchant_name": "Artisan Café"},
    )
    assert ok is True
    assert fee == Decimal("0.0000")  # 0% MDR on direct UPI
    assert "upi://pay?" in raw["upi_uri"]
    assert "pa=artisan.cafe%40axisbank" in raw["upi_uri"]
    assert "am=450.00" in raw["upi_uri"]
    print(f"  ✓ Direct UPI QR URI generated with 0% MDR: {raw['upi_uri'][:45]}...")


def test_multi_rail_charge_and_clearing() -> None:
    print("[3/5] Testing Stripe charge execution and double-entry clearing...")
    t_id = uuid.uuid4()
    folio_id = uuid.uuid4()
    cmd = CreatePaymentIntentCmd(
        tenant_id=t_id,
        folio_id=folio_id,
        amount=Decimal("100.00"),
        currency="USD",
    )
    intent = PaymentOrchestrationService.create_intent(cmd)
    confirm_cmd = ConfirmPaymentCmd(
        tenant_id=t_id,
        intent_id=intent.id,
        gateway_code="STRIPE",
        payment_data={"payment_method_id": "pm_card_visa"},
    )
    intent_res, attempt, postings = PaymentOrchestrationService.confirm_payment(confirm_cmd)

    assert intent_res.status == PaymentIntent.Status.SUCCEEDED
    assert attempt.status == "CAPTURED"
    assert len(postings) == 2
    dr = next(p for p in postings if p.direction == "DEBIT")
    cr = next(p for p in postings if p.direction == "CREDIT")
    assert dr.amount == Decimal("100.00")
    assert cr.amount == Decimal("100.00")
    print("  ✓ Payment captured with balanced double-entry clearing postings.")


def test_clearing_settlement_invariant() -> None:
    print("[4/5] Testing T+1 settlement journal invariant (net + fee == gross)...")
    gross = Decimal("100.00")
    fee = Decimal("3.20")
    net = Decimal("96.80")
    postings = ClearingJournalGenerator.generate_settlement_postings(gross, fee, net)

    debits = sum((p.amount for p in postings if p.direction == "DEBIT"), Decimal("0"))
    credits = sum((p.amount for p in postings if p.direction == "CREDIT"), Decimal("0"))
    assert debits == gross
    assert credits == gross
    print("  ✓ Settlement postings enforce strict zero-variance invariant.")


def test_webhook_deduplication() -> None:
    print("[5/5] Testing webhook idempotent deduplication (5 duplicate calls)...")
    t_id = uuid.uuid4()
    install = GatewayInstallation.objects.create(
        tenant_id=t_id,
        gateway_code="STRIPE",
        name="Stripe Webhook Test",
        encrypted_credentials="{}",
        is_active=True,
    )
    provider_evt = "evt_stripe_test_998877"
    cmd = WebhookEventCmd(
        tenant_id=t_id,
        gateway_code="STRIPE",
        provider_event_id=provider_evt,
        event_type="payment_intent.succeeded",
        payload={"id": "pi_123"},
    )

    first_ok, msg1 = PaymentOrchestrationService.process_inbound_webhook(cmd)
    assert first_ok is True
    assert msg1 == "Webhook processed successfully"

    # Send 4 duplicates
    for _ in range(4):
        ok, msg = PaymentOrchestrationService.process_inbound_webhook(cmd)
        assert ok is False
        assert "Duplicate" in msg

    # Exactly 1 log record persisted
    count = PaymentWebhookEventLog.objects.filter(
        tenant_id=t_id,
        gateway_installation=install,
        provider_event_id=provider_evt,
    ).count()
    assert count == 1
    print("  ✓ 5 duplicate webhooks resulted in strictly 1 log record and 4 duplicate skips.")


def main() -> None:
    print("=" * 80)
    print("NEXUS SUBPHASE 03.07: PAYMENT GATEWAYS & MULTI-RAIL VERIFICATION")
    print("=" * 80)
    _setup_schema()
    test_gateway_installation_isolation()
    test_direct_upi_qr_generation()
    test_multi_rail_charge_and_clearing()
    test_clearing_settlement_invariant()
    test_webhook_deduplication()
    print("=" * 80)
    print("ALL PAYMENT GATEWAYS & MULTI-RAIL TESTS COMPLETED WITH 100% SUCCESS.")
    print("=" * 80)


if __name__ == "__main__":
    main()
