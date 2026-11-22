"""
nexus.engines.notifications.contracts.types - Contracts & Data Transfer Objects for Channel Providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CompiledChannelMessage:
    """Standardized message payload delivered to channel provider adapter."""

    destination: str
    body: str
    subject: str = ""
    template_code: str = ""
    variables: dict[str, str] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class CanonicalDlrEvent:
    """Normalized delivery receipt event produced by inbound provider webhook parser."""

    provider_code: str
    event_type: str
    attempt_id: str
    status: str
    timestamp: str
    raw_payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SmsSegmentEstimate:
    """Billable segment analysis for SMS copy."""

    segment_count: int
    encoding: str
    char_count: int
    max_per_segment: int
    has_non_gsm: bool
    non_gsm_chars: list[str] = field(default_factory=list)
