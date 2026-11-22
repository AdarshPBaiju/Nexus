"""
nexus.engines.payment_router.application.service - Payment Orchestration Service.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from nexus.engines.payment_router.application.clearing_generator import ClearingJournalGenerator
from nexus.engines.payment_router.application.dtos import (
    ConfirmPaymentCmd,
    CreatePaymentIntentCmd,
    WebhookEventCmd,
)
from nexus.engines.payment_router.gateways.registry import GatewayAdapterRegistry
from nexus.engines.payment_router.models import (
    GatewayInstallation,
    PaymentAttempt,
    PaymentIntent,
)
from nexus.engines.payment_router.models.webhook_event_log import (
    LogWebhookEventDto,
    PaymentWebhookEventLog,
)


class PaymentOrchestrationService:
    """
    Coordinates multi-rail payment execution, ascending lock order, and double-entry clearing.
    """

    @classmethod
    def create_intent(cls, cmd: CreatePaymentIntentCmd) -> PaymentIntent:
        """Creates or retrieves an existing deduplicated payment intent."""
        existing = PaymentIntent.objects.filter(
            tenant_id=cmd.tenant_id,
            idempotency_key=cmd.idempotency_key,
        ).first()
        if existing:
            return existing

        return PaymentIntent.objects.create(
            tenant_id=cmd.tenant_id,
            folio_id=cmd.folio_id,
            customer_id=cmd.customer_id,
            amount=Decimal(str(cmd.amount)),
            currency=cmd.currency.upper(),
            status=PaymentIntent.Status.REQUIRES_PAYMENT_METHOD,
            idempotency_key=cmd.idempotency_key,
        )

    @classmethod
    def confirm_payment(
        cls,
        cmd: ConfirmPaymentCmd,
    ) -> tuple[PaymentIntent, PaymentAttempt, list[Any]]:
        """
        Executes payment capture under canonical ascending row locks.
        Zero duplicate captures under concurrent requests.
        """
        with transaction.atomic():
            # Canonical lock ordering: ORDER BY id ASC
            intent = (
                PaymentIntent.objects.select_for_update()
                .filter(tenant_id=cmd.tenant_id, id=cmd.intent_id)
                .order_by("id")
                .first()
            )
            if not intent:
                raise ValueError("PaymentIntent not found")

            if intent.status == PaymentIntent.Status.SUCCEEDED:
                return cls._handle_existing_success(intent)

            return cls._execute_charge(intent, cmd)

    @classmethod
    def _handle_existing_success(
        cls,
        intent: PaymentIntent,
    ) -> tuple[PaymentIntent, PaymentAttempt, list[Any]]:
        attempt = PaymentAttempt.objects.filter(
            intent=intent,
            status=PaymentAttempt.Status.CAPTURED,
        ).first()
        postings = ClearingJournalGenerator.generate_capture_postings(intent.amount)
        return intent, attempt, postings

    @classmethod
    def _execute_charge(
        cls,
        intent: PaymentIntent,
        cmd: ConfirmPaymentCmd,
    ) -> tuple[PaymentIntent, PaymentAttempt, list[Any]]:
        adapter = GatewayAdapterRegistry.get(cmd.gateway_code)
        if not adapter:
            raise ValueError(f"Gateway {cmd.gateway_code} not configured or unsupported")

        ok, tx_id, fee, raw = adapter.process_charge(intent, cmd.payment_data)
        if not ok:
            attempt = PaymentAttempt.objects.create(
                tenant_id=cmd.tenant_id,
                intent=intent,
                gateway_tx_id=tx_id or "tx_failed",
                status=PaymentAttempt.Status.FAILED,
                raw_response=raw,
            )
            intent.status = PaymentIntent.Status.FAILED
            intent.save(update_fields=["status", "updated_at"])
            return intent, attempt, []

        attempt = PaymentAttempt.objects.create(
            tenant_id=cmd.tenant_id,
            intent=intent,
            gateway_tx_id=tx_id,
            status=PaymentAttempt.Status.CAPTURED,
            amount_captured=intent.amount,
            fee_amount=fee,
            raw_response=raw,
        )

        intent.status = PaymentIntent.Status.SUCCEEDED
        intent.selected_gateway = cmd.gateway_code
        intent.save(update_fields=["status", "selected_gateway", "updated_at"])

        postings = ClearingJournalGenerator.generate_capture_postings(intent.amount)
        return intent, attempt, postings

    @classmethod
    def process_inbound_webhook(cls, cmd: WebhookEventCmd) -> tuple[bool, str]:
        """
        Processes inbound webhook callback with idempotent duplicate protection.
        """
        install = GatewayInstallation.objects.filter(
            tenant_id=cmd.tenant_id,
            gateway_code=cmd.gateway_code,
            is_active=True,
        ).first()
        if not install:
            raise ValueError(f"Gateway {cmd.gateway_code} not active for tenant")

        exists = PaymentWebhookEventLog.objects.filter(
            tenant_id=cmd.tenant_id,
            gateway_installation=install,
            provider_event_id=cmd.provider_event_id,
        ).exists()
        if exists:
            return False, "Duplicate webhook event ignored"

        PaymentWebhookEventLog.record_event(
            LogWebhookEventDto(
                tenant_id=cmd.tenant_id,
                installation_id=install.id,
                provider_event_id=cmd.provider_event_id,
                event_type=cmd.event_type,
                payload=cmd.payload,
            )
        )
        return True, "Webhook processed successfully"
