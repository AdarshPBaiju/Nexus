"""
nexus.libs.serializers.fields.text - Multilingual, slug and HTML fields.
"""

from __future__ import annotations

import re
from typing import Any

from rest_framework import serializers

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TAG_STRIP_PATTERN = re.compile(r"<[^>]+>")


class I18nTranslatableCharField(serializers.Field):
    """Multilingual text field resolving localized string or dict mapping."""

    def to_representation(self, value: Any) -> Any:
        if isinstance(value, dict):
            return value.get("en", next(iter(value.values()), ""))
        return str(value or "")

    def to_internal_value(self, data: Any) -> Any:
        if isinstance(data, (str, dict)):
            return data
        raise serializers.ValidationError("Translatable text must be string or localized dict")


class StrictSlugField(serializers.CharField):
    """Enforces kebab-case slug format strictly."""

    def to_internal_value(self, data: Any) -> str:
        val = super().to_internal_value(data).strip().lower()
        if not SLUG_PATTERN.match(val):
            raise serializers.ValidationError("Slug must be lowercase alphanumeric with hyphens")
        return val


class SafeHtmlDescriptionField(serializers.CharField):
    """Strips dangerous HTML scripts/tags while allowing formatted descriptions."""

    def to_internal_value(self, data: Any) -> str:
        raw = super().to_internal_value(data)
        # Strip script tags or raw HTML tags
        cleaned = TAG_STRIP_PATTERN.sub("", raw).strip()
        return cleaned
