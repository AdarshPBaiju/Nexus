"""
nexus.engines.discounts.service - Discount Calculation and Stacking Service.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Sequence

from nexus.engines.discounts.domain.allocator import ProportionalDiscountAllocator
from nexus.engines.discounts.domain.condition_ast import ConditionAstEvaluator
from nexus.libs.money.money import Money


@dataclass(frozen=True)
class DiscountEvaluationRequest:
    """Strongly typed parameter DTO for discount evaluation."""

    rule_code: str
    condition_ast: dict
    action_ast: dict
    guardrail_policy: dict = field(default_factory=dict)
    context: dict = field(default_factory=dict)


@dataclass(frozen=True)
class DiscountCalculationResult:
    """Exact discount calculation result with line-level distribution."""

    original_total: Money
    discount_total: Money
    net_total: Money
    applied_rule_codes: tuple[str, ...]
    line_discounts: tuple[Money, ...]


class DiscountEvaluatorService:
    """
    Evaluates discount rules, checks condition ASTs, computes benefits,
    enforces maximum caps, and proportionally allocates line discounts.
    """

    @classmethod
    def evaluate_order_discount(
        cls,
        lines: Sequence[Money],
        req: DiscountEvaluationRequest,
    ) -> DiscountCalculationResult:
        """Evaluates single rule benefit and produces line-level allocations."""
        if not lines:
            zero = Money.zero("USD")
            return DiscountCalculationResult(zero, zero, zero, (), ())

        currency = lines[0].currency
        total_orig = sum((m.amount for m in lines), Decimal("0.00"))
        orig_money = Money.of(total_orig, currency)

        ctx = cls._build_context(req.context, total_orig, len(lines))
        if not ConditionAstEvaluator.evaluate(req.condition_ast, ctx):
            return cls._build_zero_result(orig_money, lines)

        discount_amt = cls._calculate_benefit(orig_money.amount, req.action_ast)
        discount_amt = cls._apply_guardrails(discount_amt, orig_money.amount, req.guardrail_policy)
        return cls._build_success_result(orig_money, discount_amt, lines, req.rule_code)

    @classmethod
    def _build_context(cls, base_ctx: dict, total_orig: Decimal, items_count: int) -> dict:
        ctx = dict(base_ctx)
        ctx["cart_total"] = total_orig
        ctx["items_count"] = items_count
        return ctx

    @classmethod
    def _build_zero_result(
        cls, orig_money: Money, lines: Sequence[Money]
    ) -> DiscountCalculationResult:
        zero_disc = Money.of(Decimal("0.00"), orig_money.currency)
        return DiscountCalculationResult(
            original_total=orig_money,
            discount_total=zero_disc,
            net_total=orig_money,
            applied_rule_codes=(),
            line_discounts=tuple(zero_disc for _ in lines),
        )

    @classmethod
    def _build_success_result(
        cls, orig: Money, discount_amt: Decimal, lines: Sequence[Money], rule_code: str
    ) -> DiscountCalculationResult:
        disc_money = Money.of(discount_amt, orig.currency)
        line_allocs = ProportionalDiscountAllocator.allocate(disc_money, lines)
        net_amt = (orig.amount - disc_money.amount).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_EVEN
        )
        return DiscountCalculationResult(
            original_total=orig,
            discount_total=disc_money,
            net_total=Money.of(net_amt, orig.currency),
            applied_rule_codes=(rule_code,),
            line_discounts=tuple(line_allocs),
        )

    @classmethod
    def _calculate_benefit(cls, total_amount: Decimal, action_ast: dict) -> Decimal:
        atype = str(action_ast.get("type", "")).upper()
        val = Decimal(str(action_ast.get("value", "0")))
        if atype == "PERCENTAGE":
            return (total_amount * (val / Decimal("100.0"))).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_EVEN
            )
        if atype == "FIXED_AMOUNT":
            return min(val, total_amount)
        return Decimal("0.00")

    @classmethod
    def _apply_guardrails(
        cls, discount_amt: Decimal, total_amount: Decimal, guardrails: dict
    ) -> Decimal:
        cap_val = guardrails.get("max_discount_cap")
        if cap_val is not None:
            discount_amt = min(discount_amt, Decimal(str(cap_val)))
        return min(discount_amt, total_amount)
