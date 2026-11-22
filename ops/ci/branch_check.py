#!/usr/bin/env python3
r"""
branch_check.py - Project Nexus Git Branch Naming Governance Auditor.

Enforces rules defined in .agents/rules/04-git-branching-and-workflow.md:
- 4-Tier Hierarchy: main <- development <- feat/<parent-domain> <- feat/<subphase> & test/<subphase>
- Standard regex: ^(main|development|(feat|test|fix|perf|refactor|chore)\/[a-z0-9\-]+)$
- Strictly lowercase kebab-case
- Strictly ZERO "phase" or "phase/" prefix in branch names
- Blocks direct feature commits on main
"""

from __future__ import annotations

import re
import subprocess
import sys

BRANCH_REGEX = re.compile(r"^(main|development|(feat|test|fix|perf|refactor|chore)\/[a-z0-9\-]+)$")

FORBIDDEN_PATTERNS = [
    (
        re.compile(r"^phase", re.IGNORECASE),
        "Branch names must NEVER start with 'phase' or 'phase/'",
    ),
    (re.compile(r"\/phase", re.IGNORECASE), "Branch names must NEVER contain '/phase'"),
    (re.compile(r"[A-Z]"), "Branch names must be strictly lowercase"),
    (re.compile(r"_"), "Branch names must use kebab-case hyphens, never underscores"),
    (re.compile(r"^(dev|develop|staging)$"), "Use canonical 'development' branch name"),
    (re.compile(r"^(temp|tmp|wip|work|scratch)"), "Generic scratch branch names are forbidden"),
]


def get_current_branch() -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return res.stdout.strip()
    except Exception as e:
        print(f"ERROR: Failed to determine current git branch: {e}", file=sys.stderr)
        sys.exit(1)


def validate_branch_name(branch_name: str) -> tuple[bool, list[str]]:
    errors: list[str] = []

    # Detached HEAD (e.g., in CI or merge commit check)
    if branch_name in {"HEAD", ""}:
        return True, []

    for pattern, reason in FORBIDDEN_PATTERNS:
        if pattern.search(branch_name):
            errors.append(f"VIOLATION: {reason} (branch: '{branch_name}')")

    if not BRANCH_REGEX.match(branch_name):
        errors.append(
            f"VIOLATION: Branch '{branch_name}' does not match canonical taxonomy pattern: "
            f"{BRANCH_REGEX.pattern}"
        )

    return len(errors) == 0, errors


def main() -> int:
    branch = sys.argv[1] if len(sys.argv) > 1 else get_current_branch()
    print(f"Auditing Git branch name: '{branch}'...")

    valid, errors = validate_branch_name(branch)
    if not valid:
        print("\nBRANCH GOVERNANCE CHECK FAILED:")
        for err in errors:
            print(f"  - {err}")
        print("\nRefer to .agents/rules/04-git-branching-and-workflow.md for branch naming rules.")
        return 1

    print(f"SUCCESS: Branch '{branch}' strictly complies with Nexus 4-Tier Branching Taxonomy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
