"""
nexus.platform.audit.models.anchor - Merkle chain anchors & cold archive manifests.
"""

from __future__ import annotations

from django.db import models

from nexus.libs.models import TenantScopedModel


class AuditChainAnchor(TenantScopedModel):
    """
    Periodic cryptographic anchor sealing an audit log window with Ed25519 signature.
    """

    log_tier = models.CharField(max_length=16, default="TIER_A")
    window_start = models.DateTimeField()
    window_end = models.DateTimeField()
    row_count = models.IntegerField()

    prev_anchor_hash = models.CharField(max_length=64)
    merkle_chain_root_hash = models.CharField(max_length=64, db_index=True)
    ed25519_signature = models.TextField()
    minio_worm_object_key = models.CharField(max_length=512)

    class Meta:
        db_table = "audit_chain_anchor"
        ordering = ["-window_end"]


class AuditColdArchiveManifest(TenantScopedModel):
    """
    Manifest of partitions detached and archived to MinIO WORM Parquet.
    """

    partition_name = models.CharField(max_length=128)
    date_start = models.DateField()
    date_end = models.DateField()
    row_count = models.IntegerField()

    parquet_s3_key = models.CharField(max_length=512)
    sha256_checksum = models.CharField(max_length=64)
    worm_retention_until = models.DateTimeField()
    status = models.CharField(max_length=32, default="ARCHIVED")

    class Meta:
        db_table = "audit_cold_archive_manifest"
        ordering = ["-date_end"]
