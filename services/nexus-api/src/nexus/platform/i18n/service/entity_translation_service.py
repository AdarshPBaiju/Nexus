"""
nexus.platform.i18n.service.entity_translation_service - Dynamic Entity Translation & Memory Engine.
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Any

from nexus.platform.i18n.models.entity_translation import EntityTranslation
from nexus.platform.i18n.models.glossary import GlossaryTerm
from nexus.platform.i18n.models.translation_memory import TranslationMemory


class EntityTranslationService:
    """
    Translates model entity fields with Translation Memory reuse and Glossary protection.
    """

    @classmethod
    def translate_string(
        cls,
        tenant_id: uuid.UUID,
        text: str,
        target_locale: str,
    ) -> str:
        """Translates text applying Translation Memory cache and Glossary term lockouts."""
        if not text:
            return ""

        text_hash = hashlib.sha256(text.strip().encode("utf-8")).hexdigest()
        cached = TranslationMemory.objects.filter(
            tenant_id=tenant_id,
            source_hash=text_hash,
            locale_code=target_locale,
        ).first()
        if cached:
            return cached.translated_text

        # Apply glossary protections
        protected_text, replacements = cls._protect_glossary_terms(tenant_id, text, target_locale)
        raw_translated = cls._perform_translation(protected_text, target_locale)
        final_translation = cls._restore_glossary_terms(raw_translated, replacements)

        TranslationMemory.objects.create(
            tenant_id=tenant_id,
            source_hash=text_hash,
            source_text=text,
            locale_code=target_locale,
            translated_text=final_translation,
            is_verified=False,
        )
        return final_translation

    @classmethod
    def _protect_glossary_terms(
        cls,
        tenant_id: uuid.UUID,
        text: str,
        locale: str,
    ) -> tuple[str, dict[str, str]]:
        terms = GlossaryTerm.objects.filter(
            tenant_id=tenant_id,
            locale_code__in=[locale, "*"],
        )
        replacements: dict[str, str] = {}
        result = text
        for idx, g_term in enumerate(terms):
            placeholder = f"[[GLOSS_{idx}]]"
            if g_term.term in result:
                result = result.replace(g_term.term, placeholder)
                replacements[placeholder] = g_term.required_translation
        return result, replacements

    @classmethod
    def _restore_glossary_terms(cls, text: str, replacements: dict[str, str]) -> str:
        result = text
        for placeholder, required_val in replacements.items():
            result = result.replace(placeholder, required_val)
        return result

    @classmethod
    def _perform_translation(cls, text: str, locale: str) -> str:
        return f"{text} [{locale}]"

    @classmethod
    def sync_entity(
        cls,
        entity: Any,
        target_locales: list[str],
    ) -> None:
        """Translates all declared translatable fields and updates localized_cache."""
        fields = getattr(entity, "TRANSLATABLE_FIELDS", ("name",))
        for field_name in fields:
            source_val = getattr(entity, field_name, "")
            if not source_val:
                continue
            for loc in target_locales:
                translated = cls.translate_string(entity.tenant_id, source_val, loc)
                entity.set_localized(field_name, loc, translated)
                EntityTranslation.objects.update_or_create(
                    tenant_id=entity.tenant_id,
                    entity_type=entity.__class__.__name__,
                    entity_id=entity.id,
                    field_name=field_name,
                    locale_code=loc,
                    defaults={"translated_value": translated},
                )
        entity.save(update_fields=["localized_cache", "updated_at"])
