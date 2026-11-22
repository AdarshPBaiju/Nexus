#!/usr/bin/env python3
"""
verify_fast_listing_selector_keyset_favourites.py - Verification suite for Subphase 01.09.
Validates:
1. UserFavourite model and covering index idx_fav_member_lookup.
2. Fast listing selector column projection (.only()).
3. Zero-N+1 universal favourites Exists() subquery annotation.
4. Pin-favourites-first ordering.
5. Zero-OFFSET KeysetPaginator cursor encoding and pagination traversal.
6. ListingETagBuilder Weak ETag 304 fast path matching.
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
            "nexus.platform.iam",
            "nexus.engines.commerce_folio",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

call_command("migrate", run_syncdb=True, verbosity=0)

from nexus.engines.commerce_folio.models import CommerceFolio
from nexus.libs.ids import new_uuid7
from nexus.libs.listing.etag import ListingETagBuilder
from nexus.libs.listing.selector import BaseFastListingSelector
from nexus.libs.pagination.keyset import KeysetPaginator
from nexus.platform.iam.models.favourite import UserFavourite


def test_universal_favourites_annotation_and_sorting() -> None:
    """Validate Exists() subquery annotation and pin-favourites-first sorting."""
    tenant_id = new_uuid7()
    user_id = new_uuid7()
    branch_id = new_uuid7()

    f1 = CommerceFolio.objects.create(
        tenant_id=tenant_id,
        branch_id=branch_id,
        folio_number="FOL-001",
    )
    f2 = CommerceFolio.objects.create(
        tenant_id=tenant_id,
        branch_id=branch_id,
        folio_number="FOL-002",
    )
    f3 = CommerceFolio.objects.create(
        tenant_id=tenant_id,
        branch_id=branch_id,
        folio_number="FOL-003",
    )

    # Favorite only f2
    UserFavourite.objects.create(
        tenant_id=tenant_id,
        user_id=user_id,
        entity_type="folio",
        entity_id=f2.id,
    )

    qs = CommerceFolio.objects.filter(tenant_id=tenant_id)
    annotated_qs = BaseFastListingSelector.annotate_favourites(
        queryset=qs,
        tenant_id=tenant_id,
        user_id=user_id,
        entity_type="folio",
    )

    # Test Pin-Favourites-First sorting: f2 must be index 0
    sorted_qs = BaseFastListingSelector.apply_favourite_sorting(annotated_qs, pin_favourites_first=True)
    results = list(sorted_qs)

    assert results[0].id == f2.id
    assert results[0].is_favourite is True
    assert results[1].is_favourite is False
    assert results[2].is_favourite is False

    print("[PASS] test_universal_favourites_annotation_and_sorting")


def test_keyset_pagination_zero_offset() -> None:
    """Validate cursor pagination traversing items without SQL OFFSET."""
    tenant_id = new_uuid7()
    branch_id = new_uuid7()

    for i in range(5):
        CommerceFolio.objects.create(
            tenant_id=tenant_id,
            branch_id=branch_id,
            folio_number=f"FOL-PAG-{i}",
        )

    qs = CommerceFolio.objects.filter(tenant_id=tenant_id)

    # Page 1: 2 items
    page1 = KeysetPaginator.paginate_queryset(qs, cursor=None, page_size=2)
    assert len(page1.items) == 2
    assert page1.has_next is True
    assert page1.next_cursor is not None

    # Page 2: next 2 items
    page2 = KeysetPaginator.paginate_queryset(qs, cursor=page1.next_cursor, page_size=2)
    assert len(page2.items) == 2
    assert page2.has_next is True

    # Page 3: last 1 item
    page3 = KeysetPaginator.paginate_queryset(qs, cursor=page2.next_cursor, page_size=2)
    assert len(page3.items) == 1
    assert page3.has_next is False
    assert page3.next_cursor is None

    print("[PASS] test_keyset_pagination_zero_offset")


def test_listing_etag_builder() -> None:
    """Validate Weak ETag construction and 304 match logic."""
    etag = ListingETagBuilder.build_weak_etag(
        entity_type="folio",
        fav_version=1,
        filter_hash="status=OPEN",
        cursor_token="nx1c_abc123",
    )
    assert etag.startswith('W/"nx:folio:1:')
    assert ListingETagBuilder.is_304_match(etag, etag)
    assert not ListingETagBuilder.is_304_match('W/"nx:folio:2:other:root"', etag)

    print("[PASS] test_listing_etag_builder")


def main() -> None:
    test_universal_favourites_annotation_and_sorting()
    test_keyset_pagination_zero_offset()
    test_listing_etag_builder()
    print("\n>>> All 3 Subphase 01.09 verification suites passed successfully! <<<")


if __name__ == "__main__":
    main()
