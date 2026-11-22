"""
nexus.platform.i18n.engine - 5-Level Resolution, 5-Step Fallback & ICU MessageFormat Engine.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class IcuMessageFormatter:
    """
    Evaluates ICU MessageFormat patterns with parameter interpolation and pluralization.
    """

    BRANCH_REGEX = re.compile(
        r"(?:=(?P<exact>\d+)|(?P<cat>other))\s*\{(?P<text>[^}]*)\}",
    )

    @classmethod
    def format_pattern(cls, pattern: str, params: dict[str, Any] | None = None) -> str:
        """Interpolate parameters and evaluate plural branches in pattern."""
        if not params:
            return pattern

        text = cls._evaluate_plurals(pattern, params)
        for k, v in params.items():
            text = text.replace(f"{{{k}}}", str(v))
        return text

    @classmethod
    def _select_branch(cls, branches_str: str, val_str: str) -> str:
        """Select matching plural branch from branch specification string."""
        other_text = ""
        for b in cls.BRANCH_REGEX.finditer(branches_str):
            exact = b.group("exact")
            cat = b.group("cat")
            text = b.group("text")
            if exact is not None and exact == val_str:
                return text
            if cat == "other":
                other_text = text
        return other_text

    @classmethod
    def _find_matching_brace(cls, text: str, start: int) -> int:
        """Find matching closing brace taking nested braces into account."""
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return i
        return -1

    @classmethod
    def _evaluate_plurals(cls, pattern: str, params: dict[str, Any]) -> str:
        """Evaluate {count, plural, =0{none} =1{one} other{many}} blocks."""
        tag = ", plural,"
        while tag in pattern:
            idx = pattern.find(tag)
            open_pos = pattern.rfind("{", 0, idx)
            if open_pos == -1:
                break
            var_name = pattern[open_pos + 1 : idx].strip()
            close_pos = cls._find_matching_brace(pattern, open_pos)
            if close_pos == -1:
                break

            branches = pattern[idx + len(tag) : close_pos].strip()
            val_str = str(params.get(var_name, 0))
            chosen = cls._select_branch(branches, val_str)
            replacement = chosen.replace("#", val_str)
            pattern = pattern[:open_pos] + replacement + pattern[close_pos + 1 :]
        return pattern


class TranslationResolutionEngine:
    """
    Evaluates 5-level copy resolution and 5-step locale fallback chain.
    """

    DIAGNOSTIC_PREFIX = "[missing:"

    @classmethod
    def build_weak_etag(cls, namespace: str, locale: str, bundle: dict[str, str]) -> str:
        """Construct deterministic Weak ETag W/\"nx:i18n:{ns}:{locale}:{sha256_prefix}\"."""
        canonical = json.dumps(bundle, sort_keys=True)
        h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
        return f'W/"nx:i18n:{namespace}:{locale}:{h}"'

    @classmethod
    def is_etag_match(cls, if_none_match: str | None, current_etag: str) -> bool:
        """Assert whether client If-None-Match matches current weak ETag."""
        if not if_none_match:
            return False
        cleaned_client = if_none_match.strip()
        cleaned_current = current_etag.strip()
        return (
            cleaned_client == cleaned_current
            or cleaned_client == f'W/"{cleaned_current.strip('W/"')}"'
        )

    @classmethod
    def resolve_key(
        cls,
        key_code: str,
        namespace: str,
        lookups_by_priority: list[dict[str, str]],
    ) -> str:
        """
        Evaluate 5-level resolution:
        Platform -> IndustryPreset -> TenantOverride -> BrandOverride -> BranchOverride.
        Highest index in list takes precedence.
        """
        for tier in reversed(lookups_by_priority):
            if key_code in tier:
                return tier[key_code]
        return f"{cls.DIAGNOSTIC_PREFIX}{namespace}:{key_code}]"

    @classmethod
    def fallback_locale_chain(
        cls,
        target_locale: str,
        tenant_default_locale: str = "en-US",
        platform_source_locale: str = "en-US",
    ) -> list[str]:
        """
        5-step locale fallback chain:
        1. Exact Locale (e.g. ar-AE)
        2. Base Language (e.g. ar)
        3. Tenant Default Locale (e.g. ar-SA)
        4. Platform Source Locale (en-US)
        """
        chain: list[str] = [target_locale]
        if "-" in target_locale:
            base = target_locale.split("-")[0]
            if base not in chain:
                chain.append(base)
        if tenant_default_locale not in chain:
            chain.append(tenant_default_locale)
        if platform_source_locale not in chain:
            chain.append(platform_source_locale)
        return chain
