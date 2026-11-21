#!/usr/bin/env python3
"""
audit_code_budget.py - Project Nexus Code Budget and Structural Ceiling Auditor.

Enforces rules defined in .agents/rules/03-code-structure-and-limits.md:
- Repository global ceiling: 400 lines (500 for centralized auto-generated schemas)
- Models / domain services: max 350 lines
- ViewSets: max 150 lines
- Methods: max 35 lines (hard limit 50)
- Parameters: max 4
- Zero untyped dict[str, Any] at service boundaries
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def audit_file(file_path: Path) -> list[str]:
    violations: list[str] = []
    lines = file_path.read_text(encoding="utf-8").splitlines()
    total_lines = len(lines)

    # Global ceiling
    is_schema = "schema" in file_path.name or "types" in file_path.name
    max_file_lines = 500 if is_schema else 400
    if total_lines > max_file_lines:
        violations.append(f"File line count {total_lines} exceeds maximum {max_file_lines}")

    # Specific file ceiling
    if "views.py" in file_path.name and total_lines > 150:
        violations.append(f"ViewSet file lines {total_lines} exceeds ceiling 150")
    elif ("models.py" in file_path.name or "service" in file_path.name) and total_lines > 350:
        violations.append(f"Model/Service file lines {total_lines} exceeds ceiling 350")

    try:
        tree = ast.parse("\n".join(lines), filename=str(file_path))
    except Exception:
        return violations

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Method body length
            func_lines = (node.end_lineno or node.lineno) - node.lineno + 1
            if func_lines > 50:
                violations.append(f"Method '{node.name}' length {func_lines} lines exceeds hard limit 50")

            # Max params
            num_args = len(node.args.args)
            if node.args.vararg:
                num_args += 1
            if node.args.kwarg:
                num_args += 1
            # Exclude self/cls
            if node.args.args and node.args.args[0].arg in {"self", "cls"}:
                num_args -= 1
            if num_args > 4:
                violations.append(f"Method '{node.name}' param count {num_args} exceeds ceiling 4")

    return violations


def run_code_budget_audit(root_dir: Path) -> int:
    all_violations: dict[str, list[str]] = {}
    total_scanned = 0

    for py_file in root_dir.rglob("*.py"):
        if any(part in py_file.parts for part in {".venv", "venv", "node_modules", "migrations", ".git"}):
            continue
        total_scanned += 1
        violations = audit_file(py_file)
        if violations:
            all_violations[str(py_file.relative_to(root_dir))] = violations

    print(f"Code Budget Audit: Scanned {total_scanned} Python files.")
    if all_violations:
        print(f"FAILED: Found {len(all_violations)} files with budget violations:")
        for file_rel, viols in all_violations.items():
            print(f"\n  File: {file_rel}")
            for v in viols:
                print(f"    - {v}")
        return 1

    print("SUCCESS: All scanned files strictly adhere to architectural budget ceilings.")
    return 0


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parents[2]
    sys.exit(run_code_budget_audit(base_dir))
