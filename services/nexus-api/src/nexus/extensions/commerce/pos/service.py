"""
nexus.extensions.commerce.pos.service - Atomic counter checkout and double-entry sales posting.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from nexus.engines.accounting.models.account import LedgerAccount
from nexus.engines.accounting.models.journal_entry import JournalEntry
from nexus.engines.accounting.service import JournalLineDto, LedgerPostingService
from nexus.engines.taxation.service import TaxCalculationEngine
from nexus.extensions.base.fin_basic.service import ShiftSessionService
from nexus.extensions.commerce.pos.models.pos_order import (
    CreatePosOrderDto,
    PosOrder,
)
from nexus.extensions.commerce.pos.models.pos_order_line import (
    CreatePosLineDto,
    PosOrderLine,
)
from nexus.extensions.commerce.pos.models.pos_tender import (
    CreatePosTenderDto,
    PosPaymentTender,
)
from nexus.libs.money.money import Money


@dataclass(frozen=True)
class TenderPaymentSpec:
    """Specification of an incoming payment tender."""

    tender_type: str
    tendered_amount: Decimal
    applied_amount: Decimal
    change_returned: Decimal = Decimal("0.0000")
    reference_code: str = ""


@dataclass(frozen=True)
class CounterCheckoutRequestDto:
    """Parameter object for processing a complete counter POS transaction."""

    tenant_id: uuid.UUID
    branch_id: uuid.UUID
    workstation_id: str
    cashier_user_id: uuid.UUID
    legal_entity_id: uuid.UUID
    lines: list[CreatePosLineDto]
    tenders: list[TenderPaymentSpec]
    currency: str = "USD"
    discount_amount: Decimal = Decimal("0.0000")
    tax_rate: Decimal = Decimal("10.0000")
    shift_session_id: uuid.UUID | None = None
    order_number: str = field(default_factory=lambda: f"ORD-{uuid.uuid4().hex[:8].upper()}")


class PosCheckoutService:
    """
    Coordinates atomic counter checkout: order lines, multi-tender split payment,
    tax calculation, shift register increment, and balancing GL journal posting.
    """

    @classmethod
    @transaction.atomic
    def process_counter_checkout(cls, dto: CounterCheckoutRequestDto) -> PosOrder:
        """Processes atomic counter checkout with zero-drift GL integration."""
        cls._validate_checkout_request(dto)
        subtotal = sum((line.line_total for line in dto.lines), Decimal("0.0000"))
        net_taxable = max(Decimal("0.0000"), subtotal - dto.discount_amount)
        tax_res = TaxCalculationEngine.calculate_tax(
            Money.of(net_taxable, dto.currency), dto.tax_rate, is_inclusive=False
        )
        total_payable = subtotal - dto.discount_amount + tax_res.tax_money.amount

        cls._assert_tenders_match_payable(dto.tenders, total_payable)
        order = cls._persist_order_and_lines(dto, subtotal, tax_res.tax_money.amount, total_payable)
        cls._persist_tenders(dto.tenant_id, order.id, dto.tenders)
        cls._update_shift_session_if_present(dto.shift_session_id, dto.tenders)

        journal_id = cls._post_sales_journal(dto, order, subtotal, tax_res.tax_money.amount)
        order.mark_paid(journal_id)
        return order

    @classmethod
    def _validate_checkout_request(cls, dto: CounterCheckoutRequestDto) -> None:
        if not dto.lines:
            raise ValidationError("EmptyOrderError: Cannot checkout order with zero line items.")
        if not dto.tenders:
            raise ValidationError(
                "EmptyTendersError: Cannot checkout order with zero payment tenders."
            )

    @classmethod
    def _assert_tenders_match_payable(
        cls, tenders: list[TenderPaymentSpec], payable: Decimal
    ) -> None:
        total_applied = sum((t.applied_amount for t in tenders), Decimal("0.0000"))
        if total_applied != payable:
            raise ValidationError(
                f"TenderMismatchError: Applied tenders ({total_applied}) must exactly match payable ({payable})."
            )

    @classmethod
    def _persist_order_and_lines(
        cls, dto: CounterCheckoutRequestDto, subtotal: Decimal, tax: Decimal, total: Decimal
    ) -> PosOrder:
        order = PosOrder.create_order(
            CreatePosOrderDto(
                tenant_id=dto.tenant_id,
                order_number=dto.order_number,
                branch_id=dto.branch_id,
                workstation_id=dto.workstation_id,
                cashier_user_id=dto.cashier_user_id,
                subtotal_amount=subtotal,
                discount_amount=dto.discount_amount,
                tax_amount=tax,
                total_amount=total,
                currency=dto.currency,
                shift_session_id=dto.shift_session_id,
            )
        )
        for line in dto.lines:
            PosOrderLine.create_line(
                CreatePosLineDto(
                    tenant_id=dto.tenant_id,
                    order_id=order.id,
                    item_name=line.item_name,
                    sku_code=line.sku_code,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                    line_total=line.line_total,
                    modifiers_json=line.modifiers_json,
                )
            )
        return order

    @classmethod
    def _persist_tenders(
        cls, tenant_id: uuid.UUID, order_id: uuid.UUID, tenders: list[TenderPaymentSpec]
    ) -> None:
        for t in tenders:
            PosPaymentTender.create_tender(
                CreatePosTenderDto(
                    tenant_id=tenant_id,
                    order_id=order_id,
                    tender_type=t.tender_type,
                    tendered_amount=t.tendered_amount,
                    applied_amount=t.applied_amount,
                    change_returned=t.change_returned,
                    reference_code=t.reference_code,
                )
            )

    @classmethod
    def _update_shift_session_if_present(
        cls, session_id: uuid.UUID | None, tenders: list[TenderPaymentSpec]
    ) -> None:
        if session_id is None:
            return
        cash_total = sum(
            (
                t.applied_amount
                for t in tenders
                if t.tender_type == PosPaymentTender.TenderType.CASH
            ),
            Decimal("0.0000"),
        )
        if cash_total > Decimal("0.0000"):
            ShiftSessionService.record_cash_sale(session_id, cash_total)

    @classmethod
    def _post_sales_journal(
        cls,
        dto: CounterCheckoutRequestDto,
        order: PosOrder,
        subtotal: Decimal,
        tax: Decimal,
    ) -> uuid.UUID:
        entry = JournalEntry.objects.create(
            tenant_id=dto.tenant_id,
            legal_entity_id=dto.legal_entity_id,
            entry_number=f"JRN-POS-{uuid.uuid4().hex[:12].upper()}",
            entry_type=JournalEntry.EntryType.SALES,
            status=JournalEntry.EntryStatus.DRAFT,
        )
        lines = cls._build_journal_lines(dto, subtotal, tax)
        LedgerPostingService.post_journal_entry(entry, lines)
        return entry.id

    @classmethod
    def _build_journal_lines(
        cls, dto: CounterCheckoutRequestDto, subtotal: Decimal, tax: Decimal
    ) -> list[JournalLineDto]:
        lines: list[JournalLineDto] = []
        for t in dto.tenders:
            code = "1010" if t.tender_type == PosPaymentTender.TenderType.CASH else "1020"
            acc = LedgerAccount.objects.get(tenant_id=dto.tenant_id, account_code=code)
            lines.append(
                JournalLineDto(
                    acc.id,
                    t.applied_amount,
                    Decimal("0"),
                    dto.currency,
                    Decimal("1"),
                    t.applied_amount,
                    Decimal("0"),
                )
            )
        rev_acc = cls._get_or_create_account(
            dto.tenant_id,
            "4010",
            "Food & Beverage Sales",
            LedgerAccount.AccountType.REVENUE,
        )
        net_rev = subtotal - dto.discount_amount
        lines.append(
            JournalLineDto(
                rev_acc.id, Decimal("0"), net_rev, dto.currency, Decimal("1"), Decimal("0"), net_rev
            )
        )
        if tax > Decimal("0.0000"):
            tax_acc = cls._get_or_create_account(
                dto.tenant_id,
                "2020",
                "Sales Tax Payable",
                LedgerAccount.AccountType.LIABILITY,
            )
            lines.append(
                JournalLineDto(
                    tax_acc.id, Decimal("0"), tax, dto.currency, Decimal("1"), Decimal("0"), tax
                )
            )
        return lines

    @classmethod
    def _get_or_create_account(
        cls, tenant_id: uuid.UUID, code: str, name: str, account_type: str
    ) -> LedgerAccount:
        acc, _ = LedgerAccount.objects.get_or_create(
            tenant_id=tenant_id,
            account_code=code,
            defaults={
                "account_name": name,
                "account_type": account_type,
                "currency": "USD",
                "is_active": True,
            },
        )
        return acc
