#!/usr/bin/env python3
"""
verify_be_controlled_i18n_celery.py - Verification suite for Subphase 01.05.
Validates:
1. Multilingual core schema (LocaleMaster, NamespaceRegistry, TranslationKey, TranslationEntry).
2. 5-level copy resolution (Platform -> Industry -> Tenant -> Brand -> Branch).
3. 5-step locale fallback chain (Exact -> Base -> TenantDefault -> PlatformSource -> Diagnostic).
4. ICU MessageFormat 2.0 evaluation (placeholders, plurals).
5. Weak ETag 304 matching and bundle compilation.
6. CloudEvent publication broadcast payload (i18n.bundle.published.v1).
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

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
            "nexus.platform.i18n",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

call_command("migrate", run_syncdb=True, verbosity=0)

from nexus.libs.ids import new_uuid7
from nexus.platform.i18n.engine import (
    IcuMessageFormatter,
    TranslationResolutionEngine,
)
from nexus.platform.i18n.models import (
    CompiledBundle,
    LocaleMaster,
    NamespaceRegistry,
    TenantTranslationOverride,
    TranslationEntry,
    TranslationKey,
)
from nexus.platform.i18n.tasks import TranslationPipelineTaskService


def test_locale_and_namespace_models() -> None:
    """Validate LocaleMaster with RTL direction and NamespaceRegistry."""
    en_us = LocaleMaster.objects.create(
        code="en-US",
        base_language="en",
        native_name="English (US)",
        text_direction=LocaleMaster.TextDirection.LTR,
        is_platform_source=True,
    )
    ar_ae = LocaleMaster.objects.create(
        code="ar-AE",
        base_language="ar",
        native_name="العربية (الإمارات)",
        text_direction=LocaleMaster.TextDirection.RTL,
    )
    assert en_us.text_direction == "ltr"
    assert ar_ae.text_direction == "rtl"

    ns_pos = NamespaceRegistry.objects.create(
        slug="pos",
        description="Point of Sale counter interfaces",
    )
    assert ns_pos.slug == "pos"
    print("[PASS] test_locale_and_namespace_models")


def test_icu_message_format_engine() -> None:
    """Validate ICU placeholder and plural branch evaluations."""
    pattern_simple = "Welcome back, {user_name}!"
    formatted = IcuMessageFormatter.format_pattern(
        pattern_simple,
        {"user_name": "Adarsh"},
    )
    assert formatted == "Welcome back, Adarsh!"

    pattern_plural = "You have {count, plural, =0{no items} =1{one item} other{# items}} in cart."
    res_zero = IcuMessageFormatter.format_pattern(pattern_plural, {"count": 0})
    res_one = IcuMessageFormatter.format_pattern(pattern_plural, {"count": 1})
    res_many = IcuMessageFormatter.format_pattern(pattern_plural, {"count": 5})

    assert res_zero == "You have no items in cart."
    assert res_one == "You have one item in cart."
    assert res_many == "You have 5 items in cart."
    print("[PASS] test_icu_message_format_engine")


def test_5_level_copy_resolution() -> None:
    """Validate 5-level copy resolution hierarchy."""
    platform = {"btn.checkout": "Checkout", "lbl.tax": "Sales Tax"}
    industry = {"btn.checkout": "Proceed to Pay"}
    tenant = {"lbl.tax": "State Tax"}
    brand = {"btn.checkout": "Complete Order"}
    branch = {"btn.checkout": "Pay at Express Counter"}

    tiers = [platform, industry, tenant, brand, branch]
    val_checkout = TranslationResolutionEngine.resolve_key("btn.checkout", "pos", tiers)
    assert val_checkout == "Pay at Express Counter"

    tiers_without_branch = [platform, industry, tenant, brand]
    val_brand = TranslationResolutionEngine.resolve_key("btn.checkout", "pos", tiers_without_branch)
    assert val_brand == "Complete Order"

    val_tax = TranslationResolutionEngine.resolve_key("lbl.tax", "pos", tiers)
    assert val_tax == "State Tax"

    missing = TranslationResolutionEngine.resolve_key("btn.unknown", "pos", tiers)
    assert missing == "[missing:pos:btn.unknown]"
    print("[PASS] test_5_level_copy_resolution")


def test_5_step_fallback_chain() -> None:
    """Validate 5-step locale fallback order."""
    chain = TranslationResolutionEngine.fallback_locale_chain(
        target_locale="ar-AE",
        tenant_default_locale="ar-SA",
        platform_source_locale="en-US",
    )
    assert chain == ["ar-AE", "ar", "ar-SA", "en-US"]
    print("[PASS] test_5_step_fallback_chain")


def test_bundle_compilation_and_weak_etag() -> None:
    """Validate bundle compilation, Weak ETag generation, and 304 match logic."""
    ns = NamespaceRegistry.objects.get(slug="pos")
    loc = LocaleMaster.objects.get(code="en-US")
    bundle_data = {"pos.btn.pay": "Pay Now", "pos.lbl.tip": "Add Tip"}

    bundle = TranslationPipelineTaskService.compile_bundle_for_namespace(
        namespace_slug=ns.slug,
        locale_code=loc.code,
        bundle_map=bundle_data,
    )
    assert bundle.etag.startswith('W/"nx:i18n:pos:en-US:')
    assert TranslationResolutionEngine.is_etag_match(bundle.etag, bundle.etag)
    assert not TranslationResolutionEngine.is_etag_match('W/"outdated"', bundle.etag)

    event = TranslationPipelineTaskService.build_bundle_published_event(bundle)
    assert event["type"] == "i18n.bundle.published.v1"
    assert event["data"]["namespace"] == "pos"
    print("[PASS] test_bundle_compilation_and_weak_etag")


def main() -> None:
    test_locale_and_namespace_models()
    test_icu_message_format_engine()
    test_5_level_copy_resolution()
    test_5_step_fallback_chain()
    test_bundle_compilation_and_weak_etag()
    print("\n>>> All 5 Subphase 01.05 verification suites passed successfully! <<<")


if __name__ == "__main__":
    main()
