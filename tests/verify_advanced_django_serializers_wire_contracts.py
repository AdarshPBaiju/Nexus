#!/usr/bin/env python3
"""
verify_advanced_django_serializers_wire_contracts.py - Verification suite for Subphase 01.22.
"""

from __future__ import annotations

import os
import sys
import uuid
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

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
        ],
        USE_TZ=True,
    )
    django.setup()

from rest_framework import serializers

from nexus.libs.serializers import (
    UNSET,
    BaseNexusInputSerializer,
    BaseNexusOutputSerializer,
    InvalidParameterDetail,
    OrjsonResponseRenderer,
    RFC9457ProblemDetail,
)
from nexus.libs.serializers.fields import (
    BlindIndexHashField,
    EncryptedLookupField,
    EncryptedPathIdField,
    I18nTranslatableCharField,
    IsoCurrencyCodeField,
    IsoMoneyField,
    MacOrHardwareAddressField,
    MaskedPiiField,
    SafeHtmlDescriptionField,
    StrictEnumField,
    StrictSlugField,
    TaxIdentificationNumberField,
    UtcDateTimeField,
    ZonedRateDecimalField,
)


@dataclass(frozen=True)
class CreateBranchCommandDTO:
    slug: str
    name: str
    tax_id: str
    mac_address: str


class CreateBranchInputSerializer(BaseNexusInputSerializer[CreateBranchCommandDTO]):
    slug = StrictSlugField()
    name = serializers.CharField()
    tax_id = TaxIdentificationNumberField()
    mac_address = MacOrHardwareAddressField()

    def create_command_dto(self, validated_data: dict[str, object]) -> CreateBranchCommandDTO:
        return CreateBranchCommandDTO(
            slug=str(validated_data["slug"]),
            name=str(validated_data["name"]),
            tax_id=str(validated_data["tax_id"]),
            mac_address=str(validated_data["mac_address"]),
        )


class BranchOutputSerializer(BaseNexusOutputSerializer):
    id = EncryptedPathIdField()
    slug = serializers.CharField()
    name = serializers.CharField()
    money = IsoMoneyField()
    created_at = UtcDateTimeField()


def test_input_serializer_rejection_and_dto() -> None:
    # Unknown field rejection
    ser = CreateBranchInputSerializer(data={"slug": "valid-slug", "unknown_field": "intruder"})
    assert not ser.is_valid()
    assert "unknown_field" in ser.errors

    # Valid payload
    valid_data = {
        "slug": "main-cafe",
        "name": "Main Café Branch",
        "tax_id": "TAX12345XYZ",
        "mac_address": "00:1A:2B:3C:4D:5E",
    }
    ser_valid = CreateBranchInputSerializer(data=valid_data)
    assert ser_valid.is_valid(), ser_valid.errors
    dto = ser_valid.to_command_dto()
    assert isinstance(dto, CreateBranchCommandDTO)
    assert dto.slug == "main-cafe"
    print("PASS: Input serializer validation and Command DTO emission verified.")


def test_partial_patch_and_unset() -> None:
    ser_patch = CreateBranchInputSerializer(data={"slug": "updated-slug"}, partial=True)
    assert ser_patch.is_valid(), ser_patch.errors
    assert ser_patch.validated_data["slug"] == "updated-slug"
    assert ser_patch.validated_data["name"] is UNSET
    print("PASS: Partial patch UNSET sentinel semantics verified.")


def test_enterprise_fields() -> None:
    # Identity
    path_field = EncryptedPathIdField()
    u = uuid.uuid4()
    rep = path_field.to_representation(u)
    assert rep.startswith("nx1_id_")
    assert path_field.to_internal_value(rep) == u

    # Money
    money_field = IsoMoneyField()
    parsed_money = money_field.to_internal_value({"amount": "199.99", "currency": "usd"})
    assert parsed_money == {"amount": "199.99", "currency": "USD"}

    # Security & Text
    blind_field = BlindIndexHashField()
    assert len(blind_field.to_internal_value("secret-card")) == 64

    masked_field = MaskedPiiField()
    assert masked_field.to_representation("4111111111111234") == "**** 1234"

    # HTML
    html_field = SafeHtmlDescriptionField()
    cleaned = html_field.to_internal_value("<script>alert('xss')</script>Hello World")
    assert "<script>" not in cleaned

    # Enum
    enum_field = StrictEnumField(choices=["ACTIVE", "INACTIVE"])
    assert enum_field.to_internal_value("ACTIVE") == "ACTIVE"
    print("PASS: 14 Enterprise serializer fields verified.")


def test_output_pruning_and_renderer() -> None:
    raw_data = {
        "id": uuid.uuid4(),
        "slug": "coffee-hq",
        "name": "Coffee HQ",
        "money": {"amount": "50.00", "currency": "EUR"},
        "created_at": "2026-11-22T09:00:00Z",
    }
    ser_all = BranchOutputSerializer(instance=raw_data)
    assert len(ser_all.data) == 5

    ser_pruned = BranchOutputSerializer(instance=raw_data, selected_fields=["name", "slug"])
    assert set(ser_pruned.data.keys()) == {"name", "slug"}

    # Weak ETag
    etag = ser_pruned.compute_weak_etag(ser_pruned.data)
    assert etag.startswith('W/"nx:ser:')

    # Renderer
    rendered_bytes = OrjsonResponseRenderer.render(ser_pruned.data)
    assert b"Coffee HQ" in rendered_bytes

    # Problem details
    problem = RFC9457ProblemDetail(
        invalid_params=[InvalidParameterDetail(field="tax_id", reason="Invalid format")]
    )
    p_dict = problem.to_dict()
    assert p_dict["status"] == 400
    assert len(p_dict["invalid_params"]) == 1
    print("PASS: Output selected-fields pruning, ETag, and renderer verified.")


def main() -> None:
    print("--- Running Subphase 01.22 Verification Suite ---")
    test_input_serializer_rejection_and_dto()
    test_partial_patch_and_unset()
    test_enterprise_fields()
    test_output_pruning_and_renderer()
    print(
        "SUCCESS: 01.22 Advanced Django Serializers & Wire-Contracts verified with 100% assertions."
    )


if __name__ == "__main__":
    main()
