#!/usr/bin/env python3
"""
verify_messaging_channel_plugins_and_providers.py - Verification suite for Subphase 01.15.
Validates:
1. SegmentCostEstimator GSM-7 vs UCS-2 detection and segment calculations.
2. Msg91DltSmsAdapter India TRAI DLT header and variable length rules (<= 30 chars).
3. MetaWhatsAppAdapter named-to-positional template variable mapper.
4. FirebaseFcmAdapter stale device token auto-pruning.
5. InAppNotificationAdapter in-app ledger recording.
6. TenantChannelCredential KMS envelope encryption.
7. Frontend NexusNotificationCenter component existence and structure.
"""
from __future__ import annotations

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

from nexus.engines.notifications.models import (
    DevicePushToken,
    InAppNotification,
    TenantChannelCredential,
)
from nexus.extensions.channels.email.resend_adapter import ResendEmailAdapter
from nexus.extensions.channels.push.fcm_adapter import FirebaseFcmAdapter
from nexus.extensions.channels.push.in_app_adapter import InAppNotificationAdapter
from nexus.extensions.channels.sms.msg91_dlt_adapter import Msg91DltSmsAdapter
from nexus.extensions.channels.sms.segment_estimator import SegmentCostEstimator
from nexus.extensions.channels.whatsapp.meta_adapter import MetaWhatsAppAdapter
from nexus.libs.security.cipher import CipherContext, TenantEnvelopeCipher


def test_segment_cost_estimator() -> None:
    # 1. Pure GSM-7 text
    gsm_text = "Your order #1234 has been confirmed and is being prepared."
    est_gsm = SegmentCostEstimator.estimate(gsm_text)
    assert est_gsm.encoding == "GSM_7"
    assert est_gsm.segment_count == 1
    assert est_gsm.has_non_gsm is False

    # 2. Text with non-GSM curly quote or emoji (UCS-2 inflation)
    ucs_text = "Your order\u2019s ready! \u2615"
    est_ucs = SegmentCostEstimator.estimate(ucs_text)
    assert est_ucs.encoding == "UCS_2"
    assert est_ucs.has_non_gsm is True
    assert "\u2019" in est_ucs.non_gsm_chars or "\u2615" in est_ucs.non_gsm_chars
    print("[PASS] test_segment_cost_estimator")


def test_msg91_dlt_compliance() -> None:
    adapter = Msg91DltSmsAdapter(auth_key="test_key", default_pe_id="110123456789")

    # 1. Missing template_id should fail
    ok, err, _ = adapter.send("+919876543210", "tpl_1", {})
    assert ok is False
    assert err == "MISSING_DLT_HEADERS"

    # 2. Exceeded variable length (> 30 chars) should fail
    context_long = {
        "template_id": "1201999999",
        "variables": {"customer_name": "ThisNameIsExcessivelyLongAndExceedsThirtyCharactersLimit"},
    }
    ok_long, err_long, _ = adapter.send("+919876543210", "tpl_1", context_long)
    assert ok_long is False
    assert "DLT_VARIABLE_LENGTH_EXCEEDED" in err_long

    # 3. Compliant dispatch
    context_valid = {
        "template_id": "1201999999",
        "variables": {"customer_name": "Rahul Verma", "order_id": "#8821"},
    }
    ok_valid, _, cost = adapter.send("+919876543210", "tpl_1", context_valid)
    assert ok_valid is True
    assert cost > 0
    print("[PASS] test_msg91_dlt_compliance")


def test_meta_whatsapp_variable_mapping() -> None:
    adapter = MetaWhatsAppAdapter(phone_number_id="1002345", access_token="secret")
    ctx = {"var1": "Alice", "var2": "Desk 4", "var3": "$45.00"}
    params = adapter.map_template_variables(ctx)
    assert params == ["Alice", "Desk 4", "$45.00"]

    ok, _, cost = adapter.send("+15551234567", "tpl_table_ready", ctx)
    assert ok is True
    assert cost == 15
    print("[PASS] test_meta_whatsapp_variable_mapping")


def test_fcm_token_auto_pruning() -> None:
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    stale_token = "stale_fcm_device_token_xyz_123"

    token_obj = DevicePushToken.objects.create(
        tenant_id=tenant_id,
        user_id=user_id,
        token=stale_token,
        platform=DevicePushToken.Platform.FCM,
        is_active=True,
    )

    adapter = FirebaseFcmAdapter(project_id="nexus-prod")
    ok, err, _ = adapter.send(
        stale_token,
        "tpl_push",
        {"tenant_id": tenant_id, "simulated_fcm_status": "UNREGISTERED"},
    )
    assert ok is False
    assert err == "FCM_TOKEN_UNREGISTERED"

    token_obj.refresh_from_db()
    assert token_obj.is_active is False, "Stale FCM token must be automatically deactivated"
    print("[PASS] test_fcm_token_auto_pruning")


def test_in_app_notification_adapter() -> None:
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    adapter = InAppNotificationAdapter()

    ok, _, _ = adapter.send(
        str(user_id),
        "tpl_in_app",
        {
            "tenant_id": tenant_id,
            "title": "Shift Reconciled",
            "body": "Cash drawer balance verified.",
            "category": "SYSTEM",
            "action_url": "/owner/shifts/123",
        },
    )
    assert ok is True

    record = InAppNotification.objects.filter(tenant_id=tenant_id, recipient_id=user_id).first()
    assert record is not None
    assert record.title == "Shift Reconciled"
    assert record.is_read is False
    print("[PASS] test_in_app_notification_adapter")


def test_kms_envelope_credential_storage() -> None:
    tenant_id = uuid.uuid4()
    cred_id = uuid.uuid4()
    cipher = TenantEnvelopeCipher()
    secret_config = '{"api_key": "resend_live_sec_9999", "webhook_secret": "whsec_abc"}'

    ctx = CipherContext(
        tenant_id=tenant_id,
        entity_label="notif_channel_credential",
        row_id=cred_id,
        field_name="encrypted_config",
    )
    encrypted_payload = cipher.encrypt(ctx, secret_config)
    cred = TenantChannelCredential.objects.create(
        id=cred_id,
        tenant_id=tenant_id,
        channel="EMAIL",
        provider_code="RESEND",
        encrypted_config=encrypted_payload,
    )

    decrypted = cipher.decrypt(ctx, cred.encrypted_config)
    assert decrypted == secret_config
    print("[PASS] test_kms_envelope_credential_storage")


def test_frontend_components() -> None:
    ui_base = REPO_ROOT / "packages" / "ui" / "src" / "notifications"
    assert (ui_base / "NexusNotificationCenter.tsx").exists()
    assert (ui_base / "index.ts").exists()
    print("[PASS] test_frontend_components")


if __name__ == "__main__":
    test_segment_cost_estimator()
    test_msg91_dlt_compliance()
    test_meta_whatsapp_variable_mapping()
    test_fcm_token_auto_pruning()
    test_in_app_notification_adapter()
    test_kms_envelope_credential_storage()
    test_frontend_components()
    print("ALL MESSAGING CHANNEL PLUGINS & PROVIDERS VERIFICATIONS PASSED")
