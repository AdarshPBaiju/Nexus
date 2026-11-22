"""
nexus.engines.notifications.application.orchestrator - Omnichannel Notification Orchestrator.
"""

from __future__ import annotations

import datetime
import uuid

from nexus.engines.notifications.application.adapters import AdapterRegistry
from nexus.engines.notifications.application.dtos import (
    DeliveryResultDTO,
    NotificationIntentDTO,
    QuietHoursWindow,
)
from nexus.engines.notifications.application.quiet_hours import QuietHoursEvaluator
from nexus.engines.notifications.models import (
    NotificationDeliveryAttempt,
    NotificationRoutingRule,
    NotificationSuppression,
    NotificationUserPreference,
)


class NotificationOrchestrator:
    """
    Central omnichannel notification orchestrator enforcing multi-channel waterfalls,
    strict idempotency, quiet hours, and suppression lists.
    """

    DEFAULT_WATERFALL = ["PUSH", "WHATSAPP", "SMS", "EMAIL"]

    @classmethod
    def dispatch(cls, intent: NotificationIntentDTO) -> DeliveryResultDTO:
        """Dispatches notification intent through multi-channel fallback waterfall."""
        if cls._is_already_delivered(intent.tenant_id, intent.idempotency_key):
            return DeliveryResultDTO(success=True, is_duplicate=True)

        if cls._should_suppress_quiet_hours(intent):
            return DeliveryResultDTO(success=True, delayed_quiet_hours=True)

        channels = cls._resolve_waterfall(intent.tenant_id, intent.event_type)
        for idx, channel in enumerate(channels):
            result = cls._attempt_channel_send(intent, channel, idx)
            if result and result.success:
                return result

        return DeliveryResultDTO(
            success=False,
            error_message="All channels in waterfall exhausted or failed.",
        )

    @classmethod
    def _is_already_delivered(cls, tenant_id: uuid.UUID, idempotency_key: str) -> bool:
        return NotificationDeliveryAttempt.objects.filter(
            tenant_id=tenant_id,
            idempotency_key__startswith=idempotency_key,
            status__in=[
                NotificationDeliveryAttempt.Status.SENT,
                NotificationDeliveryAttempt.Status.DELIVERED,
                NotificationDeliveryAttempt.Status.READ,
            ],
        ).exists()

    @classmethod
    def _should_suppress_quiet_hours(cls, intent: NotificationIntentDTO) -> bool:
        if intent.priority == NotificationRoutingRule.Priority.CRITICAL_AUTH:
            return False
        if not intent.recipient_id:
            return False

        pref = NotificationUserPreference.objects.filter(
            tenant_id=intent.tenant_id,
            user_id=intent.recipient_id,
            quiet_hours_enabled=True,
        ).first()
        if not pref or not pref.quiet_hours_start or not pref.quiet_hours_end:
            return False

        start_min = pref.quiet_hours_start.hour * 60 + pref.quiet_hours_start.minute
        end_min = pref.quiet_hours_end.hour * 60 + pref.quiet_hours_end.minute
        now = datetime.datetime.now(datetime.timezone.utc)
        curr_min = now.hour * 60 + now.minute
        window = QuietHoursWindow(enabled=True, start_minute=start_min, end_minute=end_min)
        return QuietHoursEvaluator.is_in_quiet_hours(window, curr_min)

    @classmethod
    def _resolve_waterfall(cls, tenant_id: uuid.UUID, event_type: str) -> list[str]:
        rule = NotificationRoutingRule.objects.filter(
            tenant_id=tenant_id,
            event_type=event_type,
            is_active=True,
        ).first()
        if rule and rule.fallback_channels:
            return [c.upper() for c in rule.fallback_channels]
        return cls.DEFAULT_WATERFALL

    @classmethod
    def _attempt_channel_send(
        cls,
        intent: NotificationIntentDTO,
        channel: str,
        attempt_index: int,
    ) -> DeliveryResultDTO | None:
        dest = intent.destinations.get(channel)
        if not dest:
            return None

        if cls._is_destination_suppressed(intent.tenant_id, channel, dest):
            return None

        adapter = AdapterRegistry.get(channel)
        if not adapter:
            return None

        idem_key = f"{intent.idempotency_key}:{channel}:{attempt_index}"
        attempt = NotificationDeliveryAttempt.objects.create(
            tenant_id=intent.tenant_id,
            intent_id=intent.intent_id,
            recipient_destination=dest,
            channel=channel,
            provider_code=adapter.provider_code,
            status=NotificationDeliveryAttempt.Status.SENDING,
            idempotency_key=idem_key,
        )

        success, err_code, cost = adapter.send(dest, intent.template_code, intent.template_context)
        if success:
            attempt.status = NotificationDeliveryAttempt.Status.SENT
            attempt.cost_cents = cost
            attempt.save(update_fields=["status", "cost_cents", "updated_at"])
            return DeliveryResultDTO(
                success=True,
                channel_used=channel,
                provider_code=adapter.provider_code,
                attempt_id=attempt.id,
            )

        attempt.status = NotificationDeliveryAttempt.Status.FAILED
        attempt.error_code = err_code
        attempt.save(update_fields=["status", "error_code", "updated_at"])
        return None

    @classmethod
    def _is_destination_suppressed(
        cls,
        tenant_id: uuid.UUID,
        channel: str,
        destination: str,
    ) -> bool:
        return NotificationSuppression.objects.filter(
            tenant_id=tenant_id,
            channel=channel,
            destination=destination,
            is_active=True,
        ).exists()
