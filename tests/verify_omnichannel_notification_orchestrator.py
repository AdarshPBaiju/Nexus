#!/usr/bin/env python3
"""
verify_omnichannel_notification_orchestrator.py - Verification suite for Subphase 01.14.
Validates:
1. Multi-channel fallback waterfall (PUSH -> WHATSAPP -> SMS -> EMAIL).
2. Suppression list blocking suppressed destinations and continuing waterfall.
3. Quiet hours logic (overnight wrap, non-critical delay, CRITICAL_AUTH bypass).
4. Idempotency (zero duplicate sends on retry).
5. Inbound DLR webhook ingestion and bounce auto-suppression.
"""
from __future__ import annotations

import datetime
import os
import sys
import uuid
from pathlib import Path

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
            "nexus.engines.notifications",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

call_command("migrate", run_syncdb=True, verbosity=0)

from nexus.engines.notifications.application.adapters import (
    AdapterRegistry,
    MockAdapterOptions,
    MockChannelAdapter,
)
from nexus.engines.notifications.application.dtos import (
    NotificationIntentDTO,
    QuietHoursWindow,
)
from nexus.engines.notifications.application.orchestrator import NotificationOrchestrator
from nexus.engines.notifications.application.quiet_hours import QuietHoursEvaluator
from nexus.engines.notifications.models import (
    NotificationDeliveryAttempt,
    NotificationRoutingRule,
    NotificationSuppression,
    NotificationUserPreference,
)
from nexus.engines.notifications.webhooks.receiver import WebhookDlrEnvelope, WebhookReceiver


def setup_adapters() -> tuple[MockChannelAdapter, MockChannelAdapter]:
    AdapterRegistry.clear()
    push_opts = MockAdapterOptions(should_succeed=False, cost_cents=1)
    wa_opts = MockAdapterOptions(should_succeed=True, cost_cents=15)
    sms_opts = MockAdapterOptions(should_succeed=True, cost_cents=20)
    email_opts = MockAdapterOptions(should_succeed=True, cost_cents=5)

    push_adapter = MockChannelAdapter("FCM_HTTPV1", "PUSH", push_opts)
    wa_adapter = MockChannelAdapter("META_WHATSAPP", "WHATSAPP", wa_opts)
    sms_adapter = MockChannelAdapter("TWILIO_SMS", "SMS", sms_opts)
    email_adapter = MockChannelAdapter("RESEND", "EMAIL", email_opts)

    AdapterRegistry.register(push_adapter)
    AdapterRegistry.register(wa_adapter)
    AdapterRegistry.register(sms_adapter)
    AdapterRegistry.register(email_adapter)
    return push_adapter, wa_adapter


def test_fallback_waterfall() -> None:
    push_ad, wa_ad = setup_adapters()
    tenant_id = uuid.uuid4()
    intent_id = uuid.uuid4()

    NotificationRoutingRule.objects.create(
        tenant_id=tenant_id,
        event_type="ORDER_CONFIRMED",
        priority=NotificationRoutingRule.Priority.OPERATIONAL,
        fallback_channels=["PUSH", "WHATSAPP", "SMS"],
    )

    intent = NotificationIntentDTO(
        tenant_id=tenant_id,
        intent_id=intent_id,
        event_type="ORDER_CONFIRMED",
        priority=NotificationRoutingRule.Priority.OPERATIONAL,
        destinations={
            "PUSH": "token_device_abc",
            "WHATSAPP": "+15550001111",
            "SMS": "+15550001111",
        },
        template_code="tpl_order_confirmed",
    )

    result = NotificationOrchestrator.dispatch(intent)
    assert result.success is True, "Dispatch should succeed via waterfall"
    assert result.channel_used == "WHATSAPP", f"Expected WHATSAPP, got {result.channel_used}"
    assert push_ad.call_count == 1, "PUSH should have been attempted first"
    assert wa_ad.call_count == 1, "WHATSAPP should have succeeded"

    attempts = NotificationDeliveryAttempt.objects.filter(tenant_id=tenant_id, intent_id=intent_id)
    assert attempts.count() == 2, "Expected 2 attempts logged (1 failed PUSH, 1 sent WHATSAPP)"
    print("[PASS] test_fallback_waterfall")


def test_suppression_list_skips() -> None:
    AdapterRegistry.clear()
    sms_opts = MockAdapterOptions(should_succeed=True, cost_cents=20)
    email_opts = MockAdapterOptions(should_succeed=True, cost_cents=5)
    sms_ad = MockChannelAdapter("TWILIO_SMS", "SMS", sms_opts)
    email_ad = MockChannelAdapter("RESEND", "EMAIL", email_opts)
    AdapterRegistry.register(sms_ad)
    AdapterRegistry.register(email_ad)

    tenant_id = uuid.uuid4()
    intent_id = uuid.uuid4()
    suppressed_phone = "+15559990000"

    NotificationSuppression.objects.create(
        tenant_id=tenant_id,
        channel="SMS",
        destination=suppressed_phone,
        reason=NotificationSuppression.Reason.HARD_BOUNCE,
    )

    intent = NotificationIntentDTO(
        tenant_id=tenant_id,
        intent_id=intent_id,
        event_type="PROMO_OFFER",
        priority=NotificationRoutingRule.Priority.MARKETING,
        destinations={
            "SMS": suppressed_phone,
            "EMAIL": "customer@example.com",
        },
        template_code="tpl_promo",
    )

    result = NotificationOrchestrator.dispatch(intent)
    assert result.success is True
    assert result.channel_used == "EMAIL", "Suppressed SMS must be skipped in favor of EMAIL"
    assert sms_ad.call_count == 0, "Suppressed SMS adapter must never be called"
    print("[PASS] test_suppression_list_skips")


def test_quiet_hours() -> None:
    # 22:00 (1320) to 08:00 (480)
    window = QuietHoursWindow(enabled=True, start_minute=1320, end_minute=480)
    assert QuietHoursEvaluator.is_in_quiet_hours(window, 1350) is True  # 22:30
    assert QuietHoursEvaluator.is_in_quiet_hours(window, 200) is True   # 03:20
    assert QuietHoursEvaluator.is_in_quiet_hours(window, 600) is False  # 10:00

    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()

    NotificationUserPreference.objects.create(
        tenant_id=tenant_id,
        user_id=user_id,
        quiet_hours_enabled=True,
        quiet_hours_start=datetime.time(0, 0),
        quiet_hours_end=datetime.time(23, 59),  # all day quiet
    )

    # 1. Marketing message should be delayed
    marketing_intent = NotificationIntentDTO(
        tenant_id=tenant_id,
        intent_id=uuid.uuid4(),
        event_type="MARKETING_UPDATE",
        priority=NotificationRoutingRule.Priority.MARKETING,
        recipient_id=user_id,
        destinations={"EMAIL": "user@example.com"},
        template_code="tpl_mktg",
    )
    res_mktg = NotificationOrchestrator.dispatch(marketing_intent)
    assert res_mktg.delayed_quiet_hours is True

    # 2. Critical auth OTP should bypass quiet hours
    critical_intent = NotificationIntentDTO(
        tenant_id=tenant_id,
        intent_id=uuid.uuid4(),
        event_type="AUTH_OTP",
        priority=NotificationRoutingRule.Priority.CRITICAL_AUTH,
        recipient_id=user_id,
        destinations={"EMAIL": "user@example.com"},
        template_code="tpl_otp",
    )
    res_crit = NotificationOrchestrator.dispatch(critical_intent)
    assert res_crit.delayed_quiet_hours is False
    assert res_crit.success is True
    print("[PASS] test_quiet_hours")


def test_idempotency_zero_duplicate_sends() -> None:
    AdapterRegistry.clear()
    email_opts = MockAdapterOptions(should_succeed=True, cost_cents=5)
    email_ad = MockChannelAdapter("RESEND", "EMAIL", email_opts)
    AdapterRegistry.register(email_ad)

    tenant_id = uuid.uuid4()
    intent_id = uuid.uuid4()
    idem_key = f"idem_test_{intent_id}"

    intent = NotificationIntentDTO(
        tenant_id=tenant_id,
        intent_id=intent_id,
        event_type="RECEIPT_EMAIL",
        priority=NotificationRoutingRule.Priority.OPERATIONAL,
        destinations={"EMAIL": "receipt@example.com"},
        template_code="tpl_receipt",
        idempotency_key=idem_key,
    )

    first = NotificationOrchestrator.dispatch(intent)
    assert first.success is True
    assert first.is_duplicate is False
    assert email_ad.call_count == 1

    second = NotificationOrchestrator.dispatch(intent)
    assert second.success is True
    assert second.is_duplicate is True
    assert email_ad.call_count == 1, "Duplicate send must not invoke adapter again"
    print("[PASS] test_idempotency_zero_duplicate_sends")


def test_dlr_webhook_and_auto_suppression() -> None:
    tenant_id = uuid.uuid4()
    attempt = NotificationDeliveryAttempt.objects.create(
        tenant_id=tenant_id,
        intent_id=uuid.uuid4(),
        recipient_destination="bounced_user@example.com",
        channel="EMAIL",
        provider_code="RESEND",
        status=NotificationDeliveryAttempt.Status.SENT,
        idempotency_key=f"dlr_test_{uuid.uuid4()}",
    )

    payload = {
        "event": "email.bounced",
        "attempt_id": str(attempt.id),
        "status": "BOUNCED",
    }
    envelope = WebhookDlrEnvelope(
        tenant_id=tenant_id,
        provider_code="RESEND",
        payload=payload,
    )
    processed = WebhookReceiver.process_dlr(envelope)
    assert processed is True

    attempt.refresh_from_db()
    assert attempt.status == NotificationDeliveryAttempt.Status.BOUNCED

    suppressed = NotificationSuppression.objects.filter(
        tenant_id=tenant_id,
        channel="EMAIL",
        destination="bounced_user@example.com",
    ).exists()
    assert suppressed is True, "Bounced destination must be auto-added to suppression registry"
    print("[PASS] test_dlr_webhook_and_auto_suppression")


if __name__ == "__main__":
    test_fallback_waterfall()
    test_suppression_list_skips()
    test_quiet_hours()
    test_idempotency_zero_duplicate_sends()
    test_dlr_webhook_and_auto_suppression()
    print("ALL OMNICHANNEL NOTIFICATION ORCHESTRATOR VERIFICATIONS PASSED")
