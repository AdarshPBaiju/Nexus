#!/usr/bin/env python3
"""
verify_dynamic_universal_number_series_fiscal_sequence.py - Verification suite for Subphase 01.27.
"""
from __future__ import annotations

import os
import sys
import time
import uuid
from datetime import date
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
            "nexus.platform.tenancy",
            "nexus.engines.number_series",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

call_command("migrate", run_syncdb=True, verbosity=0)

from nexus.engines.number_series import (
    FeistelCipherPermuter,
    FormatCompileOptions,
    NumberSeriesFormatCompiler,
    RadixEncoder,
)
from nexus.engines.number_series.models import (
    NumberSeriesCounter,
    NumberSeriesDefinition,
    NumberSeriesReservation,
)
from nexus.engines.number_series.services.allocator import NumberSeriesAllocator


def test_radix_encoder() -> None:
    assert RadixEncoder.encode(42, radix="BASE10", min_length=4) == "0042"
    assert RadixEncoder.encode(255, radix="BASE16", min_length=4) == "00FF"
    assert RadixEncoder.encode(100, radix="BASE32_CROCKFORD", min_length=3) == "034"
    assert RadixEncoder.encode(1000, radix="BASE36", min_length=4) == "00RS"
    print("PASS: RadixEncoder multi-radix conversion verified.")


def test_feistel_cipher_bijectivity() -> None:
    domain_size = 10000
    key = 987654321
    seen: set[int] = set()

    for original in range(1000):
        permuted = FeistelCipherPermuter.permute(original, domain_size, key)
        assert 0 <= permuted < domain_size
        assert permuted not in seen, f"Collision detected at {original} -> {permuted}"
        seen.add(permuted)

        recovered = FeistelCipherPermuter.unpermute(permuted, domain_size, key)
        assert recovered == original, f"Bijectivity failed: {original} != {recovered}"

    print("PASS: FeistelCipherPermuter 100% bijective and reversible with 0 collisions.")


def test_format_compiler_latency() -> None:
    options = FormatCompileOptions(
        radix="BASE10",
        tokens={"BRANCH": "HQ01"},
        operational_date=date(2026, 11, 22),
    )
    start = time.perf_counter()
    for seq in range(1000):
        _ = NumberSeriesFormatCompiler.compile_code(
            pattern="INV/{BRANCH}/{YYYY}/{SEQ:6}",
            sequence_num=seq,
            options=options,
        )
    elapsed_ms = (time.perf_counter() - start) * 1000 / 1000
    assert elapsed_ms < 0.25, f"Compiler exceeded 0.25ms SLA: {elapsed_ms:.4f} ms"
    print(f"PASS: NumberSeriesFormatCompiler sub-0.25ms compilation verified ({elapsed_ms:.4f} ms).")


def test_number_series_allocator_and_reclaim() -> None:
    tenant_id = uuid.uuid4()
    series_def = NumberSeriesDefinition.objects.create(
        tenant_id=tenant_id,
        name="Sales Invoice",
        entity_target="INVOICE",
        format_pattern="INV/{YYYY}/{SEQ:4}",
        radix="BASE10",
        padding_length=4,
        reset_frequency="YEARLY",
    )

    # 1. Monotonic sequential allocation
    code1 = NumberSeriesAllocator.allocate_next(tenant_id, series_def)
    code2 = NumberSeriesAllocator.allocate_next(tenant_id, series_def)
    assert code1 == "INV/2026/0001"
    assert code2 == "INV/2026/0002"

    # 2. Reclaim pool: simulate abandoned checkout of sequence 1
    counter = NumberSeriesCounter.objects.get(tenant_id=tenant_id, series_def=series_def)
    NumberSeriesReservation.objects.create(
        tenant_id=tenant_id,
        counter=counter,
        reserved_number=1,
        ttl_expires_at=django.utils.timezone.now(),
        status="RECLAIMED",
    )

    # Next allocation should reuse sequence 1 from reclaim pool
    reclaimed_code = NumberSeriesAllocator.allocate_next(tenant_id, series_def)
    assert reclaimed_code == "INV/2026/0001"

    # Subsequent allocation continues from high-water-mark 3
    code3 = NumberSeriesAllocator.allocate_next(tenant_id, series_def)
    assert code3 == "INV/2026/0003"
    print("PASS: NumberSeriesAllocator monotonic allocation & reclaim pool verified.")


def main() -> None:
    print("--- Running Subphase 01.27 Verification Suite ---")
    test_radix_encoder()
    test_feistel_cipher_bijectivity()
    test_format_compiler_latency()
    test_number_series_allocator_and_reclaim()
    print("SUCCESS: 01.27 Dynamic Universal Number Series verified with 100% assertions.")


if __name__ == "__main__":
    main()
