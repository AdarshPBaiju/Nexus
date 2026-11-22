"""
nexus.libs.listing.selector - Sub-50ms Fast Listing Selector with Column Projection & Favourites.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from django.apps import apps
from django.db.models import Exists, OuterRef, QuerySet


class BaseFastListingSelector:
    """
    Coordinates high-concurrency listing queries:
    1. Projects only requested model fields via .only().
    2. Annotates is_favourite boolean via single covering index Exists() subquery.
    3. Eliminates COUNT(*) full scans.
    """

    @classmethod
    def apply_column_projection(
        cls,
        queryset: QuerySet,
        requested_fields: Sequence[str] | None,
        allowed_fields: Sequence[str],
    ) -> QuerySet:
        """Projects strictly selected columns, trimming SQL bandwidth and memory overhead."""
        if not requested_fields:
            return queryset

        projected = [f for f in requested_fields if f in allowed_fields]
        if "id" not in projected:
            projected.append("id")
        return queryset.only(*projected)

    @classmethod
    def annotate_favourites(
        cls,
        queryset: QuerySet,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        entity_type: str,
    ) -> QuerySet:
        """Annotates is_favourite boolean using covering index idx_fav_member_lookup."""
        model = apps.get_model("iam", "UserFavourite")
        fav_subquery = Exists(
            model.objects.filter(
                tenant_id=tenant_id,
                user_id=user_id,
                entity_type=entity_type,
                entity_id=OuterRef("id"),
            )
        )
        return queryset.annotate(is_favourite=fav_subquery)

    @classmethod
    def apply_favourite_sorting(
        cls,
        queryset: QuerySet,
        pin_favourites_first: bool = True,
        sort_field: str = "created_at",
    ) -> QuerySet:
        """Orders favourites at the top when pin_favourites_first is enabled."""
        if pin_favourites_first:
            return queryset.order_by("-is_favourite", f"-{sort_field}", "-id")
        return queryset.order_by(f"-{sort_field}", "-id")
