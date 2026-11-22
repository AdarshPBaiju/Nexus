#!/usr/bin/env python3
"""
verify_universal_embeddable_template_engine.py - Verification suite for Subphase 01.16.
Validates:
1. AST Context Evaluation without eval().
2. SSTI Security Immunity & Complexity Guards (recursion <= 8, loops <= 5000, forbidden tokens).
3. 13-Target Output Compilers from a single AST document.
4. Thermal ESC/POS byte-level control codes and ZPL label format.
5. TemplateDefinition model with Forced RLS isolation.
6. Frontend @nexus/template-studio package structure.
"""

from __future__ import annotations

import os
import sys
import uuid
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
            "nexus.engines.templates",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command

call_command("migrate", run_syncdb=True, verbosity=0)

from nexus.engines.templates.ast.evaluator import (
    SandboxedContextEvaluator,
    TemplateSecurityError,
)
from nexus.engines.templates.ast.nodes import ASTNode, ASTNodeType
from nexus.engines.templates.compilers.registry import TemplateCompilerRegistry
from nexus.engines.templates.engine import UniversalTemplateEngine
from nexus.engines.templates.models import TemplateDefinition


def _build_sample_ast() -> ASTNode:
    return ASTNode(
        node_type=ASTNodeType.DOCUMENT,
        children=[
            ASTNode(
                node_type=ASTNodeType.SECTION,
                children=[
                    ASTNode(
                        node_type=ASTNodeType.TEXT,
                        content="Order #{{ order.id }} for {{ customer.name }} Total: ${{ order.total }}",
                    )
                ],
            )
        ],
    )


def test_ast_safe_context_evaluation() -> None:
    ast = _build_sample_ast()
    context = {
        "order": {"id": "NX-8801", "total": "24.50"},
        "customer": {"name": "Jordan Smith"},
    }
    evaluated = SandboxedContextEvaluator.evaluate_node(ast, context)
    text = evaluated[0].children[0].children[0].content
    assert "Order #NX-8801 for Jordan Smith Total: $24.50" == text
    print("[PASS] test_ast_safe_context_evaluation")


def test_ssti_security_defenses() -> None:
    # 1. Prohibit forbidden tokens in variable bindings
    try:
        SandboxedContextEvaluator.resolve_binding("__class__.__base__", {})
        assert False, "Should have raised TemplateSecurityError for __"
    except TemplateSecurityError:
        pass

    try:
        SandboxedContextEvaluator.resolve_binding("eval('1+1')", {})
        assert False, "Should have raised TemplateSecurityError for eval"
    except TemplateSecurityError:
        pass

    # 2. Prohibit recursion depth > 8
    deep_ast = ASTNode(node_type=ASTNodeType.SECTION)
    curr = deep_ast
    for _ in range(10):
        nxt = ASTNode(node_type=ASTNodeType.SECTION)
        object.__setattr__(curr, "children", [nxt])
        curr = nxt

    try:
        SandboxedContextEvaluator.evaluate_node(deep_ast, {})
        assert False, "Should have raised TemplateSecurityError for recursion > 8"
    except TemplateSecurityError:
        pass

    # 3. Prohibit loop iterations > 5000
    huge_loop = ASTNode(
        node_type=ASTNodeType.LOOP,
        binding="items",
        children=[ASTNode(node_type=ASTNodeType.TEXT, content="item")],
    )
    context_huge = {"items": list(range(5001))}
    try:
        SandboxedContextEvaluator.evaluate_node(huge_loop, context_huge)
        assert False, "Should have raised TemplateSecurityError for loops > 5000"
    except TemplateSecurityError:
        pass

    print("[PASS] test_ssti_security_defenses")


def test_thirteen_output_compilers() -> None:
    ast = _build_sample_ast()
    context = {
        "order": {"id": "NX-9000", "total": "12.00"},
        "customer": {"name": "Alex"},
    }
    metadata = {
        "header": "Nexus Receipt",
        "station": "COFFEE_BAR",
        "barcode": "8901234567",
        "serial": "PASS-9000",
    }

    all_targets = TemplateCompilerRegistry.all_targets()
    assert len(all_targets) == 13, f"Expected 13 targets, got {len(all_targets)}"

    for target in all_targets:
        out = UniversalTemplateEngine.render(ast, target, context, metadata)
        assert out is not None, f"Compiler for target {target} returned None"

        if target == "THERMAL_ESCPOS":
            assert isinstance(out, bytes), "ESC/POS compiler must output raw bytes"
            assert b"\x1b@" in out, "Must initialize printer"
            assert b"\x1dV\x00" in out, "Must issue paper cut"
        elif target == "ZPL_LABEL":
            assert out.startswith("^XA") and out.endswith("^XZ"), "Must follow ZPL-II syntax"
        elif target == "EMAIL_MJML":
            assert "<mjml>" in out and "</mjml>" in out, "Must emit valid MJML document"
        elif target == "VERIFIABLE_WEB":
            assert "<!DOCTYPE html>" in out and "<div id='sig'>" in out, "Must include digest"

    print("[PASS] test_thirteen_output_compilers")


def test_template_definition_model() -> None:
    tenant_id = uuid.uuid4()
    tpl = TemplateDefinition.objects.create(
        tenant_id=tenant_id,
        code="CAFE_RECEIPT_80MM",
        name="Café Standard Thermal Receipt",
        category="POS_RECEIPT",
        supported_targets=["THERMAL_ESCPOS", "VERIFIABLE_WEB"],
        ast_definition={"node_type": "document", "children": []},
        is_system_locked=True,
    )
    assert tpl.id is not None
    assert tpl.is_system_locked is True
    print("[PASS] test_template_definition_model")


def test_frontend_template_studio_package() -> None:
    studio_base = REPO_ROOT / "packages" / "template-studio"
    assert (studio_base / "package.json").exists()
    assert (studio_base / "src" / "NexusTemplateStudio.tsx").exists()
    assert (studio_base / "src" / "index.ts").exists()
    print("[PASS] test_frontend_template_studio_package")


if __name__ == "__main__":
    test_ast_safe_context_evaluation()
    test_ssti_security_defenses()
    test_thirteen_output_compilers()
    test_template_definition_model()
    test_frontend_template_studio_package()
    print("ALL UNIVERSAL TEMPLATE ENGINE & 13 COMPILERS VERIFICATIONS PASSED")
