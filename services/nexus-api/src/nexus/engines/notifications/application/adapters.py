"""
nexus.engines.notifications.application.adapters - Pluggable Provider Adapters.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class BaseChannelProviderAdapter(ABC):
    """Abstract interface implemented by all notification vendor adapters."""

    @property
    @abstractmethod
    def provider_code(self) -> str:
        """Unique provider identifier (e.g. FCM_HTTPV1, RESEND, META_WHATSAPP)."""
        pass

    @property
    @abstractmethod
    def channel(self) -> str:
        """Channel supported by this adapter (PUSH, WHATSAPP, SMS, EMAIL)."""
        pass

    @abstractmethod
    def send(
        self,
        destination: str,
        template_code: str,
        context: dict[str, Any],
    ) -> tuple[bool, str, int]:
        """
        Transmits payload to downstream vendor.
        Returns: (success: bool, error_code: str, cost_cents: int)
        """
        pass


@dataclass(frozen=True)
class MockAdapterOptions:
    """Configuration options for mock channel adapter."""

    should_succeed: bool = True
    error_code: str = ""
    cost_cents: int = 10


class MockChannelAdapter(BaseChannelProviderAdapter):
    """Testable mock adapter allowing deterministic simulation of provider outcomes."""

    def __init__(
        self,
        provider_code: str,
        channel: str,
        options: MockAdapterOptions | None = None,
    ) -> None:
        opts = options or MockAdapterOptions()
        self._provider_code = provider_code
        self._channel = channel
        self.should_succeed = opts.should_succeed
        self.error_code = opts.error_code
        self.cost_cents = opts.cost_cents
        self.call_count = 0

    @property
    def provider_code(self) -> str:
        return self._provider_code

    @property
    def channel(self) -> str:
        return self._channel

    def send(
        self,
        destination: str,
        template_code: str,
        context: dict[str, Any],
    ) -> tuple[bool, str, int]:
        self.call_count += 1
        if self.should_succeed:
            return True, "", self.cost_cents
        return False, self.error_code or "PROVIDER_TRANSIENT_ERROR", 0


class AdapterRegistry:
    """Registry managing active channel adapters."""

    _adapters: dict[str, BaseChannelProviderAdapter] = {}

    @classmethod
    def register(cls, adapter: BaseChannelProviderAdapter) -> None:
        cls._adapters[adapter.channel.upper()] = adapter

    @classmethod
    def get(cls, channel: str) -> BaseChannelProviderAdapter | None:
        return cls._adapters.get(channel.upper())

    @classmethod
    def clear(cls) -> None:
        cls._adapters.clear()
