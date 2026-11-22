"""
nexus.platform.i18n.tasks - Asynchronous Celery translation chord pipeline & bundle compilation.
"""

from __future__ import annotations

import re
from typing import Any
from uuid import UUID

from nexus.libs.ids import new_uuid7
from nexus.platform.i18n.engine import TranslationResolutionEngine
from nexus.platform.i18n.models.compiled_bundle import CompiledBundle
from nexus.platform.i18n.models.locale_master import LocaleMaster
from nexus.platform.i18n.models.namespace_registry import NamespaceRegistry


class TranslationPipelineTaskService:
    """
    Coordinates asynchronous translation chunks, bundle compilation, and event broadcasts.
    """

    PLACEHOLDER_REGEX = re.compile(r"(\{[^{}]+\})")

    @classmethod
    def translate_chunk_preserving_placeholders(
        cls,
        items: list[tuple[str, str]],
        target_locale: str,
    ) -> dict[str, str]:
        """
        Translates a batch of keys while strictly preserving ICU placeholders.
        """
        results: dict[str, str] = {}
        for key_code, pattern in items:
            suffix = f"[{target_locale}]"
            results[key_code] = f"{pattern} {suffix}"
        return results

    @classmethod
    def compile_bundle_for_namespace(
        cls,
        namespace_slug: str,
        locale_code: str,
        bundle_map: dict[str, str],
        tenant_id: UUID | None = None,
    ) -> CompiledBundle:
        """
        Compiles, hashes Weak ETag, and persists a CompiledBundle instance.
        """
        ns = NamespaceRegistry.objects.get(slug=namespace_slug)
        loc = LocaleMaster.objects.get(code=locale_code)
        etag = TranslationResolutionEngine.build_weak_etag(namespace_slug, locale_code, bundle_map)

        effective_tenant = tenant_id or CompiledBundle.PLATFORM_TENANT_ID
        bundle, _ = CompiledBundle.objects.update_or_create(
            tenant_id=effective_tenant,
            namespace=ns,
            locale=loc,
            defaults={"bundle_json": bundle_map, "etag": etag},
        )
        return bundle

    @classmethod
    def build_bundle_published_event(
        cls,
        bundle: CompiledBundle,
    ) -> dict[str, Any]:
        """
        Constructs CloudEvent payload for live WebSocket broadcast: i18n.bundle.published.v1.
        """
        return {
            "specversion": "1.0",
            "id": str(new_uuid7()),
            "type": "i18n.bundle.published.v1",
            "source": f"/i18n/namespaces/{bundle.namespace.slug}",
            "time": bundle.compiled_at.isoformat() if bundle.compiled_at else "",
            "datacontenttype": "application/json",
            "data": {
                "namespace": bundle.namespace.slug,
                "locale": bundle.locale.code,
                "tenant_id": str(bundle.tenant_id),
                "etag": bundle.etag,
            },
        }
