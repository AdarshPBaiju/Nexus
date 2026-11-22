#!/usr/bin/env python3
"""
verify_translatable_entities_localized_inputs.py - Verification suite for Subphase 01.17.
Validates:
1. TranslatableFieldsMixin with zero-join get_localized() resolution and fallback cascade.
2. GlossaryTerm protection enforcing verbatim or required terms during translation.
3. TranslationMemory reuse preventing redundant translation execution.
4. EntityTranslationService syncing entity localized_cache and recording entries.
5. Presence of NexusLocalizedTextInput component (#19).
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
from django.db import models

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

from nexus.libs.models.tenant_scoped import TenantScopedModel
from nexus.libs.models.translatable import TranslatableFieldsMixin
from nexus.platform.i18n.models import (
    EntityTranslation,
    GlossaryTerm,
    TranslationMemory,
)
from nexus.platform.i18n.service.entity_translation_service import EntityTranslationService


class SampleCatalogItem(TenantScopedModel, TranslatableFieldsMixin):
    TRANSLATABLE_FIELDS = ("name", "description")

    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, default="")

    class Meta:
        app_label = "i18n"
        db_table = "test_catalog_item"


with django.db.connection.schema_editor() as editor:
    editor.create_model(SampleCatalogItem)


def test_translatable_fields_mixin_fallback() -> None:
    tenant_id = uuid.uuid4()
    item = SampleCatalogItem(
        tenant_id=tenant_id,
        source_locale="en-US",
        name="Artisan Latte",
        description="Double shot with steamed milk",
    )
    item.set_localized("name", "en-US", "Artisan Latte")
    item.set_localized("name", "ar-AE", "لاتيه حرفي")
    item.save()

    # 1. Exact match
    assert item.get_localized("name", "ar-AE") == "لاتيه حرفي"

    # 2. Fallback to source_locale
    assert item.get_localized("name", "fr-FR") == "Artisan Latte"

    # 3. Description has no localized cache, should fallback to model attribute
    assert item.get_localized("description", "es-ES") == "Double shot with steamed milk"
    print("[PASS] test_translatable_fields_mixin_fallback")


def test_glossary_term_protection() -> None:
    tenant_id = uuid.uuid4()
    GlossaryTerm.objects.create(
        tenant_id=tenant_id,
        term="Nexus Cold Brew",
        locale_code="ar-AE",
        required_translation="نيكسوس كولد برو",
    )

    source_text = "Try our signature Nexus Cold Brew today!"
    translated = EntityTranslationService.translate_string(tenant_id, source_text, "ar-AE")
    assert "نيكسوس كولد برو" in translated, "Glossary term must be protected in translation"
    print("[PASS] test_glossary_term_protection")


def test_translation_memory_caching() -> None:
    tenant_id = uuid.uuid4()
    text = "Freshly baked croissant"

    # First translation
    res1 = EntityTranslationService.translate_string(tenant_id, text, "hi-IN")

    # Verify TranslationMemory row created
    tm_entry = TranslationMemory.objects.filter(tenant_id=tenant_id, locale_code="hi-IN").first()
    assert tm_entry is not None
    assert tm_entry.translated_text == res1

    # Second translation should hit memory cache directly
    res2 = EntityTranslationService.translate_string(tenant_id, text, "hi-IN")
    assert res1 == res2
    print("[PASS] test_translation_memory_caching")


def test_sync_entity_cache() -> None:
    tenant_id = uuid.uuid4()
    item = SampleCatalogItem.objects.create(
        tenant_id=tenant_id,
        source_locale="en-US",
        name="Iced Mocha",
        description="Espresso with chocolate and ice",
    )

    EntityTranslationService.sync_entity(item, ["ar-AE", "hi-IN"])
    item.refresh_from_db()

    # Check localized_cache has been populated
    assert "name" in item.localized_cache
    assert "ar-AE" in item.localized_cache["name"]
    assert "hi-IN" in item.localized_cache["name"]

    # Check EntityTranslation entries exist
    entries = EntityTranslation.objects.filter(
        tenant_id=tenant_id,
        entity_id=item.id,
        field_name="name",
    )
    assert entries.count() == 2
    print("[PASS] test_sync_entity_cache")


def test_frontend_localized_input_component() -> None:
    input_file = (
        REPO_ROOT
        / "packages"
        / "ui"
        / "src"
        / "inputs"
        / "localized"
        / "NexusLocalizedTextInput.tsx"
    )
    assert input_file.exists(), "NexusLocalizedTextInput.tsx must exist"
    index_file = REPO_ROOT / "packages" / "ui" / "src" / "inputs" / "localized" / "index.ts"
    assert index_file.exists(), "localized/index.ts must exist"
    print("[PASS] test_frontend_localized_input_component")


if __name__ == "__main__":
    test_translatable_fields_mixin_fallback()
    test_glossary_term_protection()
    test_translation_memory_caching()
    test_sync_entity_cache()
    test_frontend_localized_input_component()
    print("ALL TRANSLATABLE ENTITIES & LOCALIZED INPUTS VERIFICATIONS PASSED")
