"""
nexus.platform.i18n.models - Re-export of all multilingual data models.
"""
from nexus.platform.i18n.models.compiled_bundle import CompiledBundle
from nexus.platform.i18n.models.entity_translation import EntityTranslation
from nexus.platform.i18n.models.glossary import GlossaryTerm
from nexus.platform.i18n.models.locale_master import LocaleMaster
from nexus.platform.i18n.models.namespace_registry import NamespaceRegistry
from nexus.platform.i18n.models.tenant_override import TenantTranslationOverride
from nexus.platform.i18n.models.translation_entry import TranslationEntry
from nexus.platform.i18n.models.translation_key import TranslationKey
from nexus.platform.i18n.models.translation_memory import TranslationMemory

__all__ = [
    "CompiledBundle",
    "EntityTranslation",
    "GlossaryTerm",
    "LocaleMaster",
    "NamespaceRegistry",
    "TenantTranslationOverride",
    "TranslationEntry",
    "TranslationKey",
    "TranslationMemory",
]
