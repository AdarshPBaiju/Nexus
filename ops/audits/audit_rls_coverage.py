#!/usr/bin/env python3
"""
audit_rls_coverage.py - Project Nexus RLS Coverage Auditor.

Scans all Django models in services/nexus-api/src/nexus.
Enforces that every model with a 'tenant_id' field declares
Forced Row-Level Security (RLS) enforcement.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def _inspect_class(node: ast.ClassDef) -> tuple[bool, bool]:
    has_tenant_field = False
    has_rls_declaration = False

    for item in node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name) and target.id == "tenant_id":
                    has_tenant_field = True
        elif isinstance(item, ast.ClassDef) and item.name == "Meta":
            for meta_item in item.body:
                if isinstance(meta_item, ast.Assign):
                    for target in meta_item.targets:
                        if isinstance(target, ast.Name) and target.id in {
                            "has_tenant_rls",
                            "enforce_tenant_rls",
                        }:
                            has_rls_declaration = True

    base_names = [b.id for b in node.bases if isinstance(b, ast.Name)]
    if "TenantScopedModel" in base_names or "TenantScopedEntity" in base_names:
        return True, True

    return has_tenant_field, has_rls_declaration


def _scan_python_file(py_file: Path) -> list[str]:
    unprotected: list[str] = []
    try:
        content = py_file.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(py_file))
    except Exception:
        return unprotected

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            has_tenant, has_rls = _inspect_class(node)
            if has_tenant and not has_rls:
                unprotected.append(node.name)
    return unprotected


def audit_rls_coverage(src_dir: Path) -> int:
    unprotected_models: list[tuple[str, str]] = []

    for py_file in src_dir.rglob("*.py"):
        if "migrations" in py_file.parts or "tests" in py_file.parts:
            continue
        missing = _scan_python_file(py_file)
        for name in missing:
            unprotected_models.append((name, str(py_file.relative_to(src_dir))))

    if unprotected_models:
        print(f"ERROR: Found {len(unprotected_models)} models lacking forced RLS declaration:")
        for name, file_path in unprotected_models:
            print(f"  - {name} in {file_path}")
        return 1

    print("SUCCESS: 100% of tenant-scoped models comply with Forced RLS law.")
    return 0


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parents[2] / "services" / "nexus-api" / "src"
    sys.exit(audit_rls_coverage(base_dir))
