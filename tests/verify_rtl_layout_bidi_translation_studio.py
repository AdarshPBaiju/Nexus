#!/usr/bin/env python3
"""
verify_rtl_layout_bidi_translation_studio.py - Verification suite for Subphase 01.18.
Validates:
1. I18nCliRunner subcommands: audit-hardcoded, validate-icu, sync-keys, placeholder-diff.
2. Placeholder safety diff detecting breaking dropped parameters.
3. Logical CSS compliance in frontend components (zero physical directional classes).
4. KeyInspectorDrawer and TranslationStudioView components presence and exports.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "services" / "nexus-api" / "src"
sys.path.insert(0, str(API_SRC))
sys.path.insert(0, str(REPO_ROOT))

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

from ops.cli.i18n_cli import I18nCliRunner
from nexus.platform.i18n.models.namespace_registry import NamespaceRegistry
from nexus.platform.i18n.models.translation_key import TranslationKey


def test_i18n_cli_commands() -> None:
    # 1. audit-hardcoded
    assert I18nCliRunner.audit_hardcoded(["pos.order.create", "common.btn.save"]) == 0
    assert I18nCliRunner.audit_hardcoded(["Click here to continue"]) == 1

    # 2. validate-icu
    ns, _ = NamespaceRegistry.objects.get_or_create(slug="pos", defaults={"description": "POS"})
    TranslationKey.objects.get_or_create(
        namespace=ns,
        key_code="order_items",
        defaults={"default_icu_pattern": "{count, plural, =0{no items} other{# items}}"},
    )
    assert I18nCliRunner.validate_icu() == 0

    # 3. sync-keys
    assert I18nCliRunner.sync_keys() == 0
    print("[PASS] test_i18n_cli_commands")


def test_placeholder_diff() -> None:
    old_pattern = "Order {order_id} total: ${amount}"

    # Safe: preserves both order_id and amount
    safe_pattern = "Your total for order {order_id} is ${amount}"
    assert I18nCliRunner.placeholder_diff(old_pattern, safe_pattern) is True

    # Breaking: drops {amount}
    breaking_pattern = "Order {order_id} processed"
    assert I18nCliRunner.placeholder_diff(old_pattern, breaking_pattern) is False
    print("[PASS] test_placeholder_diff")


def test_logical_css_enforcement() -> None:
    ui_files = [
        REPO_ROOT / "packages" / "ui" / "src" / "i18n" / "KeyInspectorDrawer.tsx",
        REPO_ROOT / "packages" / "ui" / "src" / "i18n" / "TranslationStudioView.tsx",
    ]
    physical_class_regex = re.compile(r"\b(ml-|mr-|pl-|pr-|text-left\b|text-right\b)")

    for file_path in ui_files:
        assert file_path.exists(), f"{file_path} must exist"
        content = file_path.read_text(encoding="utf-8")
        matches = physical_class_regex.findall(content)
        assert len(matches) == 0, (
            f"Found forbidden physical CSS classes {matches} in {file_path.name}"
        )
    print("[PASS] test_logical_css_enforcement")


def test_frontend_components_exports() -> None:
    index_file = REPO_ROOT / "packages" / "ui" / "src" / "i18n" / "index.ts"
    assert index_file.exists()
    content = index_file.read_text(encoding="utf-8")
    assert "KeyInspectorDrawer" in content
    assert "TranslationStudioView" in content
    print("[PASS] test_frontend_components_exports")


if __name__ == "__main__":
    test_i18n_cli_commands()
    test_placeholder_diff()
    test_logical_css_enforcement()
    test_frontend_components_exports()
    print("ALL RTL LAYOUT, TRANSLATION STUDIO & CLI VERIFICATIONS PASSED")
